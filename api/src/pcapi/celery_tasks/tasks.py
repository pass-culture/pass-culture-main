import json
import logging
import typing
from functools import wraps

import pydantic.v1 as pydantic_v1
from celery import shared_task


logger = logging.getLogger(__name__)


def celery_async_task(
    name: str,
    autoretry_for: typing.Tuple[Exception, ...],
    model: type[pydantic_v1.BaseModel] | None,
    retry_backoff: bool = True,
) -> typing.Callable:
    """
    celery_async_task decorator is used to defer the function execution to a Celery worker.

    Parameters :
    name:  controls what route is used for the task and therefore which worker will run it.
    model: if not None, will perform input validation against pydantic model and parse and load it to and from JSON to ensure
    that the input is JSON serializable. Otherwise this step will be skipped.
    """

    def decorator(f: typing.Callable) -> typing.Callable:
        @shared_task(name=name, autoretry_for=autoretry_for, retry_backoff=retry_backoff)
        @wraps(f)
        def task(payload: dict) -> None:
            if model is not None:
                try:
                    # We want to ensure payload is JSON serializable, we do that by encoding and decoding
                    # to and from json. This is needed because Celery uses the __repr__ of the task to pass
                    # it so values like dates and Decimal will be preserved instead of being transformed to their
                    # JSON representation.
                    # This is the same behavior that we had on cloud_tasks
                    parsed_payload = model.parse_obj(payload)
                    parsed_payload = json.loads(parsed_payload.json())
                    parsed_payload = model.parse_obj(parsed_payload)
                except pydantic_v1.ValidationError as exp:
                    logger.error("could not deserialize object", extra={"exception": exp})

            f(parsed_payload)

        return task

    return decorator

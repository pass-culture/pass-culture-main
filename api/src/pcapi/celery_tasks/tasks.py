from functools import wraps
import json
import logging
import typing

from celery import shared_task
from pydantic import ValidationError
import pydantic.v1 as pydantic_v1


logger = logging.getLogger(__name__)


def celery_async_task(
    name: str, autoretry_for: typing.Tuple[Exception, ...], retry_backoff: bool, model: type[pydantic_v1.BaseModel]
) -> typing.Callable:
    def decorator(f: typing.Callable[[pydantic_v1.BaseModel], None]) -> typing.Callable:
        @shared_task(name=name, autoretry_for=autoretry_for, retry_backoff=retry_backoff)
        @wraps(f)
        def task(payload: dict) -> None:
            try:
                # We want to ensure payload is JSON serializable, we do that by encoding and decoding
                # to and from json. This is needed because Celery uses the __repr__ of the task to pass
                # it so values like dates and Decimal will be preserved instead of being transformed to their
                # JSON representation.
                # This is the same behavior that we have on cloud_tasks
                parsed_payload = model.parse_obj(payload)
                parsed_payload = json.loads(parsed_payload.json())
                parsed_payload = model.parse_obj(parsed_payload)
            except ValidationError as exp:
                logger.error("could not deserialize object", extra={"exception": exp})

            f(parsed_payload)

        return task

    return decorator

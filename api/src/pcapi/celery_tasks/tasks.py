import json
import logging
import time
import typing
from functools import wraps

import pydantic.v1 as pydantic_v1
from celery import shared_task

import pcapi.celery_tasks.metrics as metrics


logger = logging.getLogger(__name__)


def celery_async_task(
    name: str,
    model: type[pydantic_v1.BaseModel] | None,
    autoretry_for: typing.Tuple[Exception, ...] = (),
    retry_backoff: bool = True,
) -> typing.Callable:
    """
    celery_async_task decorator is used to defer the function execution to a Celery worker.

    Parameters :
    name:  controls what route is used for the task and therefore which worker will run it.
    autoretry_for:  a tuple of exception that will make the worker retry the task automatically if they are raised.
    retry_backoff: if set, the task will not be retried immediately and will follow an exponential backoff retry scheme.
    model: if not None, will perform input validation against pydantic model and parse and load it to and from JSON to ensure
    that the input is JSON serializable. Otherwise this step will be skipped.
    """

    def decorator(f: typing.Callable) -> typing.Callable:
        @shared_task(name=name, autoretry_for=autoretry_for, retry_backoff=retry_backoff)
        @wraps(f)
        def task(payload: dict) -> None:
            metrics.tasks_counter.labels(task=name).inc()
            metrics.tasks_in_progress.labels(task=name).inc()
            start_time = time.time()
            try:
                if model is not None:
                    # We want to ensure payload is JSON serializable, we do that by encoding and decoding
                    # to and from json. This is needed because Celery uses the __repr__ of the task to pass
                    # it so values like dates and Decimal will be preserved instead of being transformed to their
                    # JSON representation.
                    # This is the same behavior that we had on cloud_tasks
                    parsed_payload = model.parse_obj(payload)
                    parsed_payload = json.loads(parsed_payload.json())
                    parsed_payload = model.parse_obj(parsed_payload)
                f(parsed_payload)
                metrics.tasks_succeeded_counter.labels(task=name).inc()
                elapsedseconds = time.time() - start_time
                metrics.tasks_execution_time_histogram.labels(task=name).observe(elapsedseconds)
            except Exception:
                metrics.tasks_failed_counter.labels(task=name).inc()
                raise
            finally:
                metrics.tasks_in_progress.labels(task=name).dec()

        return task

    return decorator

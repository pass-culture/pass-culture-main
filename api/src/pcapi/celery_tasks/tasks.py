import json
import logging
import time
import typing
from functools import wraps

from celery import Task
from celery import shared_task
from pydantic import BaseModel as BaseModelV2

import pcapi.celery_tasks.metrics as metrics
from pcapi import settings
from pcapi.utils import requests


# These values will prevent retrying tasks too far in the future as this can have negative effects
# because they are loaded by the worker. These can be increased memory consumption and risk of losing tasks.
# (https://docs.celeryq.dev/en/latest/userguide/calling.html#eta-and-countdown)
MAX_RETRY_DURATION = 1200  # 20 minutes

logger = logging.getLogger(__name__)


class CloudTaskRetryException(Exception):
    pass


def celery_async_task(
    name: str,
    model: type[BaseModelV2] | None = None,
    autoretry_for: tuple[type[Exception], ...] = tuple(),
    retry_backoff: bool = True,
    retry_backoff_max: int = settings.CELERY_TASK_RETRY_BACKOFF_MAX,
    max_retries: int = settings.CELERY_TASK_MAX_RETRIES,
    rate_limit: int | str | None = None,
    pii_fields: typing.Collection[str] | None = None,
) -> typing.Callable:
    """
    celery_async_task decorator is used to defer the function execution to a Celery worker.

    Parameters :
    name:  controls what route is used for the task and therefore which worker will run it.
    autoretry_for:  a tuple of exception that will make the worker retry the task automatically if they are raised.
    retry_backoff: if set, the task will not be retried immediately and will follow an exponential backoff retry scheme.
    model: if not None, will perform input validation against pydantic model and parse and load it to and from JSON to ensure
    that the input is JSON serializable. Otherwise this step will be skipped.
    pii_fields: keys of the payload that will be scrubbed for logging only
    """

    autoretry_for += (CloudTaskRetryException,)

    def decorator(f: typing.Callable) -> typing.Callable:
        @shared_task(
            bind=True,
            name=name,
            autoretry_for=autoretry_for,
            retry_backoff=retry_backoff,
            retry_backoff_max=retry_backoff_max,
            max_retries=max_retries,
            rate_limit=rate_limit,
            pii_fields=frozenset(pii_fields) if pii_fields else None,
        )
        @wraps(f)
        def task(self: Task, payload: dict) -> None:
            metrics.tasks_counter.labels(task=name).inc()
            metrics.tasks_in_progress.labels(task=name).inc()
            start_time = time.time()
            try:
                parsed_payload: BaseModelV2 | None = None
                if model is not None:
                    # We want to ensure payload is JSON serializable, we do that by encoding and decoding
                    # to and from json. This is needed because Celery uses the __repr__ of the task to pass
                    # it so values like dates and Decimal will be preserved instead of being transformed to their
                    # JSON representation.
                    # This is the same behavior that we had on cloud_tasks
                    parsed_payload = model.model_validate(payload)
                    parsed_payload = json.loads(parsed_payload.model_dump_json())
                    parsed_payload = model.model_validate(parsed_payload)

                f(parsed_payload)
                metrics.tasks_succeeded_counter.labels(task=name).inc()
                elapsedseconds = time.time() - start_time
                metrics.tasks_execution_time_histogram.labels(task=name).observe(elapsedseconds)

            # FIXME (tcoudray-pass, 25/11/25) To support a cloud tasks retry behavior
            # Should be removed once all the tasks have been migrated
            except requests.ExternalAPIException as exc:
                if exc.is_retryable:
                    raise CloudTaskRetryException()
            except Exception:
                metrics.tasks_failed_counter.labels(task=name).inc()
                raise
            finally:
                metrics.tasks_in_progress.labels(task=name).dec()

        return task

    return decorator

import json
import logging
import time
import typing
from contextlib import contextmanager
from functools import wraps

import pydantic.v1 as pydantic_v1
from celery import Task
from celery import shared_task
from flask import current_app as app

import pcapi.celery_tasks.metrics as metrics


# These values will prevent retrying tasks too far in the future as this can have negative effects
# because they are loaded by the worker. These can be increased memory consumption and risk of losing tasks.
# (https://docs.celeryq.dev/en/latest/userguide/calling.html#eta-and-countdown)
MAX_TIME_WINDOW_SIZE = 600
MAX_RETRY_DURATION = 1200

logger = logging.getLogger(__name__)


class RateLimitedError(Exception):
    def __init__(self, time_window_size: int, max_per_time_window: int, current: int):
        self.time_window_size = time_window_size
        self.max_per_time_window = max_per_time_window
        self.current = current


def get_key(name: str, time_window_size: int) -> str:
    # The rate limiting works by using time window of size "time_window_size".
    # If time_window_size is 60 (a minute) this means we will count every task call for a given minute
    # To identify a given time_window we divide the current timestamp by "time_window_size".
    time_window_id = int(time.time()) // time_window_size
    return f"pcapi:celery:bucket:{name}:{time_window_size}:{time_window_id}"


@contextmanager
def rate_limit(name: str, time_window_size: int, max_per_time_window: int) -> typing.Iterator:
    if max_per_time_window <= 0:
        raise ValueError("max_per_time_window parameter must be above 0")
    if time_window_size <= 0 or time_window_size >= MAX_TIME_WINDOW_SIZE:
        raise ValueError(f"time_window_size parameter must be between {MAX_TIME_WINDOW_SIZE}")
    key = get_key(name, time_window_size)
    current_value = app.redis_client.incr(key)
    app.redis_client.expire(key, 2 * time_window_size, nx=True)
    if current_value > max_per_time_window:
        raise RateLimitedError(time_window_size, max_per_time_window, current_value)
    yield


def celery_async_task(
    name: str,
    model: type[pydantic_v1.BaseModel] | None = None,
    autoretry_for: typing.Tuple[Exception, ...] = tuple(),
    retry_backoff: bool = True,
    time_window_size: int = 60,
    max_per_time_window: int | None = None,
) -> typing.Callable:
    """
    celery_async_task decorator is used to defer the function execution to a Celery worker.

    Parameters :
    name:  controls what route is used for the task and therefore which worker will run it.
    autoretry_for:  a tuple of exception that will make the worker retry the task automatically if they are raised.
    retry_backoff: if set, the task will not be retried immediately and will follow an exponential backoff retry scheme.
    model: if not None, will perform input validation against pydantic model and parse and load it to and from JSON to ensure
    that the input is JSON serializable. Otherwise this step will be skipped.
    time_window_size: time window in seconds during which no more than "max_per_time_window" tasks can run. Only used when "max_per_time_window" is set. Do not set this above visibility_timeout celery option, otherwise the behavior is not not predictable. Rate limited tasks will stay loaded in the worker memory and might be lost if the worker is killed abrutply (SIGKILL).
    max_per_time_window: the maximum number of tasks which can run during a time window. When the maximum is reached, tasks will be retried.
    """

    # Since tasks above "max_per_time_window" will be retried in "time_window_size" time, time_window_size cannot be above the visibility_timeout setting of redis
    # See https://docs.celeryq.dev/en/stable/getting-started/backends-and-brokers/redis.html#id3 for more details
    if time_window_size > 600:
        raise ValueError("task rate limit time_window_size above maximum")

    def decorator(f: typing.Callable) -> typing.Callable:
        @shared_task(bind=True, name=name, autoretry_for=autoretry_for, retry_backoff=retry_backoff)
        @wraps(f)
        def task(self: Task, payload: dict) -> None:
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
                if max_per_time_window:
                    with rate_limit(name, time_window_size, max_per_time_window):
                        f(parsed_payload)
                else:
                    f(parsed_payload)
                metrics.tasks_succeeded_counter.labels(task=name).inc()
                elapsedseconds = time.time() - start_time
                metrics.tasks_execution_time_histogram.labels(task=name).observe(elapsedseconds)
            except RateLimitedError as exp:
                logger.info(
                    "task rate-limited",
                    extra={
                        "time_window_size": exp.time_window_size,
                        "max_per_time_window": exp.max_per_time_window,
                        "current": exp.current,
                    },
                )
                calls_over_limit = exp.current - exp.max_per_time_window
                nb_time_windows_to_skip = 1 + (calls_over_limit // exp.max_per_time_window)
                time_to_wait_before_retry = exp.time_window_size * nb_time_windows_to_skip
                metrics.tasks_rate_limited_counter.labels(task=name).inc()
                self.retry(exc=exp, countdown=min(time_to_wait_before_retry, MAX_RETRY_DURATION))
            except Exception:
                metrics.tasks_failed_counter.labels(task=name).inc()
                raise
            finally:
                metrics.tasks_in_progress.labels(task=name).dec()

        return task

    return decorator

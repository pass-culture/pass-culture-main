from datetime import datetime
from functools import wraps
import logging
import time
import typing

from flask import current_app
from rq.job import get_current_job
from rq.queue import Queue

from pcapi import settings
from pcapi.workers.logger import job_extra_description


logger = logging.getLogger(__name__)


def job(queue: Queue) -> typing.Callable:
    def decorator(func: typing.Callable) -> typing.Callable:
        @wraps(func)
        def job_func(*args: typing.Any, **kwargs: typing.Any) -> None:
            current_job = get_current_job()
            if not current_job or settings.IS_JOB_SYNCHRONOUS:
                # in synchronous calls (as wall in TESTS because queued jobs are executed synchronously)
                # we don't want to create another session
                func(*args, **kwargs)
                return

            start = time.perf_counter()
            started_at = current_job.started_at or datetime.utcnow()
            enqueued_at = current_job.enqueued_at
            assert enqueued_at is not None  # help mypy
            logger.info(
                "Started job %s",
                func.__name__,
                extra={
                    **job_extra_description(current_job),
                    "status": "started",
                    "waiting_time": round(((started_at - enqueued_at).microseconds) / 1000),
                },
            )

            with current_app.app_context():
                func(*args, **kwargs)

            logger.info(
                "Ended job %s",
                func.__name__,
                extra={
                    **job_extra_description(current_job),
                    "status": "ended",
                    "duration": round((time.perf_counter() - start) * 1000),
                },
            )

        @wraps(job_func)
        def delay(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
            current_job = queue.enqueue(job_func, *args, **kwargs)
            logger.info(
                "Enqueue job %s",
                func.__name__,
                extra={**job_extra_description(current_job), "status": "enqueued"},
            )

        job_func.delay = delay  # type: ignore[attr-defined]
        return job_func

    return decorator

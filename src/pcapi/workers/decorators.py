from datetime import datetime
from functools import wraps
import logging
import time

from rq.job import get_current_job
from rq.queue import Queue

from pcapi.flask_app import app
from pcapi.settings import IS_RUNNING_TESTS
from pcapi.workers.logger import job_extra_description


logger = logging.getLogger(__name__)


def job(queue: Queue):
    def decorator(func):
        @wraps(func)
        def job_func(*args, **kwargs):
            current_job = get_current_job()
            if not current_job or IS_RUNNING_TESTS:
                # in synchronous calls (as wall in TESTS because queued jobs are executed synchronously)
                # we don't won't to create another session
                return func(*args, **kwargs)

            start = time.perf_counter()
            started_at = current_job.started_at or datetime.now()
            logger.info(
                "Started job %s",
                func.__name__,
                extra={
                    **job_extra_description(current_job),
                    "status": "started",
                    "waiting_time": round(((started_at - current_job.enqueued_at).microseconds) / 1000),
                },
            )

            # TODO(xordoquy): use flask.current_app to retrieve context
            with app.app_context():
                result = func(*args, **kwargs)

            logger.info(
                "Ended job %s",
                func.__name__,
                extra={
                    **job_extra_description(current_job),
                    "status": "ended",
                    "duration": round((time.perf_counter() - start) * 1000),
                },
            )
            return result

        @wraps(job_func)
        def delay(*args, **kwargs):
            current_job = queue.enqueue(job_func, *args, **kwargs)
            logger.info(
                "Enqueue job %s",
                func.__name__,
                extra={**job_extra_description(current_job), "status": "enqueued"},
            )
            return job

        job_func.delay = delay
        return job_func

    return decorator

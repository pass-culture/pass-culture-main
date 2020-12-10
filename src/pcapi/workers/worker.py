# Loading variables should always be the first thing, before any other load
from pcapi.load_environment_variables import load_environment_variables


load_environment_variables()

import logging
import time
from typing import Type

import redis
from rq import Connection
from rq import Queue
from rq import Worker
from rq.job import Job
import sentry_sdk
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.rq import RqIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from pcapi import settings
from pcapi.utils.health_checker import read_version_from_file
from pcapi.utils.logger import logger
from pcapi.workers.logger import JobStatus
from pcapi.workers.logger import build_job_log_message


listen = ["default"]
conn = redis.from_url(settings.REDIS_URL)
redis_queue = Queue(connection=conn)
logging.getLogger("rq.worker").setLevel(logging.CRITICAL)

if settings.IS_DEV is False:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[RedisIntegration(), RqIntegration(), SqlalchemyIntegration()],
        release=read_version_from_file(),
        environment=settings.ENV,
        traces_sample_rate=settings.SENTRY_SAMPLE_RATE,
    )


def log_worker_error(job: Job, exception_type: Type, exception_value: Exception) -> None:
    # This handler is called by `rq.Worker.handle_exception()` from an
    # `except` clause, so we can (and should) use `logger.exception`.
    logger.exception(build_job_log_message(job, JobStatus.FAILED, f"{exception_type.__name__}: {exception_value}"))


if __name__ == "__main__":
    while True:
        try:
            with Connection(conn):
                worker = Worker(list(map(Queue, listen)), exception_handlers=[log_worker_error])
                worker.work()

        except redis.ConnectionError:
            logger.warning("Catched connection error. Restarting in 5 seconds")
            time.sleep(5)

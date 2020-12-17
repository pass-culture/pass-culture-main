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
from pcapi.flask_app import app
from pcapi.utils.health_checker import check_database_connection
from pcapi.utils.health_checker import read_version_from_file
from pcapi.utils.logger import logger
from pcapi.workers.logger import JobStatus
from pcapi.workers.logger import build_job_log_message


listen = ["default"]
conn = redis.from_url(settings.REDIS_URL)
redis_queue = Queue(connection=conn)
logging.getLogger("rq.worker").setLevel(logging.CRITICAL)


def log_worker_error(job: Job, exception_type: Type, exception_value: Exception) -> None:
    # This handler is called by `rq.Worker.handle_exception()` from an
    # `except` clause, so we can (and should) use `logger.exception`.
    logger.exception(build_job_log_message(job, JobStatus.FAILED, f"{exception_type.__name__}: {exception_value}"))


def log_redis_connection_status():
    try:
        conn.ping()
        logger.info("Worker: redis connection OK")

    except redis.exceptions.ConnectionError as e:
        logger.critical("Worker: redis connection KO: %s", e)


def log_database_connection_status():
    with app.app_context():
        if check_database_connection():
            logger.info("Worker: database connection OK")
        else:
            logger.critical("Worker: database connection KO")


if __name__ == "__main__":
    log_redis_connection_status()
    log_database_connection_status()

    if settings.IS_DEV is False:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            integrations=[RedisIntegration(), RqIntegration(), SqlalchemyIntegration()],
            release=read_version_from_file(),
            environment=settings.ENV,
            traces_sample_rate=settings.SENTRY_SAMPLE_RATE,
        )
        logger.info("Worker : connection to sentry OK")
    while True:
        try:
            with Connection(conn):
                worker = Worker(list(map(Queue, listen)), exception_handlers=[log_worker_error])
                worker.work()

        except redis.ConnectionError:
            logger.warning("Worker connection error. Restarting in 5 seconds")
            time.sleep(5)

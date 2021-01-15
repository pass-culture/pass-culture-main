import logging
import sys
import time
from typing import Any
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

# FIXME (cgaunet, 2021-01-13): this is to prevent Booking circular import when importing user in read_version_from_file
from pcapi import models  # pylint: disable=unused-import
from pcapi import settings
from pcapi.flask_app import app
from pcapi.models.db import db
from pcapi.utils.health_checker import check_database_connection
from pcapi.utils.health_checker import read_version_from_file
from pcapi.utils.logger import logger
from pcapi.workers.logger import JobStatus
from pcapi.workers.logger import build_job_log_message


conn = redis.from_url(settings.REDIS_URL)
logging.getLogger("rq.worker").setLevel(logging.CRITICAL)

default_queue = Queue("default", connection=conn)
low_queue = Queue("low", connection=conn, default_timeout=3600)


def log_worker_error(job: Job, exception_type: Type, exception_value: Exception, traceback: Any = None) -> None:
    # This handler is called by `rq.Worker.handle_exception()` from an
    # `except` clause, so we can (and should) use `logger.exception`.
    logger.exception(build_job_log_message(job, JobStatus.FAILED, f"{exception_type.__name__}: {exception_value}"))


def log_redis_connection_status() -> None:
    try:
        conn.ping()
        logger.info("Worker: redis connection OK")
    except redis.exceptions.ConnectionError as e:
        logger.critical("Worker: redis connection KO: %s", e)


def log_database_connection_status() -> None:
    with app.app_context():
        if check_database_connection():
            logger.info("Worker: database connection OK")
        else:
            logger.critical("Worker: database connection KO")
    db.session.remove()
    db.session.close()
    db.engine.dispose()


if __name__ == "__main__":
    listen = sys.argv[1:] or ["default"]
    logger.info("Worker: listening to queues %s", listen)

    log_redis_connection_status()

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
            # This sessions removals are meant to prevent open db connection
            # to spread through forked children and cause bugs in the jobs
            # https://python-rq.org/docs/workers/#the-worker-lifecycle
            # https://docs.sqlalchemy.org/en/13/core/connections.html?highlight=dispose#engine-disposal
            db.session.remove()
            db.session.close()
            db.engine.dispose()
            with Connection(conn):
                worker = Worker(list(map(Queue, listen)), exception_handlers=[log_worker_error])
                worker.work()

        except redis.ConnectionError:
            logger.warning("Worker connection error. Restarting in 5 seconds")
            time.sleep(5)

import logging
import time
from typing import Any
from typing import Type

import click
import redis
from rq import Connection
from rq import Queue
from rq import Worker
from rq.job import Job
import sentry_sdk

from pcapi import settings
from pcapi.models import db
from pcapi.utils.blueprint import Blueprint
from pcapi.utils.health_checker import check_database_connection
from pcapi.workers.logger import job_extra_description


blueprint = Blueprint(__name__, __name__)
conn = redis.from_url(settings.REDIS_URL)

default_queue = Queue("default", connection=conn, is_async=(not settings.IS_RUNNING_TESTS))
low_queue = Queue("low", connection=conn, default_timeout=3600, is_async=(not settings.IS_RUNNING_TESTS))
id_check_queue = Queue("id_check", connection=conn, default_timeout=3600, is_async=(not settings.IS_RUNNING_TESTS))

logger = logging.getLogger(__name__)


def log_worker_error(job: Job, exception_type: Type, exception_value: Exception, traceback: Any = None) -> None:
    # This handler is called by `rq.Worker.handle_exception()` from an
    # `except` clause, so we can (and should) use `logger.exception`.
    logger.exception(
        "Failed job %s",
        job.func_name,
        extra={
            **job_extra_description(job),
            "status": "failed",
            "error": f"{exception_type.__name__}: {exception_value}",
        },
    )


def log_redis_connection_status() -> None:
    try:
        conn.ping()
        logger.info("Worker: redis connection OK")
    except redis.exceptions.ConnectionError as e:
        logger.critical("Worker: redis connection KO: %s", e)


def log_database_connection_status() -> None:
    if check_database_connection():
        logger.info("Worker: database connection OK")
    else:
        logger.critical("Worker: database connection KO")
    db.session.remove()
    db.session.close()
    db.engine.dispose()


@blueprint.cli.command("worker")
@click.argument("queues", nargs=-1)
def run_worker(queues=None):
    from flask import current_app as app

    sentry_sdk.set_tag("pcapi.app_type", "worker")
    queues = queues or ["default"]
    logger.info("Worker: listening to queues %s", queues)

    log_redis_connection_status()
    with app.app_context():
        log_database_connection_status()

    while True:
        try:
            with app.app_context():
                # This sessions removals are meant to prevent open db connection
                # to spread through forked children and cause bugs in the jobs
                # https://python-rq.org/docs/workers/#the-worker-lifecycle
                # https://docs.sqlalchemy.org/en/13/core/connections.html?highlight=dispose#engine-disposal
                db.session.remove()
                db.session.close()
                db.engine.dispose()
            with Connection(conn):
                worker = Worker(list(map(Queue, queues)), exception_handlers=[log_worker_error])
                worker.work()

        except redis.ConnectionError:
            logger.warning("Worker connection error. Restarting in 5 seconds")
            time.sleep(5)

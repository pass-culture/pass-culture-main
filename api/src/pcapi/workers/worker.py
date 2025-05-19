import logging
from resource import struct_rusage
from typing import Any
from typing import Iterable

import click
import redis
import sentry_sdk
from rq import Queue
from rq import Worker
from rq.job import Job

from pcapi import settings
from pcapi.models import db
from pcapi.utils.blueprint import Blueprint
from pcapi.utils.health_checker import check_database_connection
from pcapi.workers.logger import job_extra_description


blueprint = Blueprint(__name__, __name__)
conn = redis.from_url(settings.REDIS_URL)

default_queue = Queue("default", connection=conn, is_async=not settings.IS_JOB_SYNCHRONOUS)
low_queue = Queue("low", connection=conn, default_timeout=3600, is_async=not settings.IS_JOB_SYNCHRONOUS)

logger = logging.getLogger(__name__)


def log_worker_error(job: Job, exception_type: type, exception_value: Exception, traceback: Any | None = None) -> None:
    """This handler is called by `rq.Worker.handle_exception()` from an `except` clause,
    so we can (and should) use `logger.exception`."""
    # we don't need the whole path for pcapi.workers.function_xxx
    shortened_function_name = job.func_name.split(".")[-1]
    logger.exception(
        "[RQ](%s) Failed job !",
        shortened_function_name,
        extra={
            **job_extra_description(job),
            "status": "failed",
            "error": f"{exception_type.__name__}: {exception_value}",
        },
    )


def work_horse_killed_handler(job: Job, retpid: int, ret_val: int, rusage: struct_rusage) -> None:
    # we don't need the whole path for pcapi.workers.function_xxx
    shortened_function_name = job.func_name.split(".")[-1]
    logger.exception(
        "[RQ](%s) Work horse killed !",
        shortened_function_name,
        extra={
            **job_extra_description(job),
            "retpid": retpid,
            "ret_val": ret_val,
            "rusage": rusage,
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
def run_worker(queues: Iterable = ()) -> None:
    from flask import current_app as app

    sentry_sdk.set_tag("pcapi.app_type", "worker")
    queues = queues or ["default"]
    logger.info("Worker: listening to queues %s", queues)

    log_redis_connection_status()
    with app.app_context():
        log_database_connection_status()

    with app.app_context():
        # This sessions removals are meant to prevent open db connection
        # to spread through forked children and cause bugs in the jobs
        # https://python-rq.org/docs/workers/#the-worker-lifecycle
        # https://docs.sqlalchemy.org/en/13/core/connections.html?highlight=dispose#engine-disposal
        db.session.remove()
        db.session.close()
        db.engine.dispose()

    worker = Worker(
        [Queue(name, connection=conn) for name in queues],
        exception_handlers=[log_worker_error],
        work_horse_killed_handler=work_horse_killed_handler,
        connection=conn,
    )
    worker.work()

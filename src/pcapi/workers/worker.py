# Loading variables should always be the first thing, before any other load
from pcapi.load_environment_variables import load_environment_variables
load_environment_variables()

import time

import redis
from rq import Worker, Queue, Connection
from rq.job import Job
from pcapi.utils.config import REDIS_URL
from pcapi.workers.logger import build_job_log_message, JobStatus
import logging
from pcapi.utils.logger import logger
from typing import Type


listen = ['default']
conn = redis.from_url(REDIS_URL)
redis_queue = Queue(connection=conn)
logging.getLogger("rq.worker").setLevel(logging.CRITICAL)


def log_worker_error(job: Job, exception_type: Type, exception_value: Exception):
    # This handler is called by `rq.Worker.handle_exception()` from an
    # `except` clause, so we can (and should) use `logger.exception`.
    logger.exception(build_job_log_message(job, JobStatus.FAILED,
                                      f'{exception_type.__name__}: {exception_value}'))


if __name__ == '__main__':
    while True:
        try:
            with Connection(conn):
                worker = Worker(list(map(Queue, listen)), exception_handlers=[log_worker_error])
                worker.work()

        except redis.ConnectionError:
            logger.warning('Catched connection error. Restarting in 5 seconds')
            time.sleep(5)


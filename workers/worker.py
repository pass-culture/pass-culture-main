import redis
from rq import Worker, Queue, Connection
from utils.config import REDIS_URL
from workers.logger import build_job_log_message, JobStatus
import logging
from utils.logger import logger


listen = ['default']
conn = redis.from_url(REDIS_URL)
redis_queue = Queue(connection=conn)
logging.getLogger("rq.worker").setLevel(logging.CRITICAL)

def log_worker_error(job, exc_type, exc_value, traceback):
    logger.info(build_job_log_message(job, JobStatus.FAILED, f'{exc_type.__name__}: {exc_value}', traceback))


if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(list(map(Queue, listen)), exception_handlers=[log_worker_error])
        worker.work()

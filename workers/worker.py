import redis
from rq import Worker, Queue, Connection
from utils.config import REDIS_URL
from workers.logger import build_job_log_message


listen = ['default']
conn = redis.from_url(REDIS_URL)
redis_queue = Queue(connection=conn)

def worker_error_handler(job, exc_type, exc_value, traceback):
    print(build_job_log_message(job, f'{exc_type.__name__}: {exc_value}'))


if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(list(map(Queue, listen)), exception_handlers=[worker_error_handler])
        worker.work()

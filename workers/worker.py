import redis
from rq import Worker, Queue, Connection
from utils.config import REDIS_URL


listen = ['default']
conn = redis.from_url(REDIS_URL)
redis_queue = Queue(connection=conn)



if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(list(map(Queue, listen)))
        worker.work()

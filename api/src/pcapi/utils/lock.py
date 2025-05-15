import datetime
import time
import typing
from contextlib import contextmanager

import redis
from flask import current_app


class LockError(Exception):
    def __init__(self, name: str) -> None:
        self._name = name

    def __str__(self) -> str:
        return f"Failed to acquire lock: {self._name}"


@contextmanager
def lock(name: str, ttl: int | datetime.timedelta = 60, timeout: int | float = 30) -> typing.Iterator[None]:
    redis_client = current_app.redis_client
    start = time.time()
    while True:
        if not redis_client.exists(name):
            break
        if time.time() - start > timeout:
            raise LockError(name)
        time.sleep(0.1)

    redis_client.set(name, "1", ex=ttl, nx=True)
    try:
        yield
    finally:
        try:
            redis_client.delete(name)
        except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError):
            pass

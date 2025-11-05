import time
import typing
from contextlib import contextmanager

from flask import current_app as app


class RateLimitedError(Exception):
    def __init__(self, time_window_size: int, max_per_time_window: int, current: int):
        self.time_window_size = time_window_size
        self.max_per_time_window = max_per_time_window
        self.current = current


@contextmanager
def rate_limit(key: str, time_window_size: int, max_per_time_window: int) -> typing.Iterator:
    """
    The rate limiting uses fixed time windows of size "time_window_size".
    If time_window_size is 60 seconds, we will count every task call for a given minute
    To identify a given time_window we divide the current timestamp by "time_window_size".
    """
    if max_per_time_window <= 0:
        raise ValueError("max_per_time_window parameter must be above 0")
    if time_window_size <= 0:
        raise ValueError("time_window_size parameter must be above 0")

    time_window_id = int(time.time()) // time_window_size
    rate_limit_key = f"pcapi:rate_limit:{key}:{time_window_size}:{time_window_id}"

    current_value = app.redis_client.incr(rate_limit_key)
    app.redis_client.expire(rate_limit_key, 2 * time_window_size, nx=True)

    if current_value > max_per_time_window:
        raise RateLimitedError(time_window_size, max_per_time_window, current_value)

    yield

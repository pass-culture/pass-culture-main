import time
import typing
from contextlib import contextmanager

from pcapi.utils.redis import get_redis_client


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
    rate_limit_key = _get_rate_limit_key(key, time_window_size, max_per_time_window)

    current_value = get_redis_client().incr(rate_limit_key)
    get_redis_client().expire(rate_limit_key, 2 * time_window_size, nx=True)

    if current_value > max_per_time_window:
        raise RateLimitedError(time_window_size, max_per_time_window, current_value)

    yield


def get_current_rate_limit_window_remaining_usage(key: str, time_window_size: int, max_per_time_window: int) -> int:
    current_usage = get_current_rate_limit_usage(key, time_window_size, max_per_time_window)
    return max(max_per_time_window - current_usage, 0)


def get_current_rate_limit_usage(key: str, time_window_size: int, max_per_time_window: int) -> int:
    rate_limit_key = _get_rate_limit_key(key, time_window_size, max_per_time_window)
    current_usage = get_redis_client().get(rate_limit_key)
    return int(current_usage) if current_usage else 0


def _get_rate_limit_key(key: str, time_window_size: int, max_per_time_window: int) -> str:
    if max_per_time_window <= 0:
        raise ValueError("max_per_time_window parameter must be above 0")
    if time_window_size <= 0:
        raise ValueError("time_window_size parameter must be above 0")

    time_window_id = int(time.time()) // time_window_size
    return f"pcapi:rate_limit:{key}:{time_window_size}:{time_window_id}"


def lock_until_rate_limit_reset(lock_key: str, retry_after: int) -> None:
    get_redis_client().set(lock_key, "1", ex=retry_after)


def get_rate_limit_lock_ttl(lock_key: str) -> int:
    # `ttl` returns a negative value when the key has no expiry (-1) or does not exist (-2)
    return max(0, get_redis_client().ttl(lock_key))

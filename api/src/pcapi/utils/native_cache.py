"""Cache of native API responses in a dedicated Redis instance.

The cache stores the exact JSON body served on a miss and expires by TTL only.
It must never make a request fail: any error on the cache path falls back to
computing the response from the database.
"""

import functools
import hashlib
import json
import logging
import typing
from collections.abc import Callable

import pydantic as pydantic_v2
import redis
from prometheus_client import Counter
from redis.backoff import NoBackoff
from redis.retry import Retry

from pcapi import settings


logger = logging.getLogger(__name__)

cache_requests_counter = Counter(
    "pcapi_native_cache_requests_total",
    "Native API cache lookups by result",
    labelnames=["endpoint", "result"],
)

_client: "redis.Redis[str] | None" = None


class CachedJsonBody:
    """Response body already serialized to JSON, accepted by `spectree_serialize` like a response model."""

    def __init__(self, body: str) -> None:
        self._body = body

    def json(self, *args: typing.Any, **kwargs: typing.Any) -> str:
        return self._body


def is_enabled() -> bool:
    return bool(settings.REDIS_CACHE_URL) and settings.REDIS_CACHE_TTL_SECONDS > 0


def _get_client() -> "redis.Redis[str]":
    # Created on first use, in each worker process, so no connection is shared across forks.
    global _client  # noqa: PLW0603
    if _client is None:
        _client = redis.Redis.from_url(
            settings.REDIS_CACHE_URL,
            decode_responses=True,
            socket_timeout=settings.REDIS_CACHE_SOCKET_TIMEOUT_SECONDS,
            socket_connect_timeout=settings.REDIS_CACHE_SOCKET_CONNECT_TIMEOUT_SECONDS,
            retry=Retry(NoBackoff(), 1),
        )
    return _client


@functools.cache
def get_schema_hash(response_model: type[pydantic_v2.BaseModel]) -> str:
    schema = json.dumps(response_model.model_json_schema(by_alias=True), sort_keys=True)
    return hashlib.sha256(schema.encode("utf-8")).hexdigest()[:12]


def build_key(endpoint: str, api_version: str, response_model: type[pydantic_v2.BaseModel], object_id: int) -> str:
    """Single builder of cache keys: a response format change changes every key."""
    return f"native:{endpoint}:{api_version}:{get_schema_hash(response_model)}:{object_id}"


def get_or_compute(endpoint: str, key: str, compute: Callable[[], str]) -> str:
    """Return the cached JSON body for `key`, or compute it, store it and return it.

    `compute` raising (for instance on a 404) is not caught: nothing is stored.
    """
    if not is_enabled():
        return compute()

    try:
        cached = _get_client().get(key)
        if cached is not None:
            json.loads(cached)  # an unreadable entry falls back to the database
    except Exception as exc:
        _count_and_log_error(endpoint, "get", exc)
        return compute()

    if cached is not None:
        cache_requests_counter.labels(endpoint=endpoint, result="hit").inc()
        return cached

    cache_requests_counter.labels(endpoint=endpoint, result="miss").inc()
    body = compute()
    try:
        _get_client().set(key, body, ex=settings.REDIS_CACHE_TTL_SECONDS)
    except Exception as exc:
        _count_and_log_error(endpoint, "set", exc)
    return body


def _count_and_log_error(endpoint: str, operation: str, exc: Exception) -> None:
    cache_requests_counter.labels(endpoint=endpoint, result="error").inc()
    # Only the error type is logged: messages may contain the cache address
    logger.warning(
        "Native cache unavailable, falling back to database",
        extra={"endpoint": endpoint, "operation": operation, "error_type": type(exc).__name__},
    )

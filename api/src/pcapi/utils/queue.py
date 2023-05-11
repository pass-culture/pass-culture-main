import json
import logging

from flask import current_app
import redis.exceptions


logger = logging.getLogger(__name__)


def add_to_queue(queue_name: str, item: dict, at_head: bool = False) -> None:
    if not item:
        return
    dict_json = json.dumps(item)
    redis_client = current_app.redis_client  # type: ignore[attr-defined]
    try:
        if at_head:
            redis_client.lpush(queue_name, dict_json)
        else:
            redis_client.rpush(queue_name, dict_json)
    except redis.exceptions.RedisError:
        logger.exception("Could not add item to redis queue", extra={"queue": queue_name, "item": item})


def pop_from_queue(queue_name: str) -> dict | None:
    redis_client = current_app.redis_client  # type: ignore[attr-defined]
    try:
        item = redis_client.lpop(queue_name)
    except redis.exceptions.RedisError:
        logger.exception("Could not pop element from queue", extra={"queue": queue_name})
        return None
    return json.loads(item) if item else None

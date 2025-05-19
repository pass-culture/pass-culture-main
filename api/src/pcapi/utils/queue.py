import json
import logging

import redis.exceptions
from flask import current_app


logger = logging.getLogger(__name__)


def add_to_queue(queue_name: str, item: dict, at_head: bool = False) -> None:
    if not item:
        return
    dict_json = json.dumps(item)
    redis_client = current_app.redis_client
    try:
        if at_head:
            redis_client.lpush(queue_name, dict_json)
        else:
            redis_client.rpush(queue_name, dict_json)
    except redis.exceptions.RedisError:
        logger.exception("Could not add item to redis queue", extra={"queue": queue_name, "item": item})


def pop_from_queue(queue_name: str) -> dict | None:
    redis_client = current_app.redis_client
    try:
        item = redis_client.lpop(queue_name)
    except redis.exceptions.RedisError:
        logger.exception("Could not pop element from queue", extra={"queue": queue_name})
        return None
    return json.loads(item) if item else None

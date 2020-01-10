import os
from typing import List

import redis
from redis import Redis

from utils.human_ids import humanize
from utils.logger import logger

REDIS_LIST_OFFER_IDS = 'offer_ids'
REDIS_LRANGE_END = int(os.environ.get('REDIS_LRANGE_END', '1000'))


def add_to_redis(client: Redis, offer_id: int) -> None:
    try:
        client.rpush(REDIS_LIST_OFFER_IDS, offer_id)
        logger.debug(f'[REDIS] offer id "{humanize(offer_id)}" was added')
    except redis.exceptions.RedisError as error:
        logger.error(f'[REDIS] {error}')


def get_offer_ids(client: Redis) -> List[int]:
    try:
        offer_ids = client.lrange(REDIS_LIST_OFFER_IDS, 0, REDIS_LRANGE_END)
        return offer_ids
    except redis.exceptions.RedisError as error:
        logger.error(f'[REDIS] {error}')


def delete_offer_ids(client: Redis) -> None:
    try:
        client.ltrim(REDIS_LIST_OFFER_IDS, REDIS_LRANGE_END, -1)
        logger.debug('[REDIS] offer ids were deleted')
    except redis.exceptions.RedisError as error:
        logger.error(f'[REDIS] {error}')

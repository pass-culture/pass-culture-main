import os
from typing import List

import redis

from utils.human_ids import humanize
from utils.logger import logger

REDIS_HOST = 'redis'
REDIS_LIST_OFFER_IDS = 'offer_ids'
REDIS_LRANGE_END = int(os.environ.get('REDIS_LRANGE_END', '1000'))


def add_to_redis(offer_id: int) -> None:
    redis.Redis(host=REDIS_HOST) \
        .rpush(REDIS_LIST_OFFER_IDS, offer_id)
    logger.info(f'[REDIS] offer id "{humanize(offer_id)}" was added')


def get_offer_ids() -> List[int]:
    return redis.Redis(host=REDIS_HOST, decode_responses=True) \
        .lrange(REDIS_LIST_OFFER_IDS, 0, REDIS_LRANGE_END)


def delete_offer_ids():
    redis.Redis(host=REDIS_HOST) \
        .ltrim(REDIS_LIST_OFFER_IDS, REDIS_LRANGE_END, -1)
    logger.info('[REDIS] offer ids were deleted')

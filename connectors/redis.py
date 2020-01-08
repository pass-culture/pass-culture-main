import os
from typing import List

import redis

from utils.human_ids import humanize
from utils.logger import logger

REDIS_HOST = 'redis'
REDIS_LIST_OFFER_IDS = 'offer_ids'
REDIS_LRANGE_END = int(os.environ.get('REDIS_LRANGE_END', '1000'))


def add_to_redis(offer_id: int) -> None:
    try:
        redis.Redis(host=REDIS_HOST) \
            .rpush(REDIS_LIST_OFFER_IDS, offer_id)
        logger.info(f'[REDIS] offer id "{humanize(offer_id)}" was added')
    except redis.exceptions.ConnectionError:
        logger.info(f'[REDIS] Connection error, offer id "{humanize(offer_id)}" was not added')


def get_offer_ids() -> List[int]:
    try:
        offer_ids = redis.Redis(host=REDIS_HOST, decode_responses=True) \
            .lrange(REDIS_LIST_OFFER_IDS, 0, REDIS_LRANGE_END)
        return offer_ids
    except redis.exceptions.ConnectionError:
        logger.info(f'[REDIS] Connection error when attempting to retrieve offer ids')


def delete_offer_ids():
    try:
        redis.Redis(host=REDIS_HOST) \
            .ltrim(REDIS_LIST_OFFER_IDS, REDIS_LRANGE_END, -1)
        logger.info('[REDIS] offer ids were deleted')
    except redis.exceptions.ConnectionError:
        logger.info('[REDIS] Connection error, offer ids were not deleted')

import json
import os
from typing import List, Dict

import redis
from redis import Redis

from models.feature import FeatureToggle
from repository import feature_queries
from utils.human_ids import humanize
from utils.logger import logger

REDIS_LIST_OFFER_IDS_NAME = 'offer_ids'
REDIS_LIST_VENUE_IDS_NAME = 'venue_ids'
REDIS_LIST_VENUE_PROVIDERS_NAME = 'venue_providers'
REDIS_OFFER_IDS_LRANGE_END = int(os.environ.get('REDIS_OFFER_IDS_LRANGE_END', '1000'))
REDIS_VENUE_IDS_LRANGE_END = int(os.environ.get('REDIS_OFFER_IDS_LRANGE_END', '1000'))
REDIS_VENUES_PROVIDERS_LRANGE_END = int(os.environ.get('REDIS_VENUES_PROVIDERS_LRANGE_END', '1'))


def add_offer_id(client: Redis, offer_id: int) -> None:
    if feature_queries.is_active(FeatureToggle.SEARCH_ALGOLIA):
        try:
            client.rpush(REDIS_LIST_OFFER_IDS_NAME, offer_id)
            logger.debug(f'[REDIS] offer id "{humanize(offer_id)}" was added')
        except redis.exceptions.RedisError as error:
            logger.error(f'[REDIS] {error}')


def add_venue_id(client: Redis, venue_id: int) -> None:
    if feature_queries.is_active(FeatureToggle.SEARCH_ALGOLIA):
        try:
            client.rpush(REDIS_LIST_VENUE_IDS_NAME, venue_id)
            logger.debug(f'[REDIS] venue id "{humanize(venue_id)}" was added')
        except redis.exceptions.RedisError as error:
            logger.error(f'[REDIS] {error}')


def get_offer_ids(client: Redis) -> List[int]:
    try:
        offer_ids = client.lrange(REDIS_LIST_OFFER_IDS_NAME, 0, REDIS_OFFER_IDS_LRANGE_END)
        return offer_ids
    except redis.exceptions.RedisError as error:
        logger.error(f'[REDIS] {error}')


def get_venue_ids(client: Redis) -> List[int]:
    try:
        venue_ids = client.lrange(REDIS_LIST_VENUE_IDS_NAME, 0, REDIS_VENUE_IDS_LRANGE_END)
        return venue_ids
    except redis.exceptions.RedisError as error:
        logger.error(f'[REDIS] {error}')


def delete_offer_ids(client: Redis) -> None:
    try:
        client.ltrim(REDIS_LIST_OFFER_IDS_NAME, REDIS_OFFER_IDS_LRANGE_END, -1)
        logger.debug('[REDIS] offer ids were deleted')
    except redis.exceptions.RedisError as error:
        logger.error(f'[REDIS] {error}')


def delete_venue_ids(client: Redis) -> None:
    try:
        client.ltrim(REDIS_LIST_VENUE_IDS_NAME, REDIS_VENUE_IDS_LRANGE_END, -1)
        logger.debug('[REDIS] venue ids were deleted')
    except redis.exceptions.RedisError as error:
        logger.error(f'[REDIS] {error}')


def add_venue_provider_to_redis(client: Redis, venue_provider: Dict) -> None:
    try:
        venue_provider_as_string = json.dumps(venue_provider)
        client.rpush(REDIS_LIST_VENUE_PROVIDERS_NAME, venue_provider_as_string)
        logger.debug('[REDIS] venue provider was added')
    except redis.exceptions.RedisError as error:
        logger.error(f'[REDIS] {error}')


def get_venue_providers(client: Redis) -> List[dict]:
    try:
        venue_providers_as_string = client.lrange(REDIS_LIST_VENUE_PROVIDERS_NAME, 0, REDIS_VENUES_PROVIDERS_LRANGE_END)
        venue_providers_as_dict = list(
            map(lambda venue_provider: json.loads(venue_provider), venue_providers_as_string))
        return venue_providers_as_dict
    except redis.exceptions.RedisError as error:
        logger.error(f'[REDIS] {error}')


def delete_venue_providers(client: Redis) -> None:
    try:
        client.ltrim(REDIS_LIST_VENUE_PROVIDERS_NAME, REDIS_VENUES_PROVIDERS_LRANGE_END, -1)
        logger.debug('[REDIS] venues providers were deleted')
    except redis.exceptions.RedisError as error:
        logger.error(f'[REDIS] {error}')

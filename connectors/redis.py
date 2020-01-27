import json
import os
from typing import List

import redis
from models import VenueProvider
from models.feature import FeatureToggle
from redis import Redis
from repository import feature_queries
from utils.config import REDIS_URL
from utils.human_ids import humanize
from utils.logger import logger

REDIS_LIST_OFFER_IDS_NAME = 'offer_ids'
REDIS_LIST_VENUE_IDS_NAME = 'venue_ids'
REDIS_LIST_VENUE_PROVIDERS_NAME = 'venue_providers'
REDIS_OFFER_IDS_CHUNK_SIZE = int(os.environ.get('REDIS_OFFER_IDS_CHUNK_SIZE', '1000'))
REDIS_VENUE_IDS_CHUNK_SIZE = int(os.environ.get('REDIS_VENUE_IDS_CHUNK_SIZE', '1000'))
REDIS_VENUE_PROVIDERS_CHUNK_SIZE = int(os.environ.get('REDIS_VENUE_PROVIDERS_LRANGE_END', '1'))


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


def send_venue_provider_data_to_redis(venue_provider: VenueProvider) -> None:
    redis_client = redis.from_url(url=REDIS_URL, decode_responses=True)
    _add_venue_provider(client=redis_client, venue_provider=venue_provider)


def _add_venue_provider(client: Redis, venue_provider: VenueProvider) -> None:
    if feature_queries.is_active(FeatureToggle.SEARCH_ALGOLIA):
        try:
            venue_provider_as_dict = {
                'id': venue_provider.id,
                'lastProviderId': venue_provider.lastProviderId,
                'venueId': venue_provider.venueId
            }
            venue_provider_as_string = json.dumps(venue_provider_as_dict)
            client.rpush(REDIS_LIST_VENUE_PROVIDERS_NAME, venue_provider_as_string)
            logger.debug('[REDIS] venue provider was added')
        except redis.exceptions.RedisError as error:
            logger.error(f'[REDIS] {error}')


def get_offer_ids(client: Redis) -> List[int]:
    try:
        offer_ids = client.lrange(REDIS_LIST_OFFER_IDS_NAME, 0, REDIS_OFFER_IDS_CHUNK_SIZE)
        return offer_ids
    except redis.exceptions.RedisError as error:
        logger.error(f'[REDIS] {error}')


def get_venue_ids(client: Redis) -> List[int]:
    try:
        venue_ids = client.lrange(REDIS_LIST_VENUE_IDS_NAME, 0, REDIS_VENUE_IDS_CHUNK_SIZE)
        return venue_ids
    except redis.exceptions.RedisError as error:
        logger.error(f'[REDIS] {error}')


def delete_offer_ids(client: Redis) -> None:
    try:
        client.ltrim(REDIS_LIST_OFFER_IDS_NAME, REDIS_OFFER_IDS_CHUNK_SIZE, -1)
        logger.debug('[REDIS] offer ids were deleted')
    except redis.exceptions.RedisError as error:
        logger.error(f'[REDIS] {error}')


def delete_venue_ids(client: Redis) -> None:
    try:
        client.ltrim(REDIS_LIST_VENUE_IDS_NAME, REDIS_VENUE_IDS_CHUNK_SIZE, -1)
        logger.debug('[REDIS] venue ids were deleted')
    except redis.exceptions.RedisError as error:
        logger.error(f'[REDIS] {error}')


def get_venue_providers(client: Redis) -> List[dict]:
    try:
        venue_providers_as_string = client.lrange(REDIS_LIST_VENUE_PROVIDERS_NAME, 0, REDIS_VENUE_PROVIDERS_CHUNK_SIZE)
        return [json.loads(venue_provider) for venue_provider in venue_providers_as_string]
    except redis.exceptions.RedisError as error:
        logger.error(f'[REDIS] {error}')


def delete_venue_providers(client: Redis) -> None:
    try:
        client.ltrim(REDIS_LIST_VENUE_PROVIDERS_NAME, REDIS_VENUE_PROVIDERS_CHUNK_SIZE, -1)
        logger.debug('[REDIS] venues providers were deleted')
    except redis.exceptions.RedisError as error:
        logger.error(f'[REDIS] {error}')

import json
import os
from enum import Enum
from typing import List, Dict

import redis
from redis import Redis
from redis.client import Pipeline

from models import VenueProvider
from models.feature import FeatureToggle
from repository import feature_queries
from utils.config import REDIS_URL
from utils.human_ids import humanize
from utils.logger import logger

REDIS_OFFER_IDS_CHUNK_SIZE = int(os.environ.get('REDIS_OFFER_IDS_CHUNK_SIZE', 1000))
REDIS_VENUE_IDS_CHUNK_SIZE = int(os.environ.get('REDIS_VENUE_IDS_CHUNK_SIZE', 1000))
REDIS_VENUE_PROVIDERS_CHUNK_SIZE = int(os.environ.get('REDIS_VENUE_PROVIDERS_LRANGE_END', 1))


class RedisBucket(Enum):
    REDIS_LIST_OFFER_IDS_NAME = 'offer_ids'
    REDIS_LIST_VENUE_IDS_NAME = 'venue_ids'
    REDIS_LIST_VENUE_PROVIDERS_NAME = 'venue_providers'
    REDIS_HASHMAP_INDEXED_OFFERS_NAME = 'indexed_offers'
    REDIS_HASHMAP_VENUE_PROVIDERS_IN_SYNC_NAME = 'venue_providers_in_sync'


def add_offer_id(client: Redis, offer_id: int) -> None:
    if feature_queries.is_active(FeatureToggle.SEARCH_ALGOLIA):
        try:
            client.rpush(RedisBucket.REDIS_LIST_OFFER_IDS_NAME.value, offer_id)
            logger.debug(f'[REDIS] offer id "{humanize(offer_id)}" was added')
        except redis.exceptions.RedisError as error:
            logger.error(f'[REDIS] {error}')


def add_venue_id(client: Redis, venue_id: int) -> None:
    if feature_queries.is_active(FeatureToggle.SEARCH_ALGOLIA):
        try:
            client.rpush(RedisBucket.REDIS_LIST_VENUE_IDS_NAME.value, venue_id)
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
                'providerId': venue_provider.providerId,
                'venueId': venue_provider.venueId
            }
            venue_provider_as_string = json.dumps(venue_provider_as_dict)
            client.rpush(RedisBucket.REDIS_LIST_VENUE_PROVIDERS_NAME.value, venue_provider_as_string)
            logger.debug('[REDIS] venue provider was added')
        except redis.exceptions.RedisError as error:
            logger.error(f'[REDIS] {error}')


def get_offer_ids(client: Redis) -> List[int]:
    try:
        offer_ids = client.lrange(RedisBucket.REDIS_LIST_OFFER_IDS_NAME.value, 0, REDIS_OFFER_IDS_CHUNK_SIZE)
        return offer_ids
    except redis.exceptions.RedisError as error:
        logger.error(f'[REDIS] {error}')


def get_venue_ids(client: Redis) -> List[int]:
    try:
        venue_ids = client.lrange(RedisBucket.REDIS_LIST_VENUE_IDS_NAME.value, 0, REDIS_VENUE_IDS_CHUNK_SIZE)
        return venue_ids
    except redis.exceptions.RedisError as error:
        logger.error(f'[REDIS] {error}')


def get_venue_providers(client: Redis) -> List[dict]:
    try:
        venue_providers_as_string = client.lrange(RedisBucket.REDIS_LIST_VENUE_PROVIDERS_NAME.value, 0,
                                                  REDIS_VENUE_PROVIDERS_CHUNK_SIZE)
        return [json.loads(venue_provider) for venue_provider in venue_providers_as_string]
    except redis.exceptions.RedisError as error:
        logger.error(f'[REDIS] {error}')


def delete_offer_ids(client: Redis) -> None:
    try:
        client.ltrim(RedisBucket.REDIS_LIST_OFFER_IDS_NAME.value, REDIS_OFFER_IDS_CHUNK_SIZE, -1)
        logger.debug('[REDIS] offer ids were deleted')
    except redis.exceptions.RedisError as error:
        logger.error(f'[REDIS] {error}')


def delete_venue_ids(client: Redis) -> None:
    try:
        client.ltrim(RedisBucket.REDIS_LIST_VENUE_IDS_NAME.value, REDIS_VENUE_IDS_CHUNK_SIZE, -1)
        logger.debug('[REDIS] venue ids were deleted')
    except redis.exceptions.RedisError as error:
        logger.error(f'[REDIS] {error}')


def delete_venue_providers(client: Redis) -> None:
    try:
        client.ltrim(RedisBucket.REDIS_LIST_VENUE_PROVIDERS_NAME.value, REDIS_VENUE_PROVIDERS_CHUNK_SIZE, -1)
        logger.debug('[REDIS] venues providers were deleted')
    except redis.exceptions.RedisError as error:
        logger.error(f'[REDIS] {error}')


def add_to_indexed_offers(pipeline: Pipeline, offer_id: int, offer_details: dict) -> None:
    try:
        offer_details_as_string = json.dumps(offer_details)
        pipeline.hset(RedisBucket.REDIS_HASHMAP_INDEXED_OFFERS_NAME.value, offer_id, offer_details_as_string)
        logger.debug(f'[REDIS] "{offer_id}" was added to indexed offers')
    except redis.exceptions.RedisError as error:
        logger.error(f'[REDIS] {error}')


def delete_indexed_offers(client: Redis, offer_ids: List[int]) -> None:
    try:
        client.hdel(RedisBucket.REDIS_HASHMAP_INDEXED_OFFERS_NAME.value, *offer_ids)
        logger.debug(f'[REDIS] "{len(offer_ids)}" were deleted from indexed offers')
    except redis.exceptions.RedisError as error:
        logger.error(f'[REDIS] {error}')


def check_offer_exists(client: Redis, offer_id: int) -> bool:
    try:
        offer_exist = client.hexists(RedisBucket.REDIS_HASHMAP_INDEXED_OFFERS_NAME.value, offer_id)
        return offer_exist
    except redis.exceptions.RedisError as error:
        logger.error(f'[REDIS] {error}')


def get_offer_details(client: Redis, offer_id: int) -> Dict:
    try:
        offer_details = client.hget(RedisBucket.REDIS_HASHMAP_INDEXED_OFFERS_NAME.value, offer_id)

        if offer_details:
            return json.loads(offer_details)
        return dict()
    except redis.exceptions.RedisError as error:
        logger.error(f'[REDIS] {error}')


def delete_all_indexed_offers(client: Redis) -> None:
    try:
        client.delete(RedisBucket.REDIS_HASHMAP_INDEXED_OFFERS_NAME.value)
        logger.debug(f'[REDIS] indexed offers were deleted')
    except redis.exceptions.RedisError as error:
        logger.error(f'[REDIS] {error}')


def add_venue_provider_currently_in_sync(client: Redis, venue_provider_id: int, container_id: str) -> None:
    try:
        client.hset(RedisBucket.REDIS_HASHMAP_VENUE_PROVIDERS_IN_SYNC_NAME.value, venue_provider_id, container_id)
        logger.debug(f'[REDIS] venue provider "{venue_provider_id}" in container {container_id} was added.')
    except redis.exceptions.RedisError as error:
        logger.error(f'[REDIS] {error}')


def delete_venue_provider_currently_in_sync(client: Redis, venue_provider_id: int) -> None:
    try:
        container_id = client.hget(RedisBucket.REDIS_HASHMAP_VENUE_PROVIDERS_IN_SYNC_NAME.value, venue_provider_id)
        client.hdel(RedisBucket.REDIS_HASHMAP_VENUE_PROVIDERS_IN_SYNC_NAME.value, venue_provider_id)
        logger.debug(f'[REDIS] venue provider "{venue_provider_id}" in container {container_id} was deleted.')
    except redis.exceptions.RedisError as error:
        logger.error(f'[REDIS] {error}')


def get_number_of_venue_providers_currently_in_sync(client: Redis) -> int:
    try:
        return client.hlen(RedisBucket.REDIS_HASHMAP_VENUE_PROVIDERS_IN_SYNC_NAME.value)
    except redis.exceptions.RedisError as error:
        logger.error(f'[REDIS] {error}')

from enum import Enum
import json
import logging

import redis
from redis import Redis
from redis.client import Pipeline

from pcapi import settings


logger = logging.getLogger(__name__)


class RedisBucket(Enum):
    REDIS_LIST_OFFER_IDS_NAME = "offer_ids"
    REDIS_LIST_OFFER_IDS_IN_ERROR_NAME = "offer_ids_in_error"
    REDIS_LIST_VENUE_IDS_NAME = "venue_ids"
    REDIS_LIST_VENUE_PROVIDERS_NAME = "venue_providers"
    REDIS_HASHMAP_INDEXED_OFFERS_NAME = "indexed_offers"
    REDIS_HASHMAP_VENUE_PROVIDERS_IN_SYNC_NAME = "venue_providers_in_sync"


def add_offer_id(client: Redis, offer_id: int) -> None:
    try:
        client.rpush(RedisBucket.REDIS_LIST_OFFER_IDS_NAME.value, offer_id)
    except redis.exceptions.RedisError as error:
        logger.exception("[REDIS] %s", error)


def add_venue_id(client: Redis, venue_id: int) -> None:
    try:
        client.rpush(RedisBucket.REDIS_LIST_VENUE_IDS_NAME.value, venue_id)
    except redis.exceptions.RedisError as error:
        logger.exception("[REDIS] %s", error)


def send_venue_provider_data_to_redis(venue_provider) -> None:
    redis_client = redis.from_url(url=settings.REDIS_URL, decode_responses=True)
    _add_venue_provider(client=redis_client, venue_provider=venue_provider)


def _add_venue_provider(client: Redis, venue_provider) -> None:
    try:
        venue_provider_as_dict = {
            "id": venue_provider.id,
            "providerId": venue_provider.providerId,
            "venueId": venue_provider.venueId,
        }
        venue_provider_as_string = json.dumps(venue_provider_as_dict)
        client.rpush(RedisBucket.REDIS_LIST_VENUE_PROVIDERS_NAME.value, venue_provider_as_string)
    except redis.exceptions.RedisError as error:
        logger.exception("[REDIS] %s", error)


def get_offer_ids(client: Redis) -> list[int]:
    try:
        offer_ids = client.lrange(RedisBucket.REDIS_LIST_OFFER_IDS_NAME.value, 0, settings.REDIS_OFFER_IDS_CHUNK_SIZE)
        return offer_ids
    except redis.exceptions.RedisError as error:
        logger.exception("[REDIS] %s", error)
        return []


def pop_offer_ids(client: Redis) -> list[int]:
    # FIXME (dbaty, 2021-04-30): Here we should use `LPOP` but its
    # `count` argument has been added in Redis 6.2. GCP currently has
    # an earlier version of Redis (5.0), where we can pop only one
    # item at once. As a work around, we get and delete items within a
    # pipeline, which should be atomic.
    #
    # The error handling is minimal:
    # - if the get fails, the function returns an empty list. It's
    #   fine, the next run may have more chance and may work;
    # - if the delete fails, we'll process the same batch twice. It's
    #   not optimal, but it's ok.
    #
    # Fun fact: if we stored offer ids in a set (and not a list), we
    # could use `SPOP` (where the `count` argument has been added in
    # Redis 3.2).
    offer_ids = []

    try:
        pipeline = client.pipeline(transaction=True)
        pipeline.lrange(RedisBucket.REDIS_LIST_OFFER_IDS_NAME.value, 0, settings.REDIS_OFFER_IDS_CHUNK_SIZE - 1)
        pipeline.ltrim(RedisBucket.REDIS_LIST_OFFER_IDS_NAME.value, settings.REDIS_OFFER_IDS_CHUNK_SIZE, -1)
        results = pipeline.execute()
        offer_ids = results[0]
    except redis.exceptions.RedisError as error:
        logger.exception("Got Redis error in pop_offer_ids: %s", error)
    finally:
        pipeline.reset()
    return offer_ids


def get_venue_ids(client: Redis) -> list[int]:
    try:
        venue_ids = client.lrange(RedisBucket.REDIS_LIST_VENUE_IDS_NAME.value, 0, settings.REDIS_VENUE_IDS_CHUNK_SIZE)
        return venue_ids
    except redis.exceptions.RedisError as error:
        logger.exception("[REDIS] %s", error)
        return []


def get_venue_providers(client: Redis) -> list[dict]:
    try:
        venue_providers_as_string = client.lrange(
            RedisBucket.REDIS_LIST_VENUE_PROVIDERS_NAME.value, 0, settings.REDIS_VENUE_PROVIDERS_CHUNK_SIZE
        )
        return [json.loads(venue_provider) for venue_provider in venue_providers_as_string]
    except redis.exceptions.RedisError as error:
        logger.exception("[REDIS] %s", error)
        return []


def delete_offer_ids(client: Redis) -> None:
    try:
        client.ltrim(RedisBucket.REDIS_LIST_OFFER_IDS_NAME.value, settings.REDIS_OFFER_IDS_CHUNK_SIZE, -1)
    except redis.exceptions.RedisError as error:
        logger.exception("[REDIS] %s", error)


def delete_venue_ids(client: Redis) -> None:
    try:
        client.ltrim(RedisBucket.REDIS_LIST_VENUE_IDS_NAME.value, settings.REDIS_VENUE_IDS_CHUNK_SIZE, -1)
    except redis.exceptions.RedisError as error:
        logger.exception("[REDIS] %s", error)


def delete_venue_providers(client: Redis) -> None:
    try:
        client.ltrim(RedisBucket.REDIS_LIST_VENUE_PROVIDERS_NAME.value, settings.REDIS_VENUE_PROVIDERS_CHUNK_SIZE, -1)
    except redis.exceptions.RedisError as error:
        logger.exception("[REDIS] %s", error)


def add_to_indexed_offers(pipeline: Pipeline, offer_id: int, offer_details: dict) -> None:
    try:
        offer_details_as_string = json.dumps(offer_details)
        pipeline.hset(RedisBucket.REDIS_HASHMAP_INDEXED_OFFERS_NAME.value, offer_id, offer_details_as_string)
    except redis.exceptions.RedisError as error:
        logger.exception("[REDIS] %s", error)


def delete_indexed_offers(client: Redis, offer_ids: list[int]) -> None:
    try:
        client.hdel(RedisBucket.REDIS_HASHMAP_INDEXED_OFFERS_NAME.value, *offer_ids)
    except redis.exceptions.RedisError as error:
        logger.exception("[REDIS] %s", error)


def check_offer_exists(client: Redis, offer_id: int) -> bool:
    try:
        offer_exist = client.hexists(RedisBucket.REDIS_HASHMAP_INDEXED_OFFERS_NAME.value, offer_id)
        return offer_exist
    except redis.exceptions.RedisError as error:
        logger.exception("[REDIS] %s", error)
        return False


def get_offer_details(client: Redis, offer_id: int) -> dict:
    try:
        offer_details = client.hget(RedisBucket.REDIS_HASHMAP_INDEXED_OFFERS_NAME.value, offer_id)

        if offer_details:
            return json.loads(offer_details)
        return dict()
    except redis.exceptions.RedisError as error:
        logger.exception("[REDIS] %s", error)
        return dict()


def delete_all_indexed_offers(client: Redis) -> None:
    try:
        client.delete(RedisBucket.REDIS_HASHMAP_INDEXED_OFFERS_NAME.value)
    except redis.exceptions.RedisError as error:
        logger.exception("[REDIS] %s", error)


def add_venue_provider_currently_in_sync(client: Redis, venue_provider_id: int, container_id: str) -> None:
    try:
        client.hset(RedisBucket.REDIS_HASHMAP_VENUE_PROVIDERS_IN_SYNC_NAME.value, venue_provider_id, container_id)
    except redis.exceptions.RedisError as error:
        logger.exception("[REDIS] %s", error)


def delete_venue_provider_currently_in_sync(client: Redis, venue_provider_id: int) -> None:
    try:
        client.hget(RedisBucket.REDIS_HASHMAP_VENUE_PROVIDERS_IN_SYNC_NAME.value, venue_provider_id)
        client.hdel(RedisBucket.REDIS_HASHMAP_VENUE_PROVIDERS_IN_SYNC_NAME.value, venue_provider_id)
    except redis.exceptions.RedisError as error:
        logger.exception("[REDIS] %s", error)


def get_number_of_venue_providers_currently_in_sync(client: Redis) -> int:
    try:
        return client.hlen(RedisBucket.REDIS_HASHMAP_VENUE_PROVIDERS_IN_SYNC_NAME.value)
    except redis.exceptions.RedisError as error:
        logger.exception("[REDIS] %s", error)
        return 0


def add_offer_ids_in_error(client: Redis, offer_ids: list[int]) -> None:
    try:
        client.rpush(RedisBucket.REDIS_LIST_OFFER_IDS_IN_ERROR_NAME.value, *offer_ids)
    except redis.exceptions.RedisError as error:
        logger.exception("[REDIS] %s", error)


def get_offer_ids_in_error(client: Redis) -> list[int]:
    try:
        offer_ids = client.lrange(
            RedisBucket.REDIS_LIST_OFFER_IDS_IN_ERROR_NAME.value, 0, settings.REDIS_OFFER_IDS_CHUNK_SIZE
        )
        return offer_ids
    except redis.exceptions.RedisError as error:
        logger.exception("[REDIS] %s", error)
        return []


def delete_offer_ids_in_error(client: Redis) -> None:
    try:
        client.ltrim(
            RedisBucket.REDIS_LIST_OFFER_IDS_IN_ERROR_NAME.value, settings.REDIS_OFFER_IDS_IN_ERROR_CHUNK_SIZE, -1
        )
    except redis.exceptions.RedisError as error:
        logger.exception("[REDIS] %s", error)

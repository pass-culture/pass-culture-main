from typing import List

from redis import Redis
from redis.client import Pipeline

from algolia.api import add_objects, clear_objects, delete_objects
from algolia.builder import build_object
from algolia.rules_engine import is_eligible_for_indexing
from connectors.redis import add_offer_to_hashmap, get_offer_from_hashmap, delete_offer_ids_from_list, \
    delete_offers_from_hashmap, get_offer_details_from_hashmap
from models import Offer
from repository import offer_queries
from utils.human_ids import humanize
from utils.logger import logger


def orchestrate_from_offer(client: Redis, offer_ids: List[int], is_clear: bool = False) -> None:
    if is_clear:
        clear_objects()

    adding_objects = []
    deleting_objects = []
    deleting_offer_ids = []
    pipeline = client.pipeline()

    offers = offer_queries.get_offers_by_ids(offer_ids)
    for offer in offers:
        if is_eligible_for_indexing(offer):
            adding_objects.append(build_object(offer=offer))
            add_offer_to_hashmap(pipeline=pipeline, offer_id=offer.id, offer_details={})
        else:
            offer_exists = get_offer_from_hashmap(client=client, offer_id=offer.id)
            if offer_exists:
                deleting_objects.append(humanize(offer.id))
                deleting_offer_ids.append(offer.id)

    if len(adding_objects) > 0:
        _process_adding(pipeline=pipeline, adding_objects=adding_objects)

    if len(deleting_objects) > 0:
        _process_deleting(client=client, deleting_objects=deleting_objects, offer_ids=offer_ids)

    delete_offer_ids_from_list(client=client)


def orchestrate_from_venue_provider(client: Redis, offer_ids: List[int]) -> None:
    adding_objects = []
    deleting_objects = []
    deleting_offer_ids = []
    pipeline = client.pipeline()

    offers = offer_queries.get_offers_by_ids(offer_ids)
    for offer in offers:
        offer_exists = get_offer_from_hashmap(client=client, offer_id=offer.id)

        if is_eligible_for_indexing(offer):
            if offer_exists:
                offer_details = get_offer_details_from_hashmap(client=client, offer_id=offer.id)
                if offer_details:
                    if _is_eligible_to_reindexing(offer, offer_details):
                        adding_objects.append(build_object(offer=offer))
                        add_offer_to_hashmap(pipeline=pipeline,
                                             offer_id=offer.id,
                                             offer_details=_build_offer_details_to_be_indexed(offer))
            else:
                adding_objects.append(build_object(offer=offer))
                add_offer_to_hashmap(pipeline=pipeline,
                                     offer_id=offer.id,
                                     offer_details=_build_offer_details_to_be_indexed(offer))
        else:
            if offer_exists:
                deleting_objects.append(humanize(offer.id))
                deleting_offer_ids.append(offer.id)

    if len(adding_objects) > 0:
        _process_adding(pipeline=pipeline, adding_objects=adding_objects)

    if len(deleting_objects) > 0:
        _process_deleting(client=client, deleting_objects=deleting_objects, offer_ids=offer_ids)

    delete_offer_ids_from_list(client=client)


def orchestrate_delete_expired_offers(client: Redis, offer_ids: List[int]) -> None:
    if len(offer_ids) > 0:
        humanized_offer_ids = []
        for offer_id in offer_ids:
            offer_exists = get_offer_from_hashmap(client=client, offer_id=offer_id)

            if offer_exists:
                humanized_offer_ids.append(humanize(offer_id))

        if len(humanized_offer_ids) > 0:
            _process_deleting(client=client, deleting_objects=humanized_offer_ids, offer_ids=offer_ids)


def _is_eligible_to_reindexing(offer: Offer, offer_details: dict) -> bool:
    offer_name = offer.name
    offer_date_range = list(map(str, offer.dateRange.datetimes))
    indexed_offer_name = offer_details['name']
    indexed_offer_date_range = offer_details['dateRange']

    return offer_name != indexed_offer_name or offer_date_range != indexed_offer_date_range


def _build_offer_details_to_be_indexed(offer: Offer) -> dict:
    offer_details_to_be_indexed = {
        'name': offer.name,
        'dateRange': list(map(str, offer.dateRange.datetimes))
    }
    return offer_details_to_be_indexed


def _process_adding(pipeline: Pipeline, adding_objects: List[dict]) -> None:
    add_objects(objects=adding_objects)
    logger.info(f'[ALGOLIA] indexed {len(adding_objects)} objects')
    pipeline.execute()
    pipeline.reset()


def _process_deleting(client: Redis, deleting_objects: List[str], offer_ids: List[int]) -> None:
    delete_objects(object_ids=deleting_objects)
    delete_offers_from_hashmap(client=client, offer_ids=offer_ids)
    logger.info(f'[ALGOLIA] deleted {len(deleting_objects)} objects from index')

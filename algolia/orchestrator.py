from datetime import datetime
from typing import List

from redis import Redis
from redis.client import Pipeline

from algolia.api import add_objects, delete_objects
from algolia.builder import build_object
from algolia.rules_engine import is_eligible_for_indexing, is_eligible_for_reindexing
from connectors.redis import add_to_indexed_offers, check_offer_exists, delete_offer_ids, \
    delete_indexed_offers, get_offer_details
from models import Offer
from repository import offer_queries
from utils.human_ids import humanize
from utils.logger import logger


def process_eligible_offers(client: Redis, offer_ids: List[int], from_provider_update: bool = False) -> None:
    offers_to_add = []
    offers_to_delete = []
    pipeline = client.pipeline()

    offers = offer_queries.get_offers_by_ids(offer_ids)
    for offer in offers:
        offer_exists = check_offer_exists(client=client, offer_id=offer.id)

        if is_eligible_for_indexing(offer):
            if from_provider_update and offer_exists:
                offer_details = get_offer_details(client=client, offer_id=offer.id)
                if offer_details and is_eligible_for_reindexing(offer, offer_details):
                    offers_to_add.append(build_object(offer=offer))
                    add_to_indexed_offers(pipeline=pipeline,
                                          offer_id=offer.id,
                                          offer_details=_build_offer_details_to_be_indexed(offer))
            else:
                offers_to_add.append(build_object(offer=offer))
                add_to_indexed_offers(pipeline=pipeline,
                                      offer_id=offer.id,
                                      offer_details=_build_offer_details_to_be_indexed(offer))
        else:
            if offer_exists:
                offers_to_delete.append(offer.id)

    if len(offers_to_add) > 0:
        _process_adding(pipeline=pipeline, adding_objects=offers_to_add)

    if len(offers_to_delete) > 0:
        _process_deleting(client=client, offer_ids_to_delete=offers_to_delete)

    delete_offer_ids(client=client)


def delete_expired_offers(client: Redis, offer_ids: List[int]) -> None:
    offer_ids_to_delete = []
    for offer_id in offer_ids:
        offer_exists = check_offer_exists(client=client, offer_id=offer_id)

        if offer_exists:
            offer_ids_to_delete.append(offer_id)

    if len(offer_ids_to_delete) > 0:
        _process_deleting(client=client, offer_ids_to_delete=offer_ids_to_delete)


def _build_offer_details_to_be_indexed(offer: Offer) -> dict:
    offer_details = {
        'name': offer.name,
        'dateRange': list(map(str, offer.dateRange.datetimes)),
        'dates': []
    }

    if offer.isEvent:
        offer_details['dates'] = list(map(lambda stock: datetime.timestamp(stock.beginningDatetime), offer.notDeletedStocks))

    return offer_details


def _process_adding(pipeline: Pipeline, adding_objects: List[dict]) -> None:
    add_objects(objects=adding_objects)
    logger.info(f'[ALGOLIA] indexed {len(adding_objects)} objects')
    pipeline.execute()
    pipeline.reset()


def _process_deleting(client: Redis, offer_ids_to_delete: List[int]) -> None:
    humanized_offer_ids_to_delete = [humanize(offer_id) for offer_id in offer_ids_to_delete]
    delete_objects(object_ids=humanized_offer_ids_to_delete)
    delete_indexed_offers(client=client, offer_ids=offer_ids_to_delete)
    logger.info(f'[ALGOLIA] deleted {len(offer_ids_to_delete)} objects from index')

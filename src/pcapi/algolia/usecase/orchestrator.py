from datetime import datetime
from typing import List

from algoliasearch.exceptions import AlgoliaException
from redis import Redis
from redis.client import Pipeline

from pcapi.algolia.domain.rules_engine import is_eligible_for_reindexing
from pcapi.algolia.infrastructure.api import add_objects
from pcapi.algolia.infrastructure.api import delete_objects
from pcapi.algolia.infrastructure.builder import build_object
from pcapi.connectors.redis import add_offer_ids_in_error
from pcapi.connectors.redis import add_to_indexed_offers
from pcapi.connectors.redis import check_offer_exists
from pcapi.connectors.redis import delete_indexed_offers
from pcapi.connectors.redis import get_offer_details
from pcapi.models import Offer
from pcapi.repository import offer_queries
from pcapi.utils.human_ids import humanize
from pcapi.utils.logger import logger


def process_eligible_offers(client: Redis, offer_ids: List[int], from_provider_update: bool = False) -> None:
    offers_to_add = []
    offers_to_delete = []
    pipeline = client.pipeline()

    offers = offer_queries.get_offers_by_ids(offer_ids)
    for offer in offers:
        offer_exists = check_offer_exists(client=client, offer_id=offer.id)

        if offer and offer.isBookable:
            if from_provider_update and offer_exists:
                offer_details = get_offer_details(client=client, offer_id=offer.id)
                if offer_details and is_eligible_for_reindexing(offer, offer_details):
                    offers_to_add.append(build_object(offer=offer))
                    add_to_indexed_offers(
                        pipeline=pipeline, offer_id=offer.id, offer_details=_build_offer_details_to_be_indexed(offer)
                    )
            else:
                offers_to_add.append(build_object(offer=offer))
                add_to_indexed_offers(
                    pipeline=pipeline, offer_id=offer.id, offer_details=_build_offer_details_to_be_indexed(offer)
                )
        else:
            if offer_exists:
                offers_to_delete.append(offer.id)

    if len(offers_to_add) > 0:
        _process_adding(pipeline=pipeline, client=client, offer_ids=offer_ids, adding_objects=offers_to_add)

    if len(offers_to_delete) > 0:
        _process_deleting(client=client, offer_ids_to_delete=offers_to_delete)

    if len(offers_to_add) == 0 and len(offers_to_delete):
        logger.info(f"[ALGOLIA] no objects were added nor deleted!")


def delete_expired_offers(client: Redis, offer_ids: List[int]) -> None:
    offer_ids_to_delete = []
    for offer_id in offer_ids:
        offer_exists = check_offer_exists(client=client, offer_id=offer_id)

        if offer_exists:
            offer_ids_to_delete.append(offer_id)

    if len(offer_ids_to_delete) > 0:
        _process_deleting(client=client, offer_ids_to_delete=offer_ids_to_delete)


def _build_offer_details_to_be_indexed(offer: Offer) -> dict:
    stocks = offer.activeStocks
    event_dates = []
    prices = list(map(lambda stock: float(stock.price), stocks))

    if offer.isEvent:
        event_dates = list(map(lambda stock: datetime.timestamp(stock.beginningDatetime), stocks))

    return {"name": offer.name, "dates": event_dates, "prices": prices}


def _process_adding(pipeline: Pipeline, client: Redis, offer_ids: List[int], adding_objects: List[dict]) -> None:
    try:
        add_objects(objects=adding_objects)
        logger.info(f"[ALGOLIA] {len(adding_objects)} objects were indexed!")
        pipeline.execute()
        pipeline.reset()
    except AlgoliaException as error:
        logger.exception(f"[ALGOLIA] error when adding objects {error}")
        add_offer_ids_in_error(client=client, offer_ids=offer_ids)
        pipeline.reset()
        pass


def _process_deleting(client: Redis, offer_ids_to_delete: List[int]) -> None:
    humanized_offer_ids_to_delete = [humanize(offer_id) for offer_id in offer_ids_to_delete]
    try:
        delete_objects(object_ids=humanized_offer_ids_to_delete)
        delete_indexed_offers(client=client, offer_ids=offer_ids_to_delete)
        logger.info(f"[ALGOLIA] {len(offer_ids_to_delete)} objects were deleted from index!")
    except AlgoliaException as error:
        logger.exception(f"[ALGOLIA] error when deleting objects {error}")
        add_offer_ids_in_error(client=client, offer_ids=offer_ids_to_delete)

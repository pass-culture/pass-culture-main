from typing import List, Set, Tuple

from algolia.api import add_objects, clear_objects, delete_objects
from algolia.builder import build_object
from algolia.rules_engine import is_eligible_for_indexing
from repository import offer_queries
from utils.human_ids import humanize
from utils.logger import logger


def orchestrate_from_offer(offer_ids: List[int],
                           is_clear: bool = False,
                           indexed_offer_ids: Set = None) -> Tuple[List[int], List[int]]:
    if is_clear:
        clear_objects()
    indexing_offer_ids = []
    deleting_offer_ids = []
    indexing_objects = []
    deleting_objects = []
    offers = offer_queries.get_offers_by_ids(offer_ids)

    for offer in offers:
        if is_eligible_for_indexing(offer):
            indexing_objects.append(build_object(offer=offer))
            indexing_offer_ids.append(offer.id)
        else:
            if offer.id in indexed_offer_ids:
                deleting_objects.append(humanize(offer.id))
                deleting_offer_ids.append(offer.id)

    if len(indexing_objects) > 0:
        add_objects(objects=indexing_objects)
        logger.info(f'[ALGOLIA] indexed {len(indexing_objects)} objects')

    if len(deleting_objects) > 0:
        delete_objects(object_ids=deleting_objects)
        logger.info(f'[ALGOLIA] deleted {len(deleting_objects)} objects')

    return indexing_offer_ids, deleting_offer_ids


def orchestrate_from_venue_provider(offer_ids: List[int],
                                    indexed_offer_ids: Set = None) -> Tuple[List[int], List[int]]:
    indexing_offer_ids = []
    deleting_offer_ids = []
    indexing_objects = []
    deleting_objects = []
    offers = offer_queries.get_offers_by_ids(offer_ids)

    for offer in offers:
        if is_eligible_for_indexing(offer):
            if offer.id not in indexed_offer_ids:
                indexing_objects.append(build_object(offer=offer))
                indexing_offer_ids.append(offer.id)
        else:
            if offer.id in indexed_offer_ids:
                deleting_objects.append(humanize(offer.id))
                deleting_offer_ids.append(offer.id)

    if len(indexing_objects) > 0:
        add_objects(objects=indexing_objects)
        logger.info(f'[ALGOLIA] indexed {len(indexing_objects)} objects')

    if len(deleting_objects) > 0:
        delete_objects(object_ids=deleting_objects)
        logger.info(f'[ALGOLIA] deleted {len(deleting_objects)} objects from index')

    return indexing_offer_ids, deleting_offer_ids


def orchestrate_delete_expired_offers(offer_ids: List[int]) -> None:
    deleting_objects = []
    for offer_id in offer_ids:
        deleting_objects.append(humanize(offer_id))

    if len(deleting_objects) > 0:
        delete_objects(object_ids=deleting_objects)
        logger.info(f'[ALGOLIA] deleted {len(deleting_objects)} objects from index')

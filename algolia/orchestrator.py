from typing import List

from algolia.api import add_objects, delete_objects
from algolia.builder import build_object
from algolia.rules_engine import is_eligible_for_indexing
from repository import offer_queries
from utils.human_ids import humanize
from utils.logger import logger


def orchestrate(offer_ids: List[int]) -> None:
    indexing_object = []
    deleting_object = []
    indexing_ids = []
    deleting_ids = []
    offers = offer_queries.get_offers_by_ids(offer_ids)

    for offer in offers:
        humanize_offer_id = humanize(offer.id)
        algolia_object = build_object(offer=offer)

        if is_eligible_for_indexing(offer):
            indexing_object.append(algolia_object)
            indexing_ids.append(humanize_offer_id)
        else:
            deleting_object.append(humanize_offer_id)
            deleting_ids.append(humanize_offer_id)

    if len(indexing_object) > 0:
        add_objects(objects=indexing_object)
        logger.info(f'Indexing {len(indexing_ids)} objectsID: {indexing_ids}')

    if len(deleting_object) > 0:
        delete_objects(object_ids=deleting_object)
        logger.info(f'Deleting {len(deleting_ids)} objectsID: {deleting_ids}')

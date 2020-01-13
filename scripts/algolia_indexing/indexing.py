from typing import List

from redis import Redis

from algolia.orchestrator import orchestrate
from connectors.redis import get_offer_ids, delete_offer_ids
from models import Offer
from repository.offer_queries import get_paginated_offer_ids
from utils.logger import logger


def indexing(limit: int = 1) -> None:
    offer_ids = []
    offers = Offer.query.limit(limit)

    for offer in offers:
        offer_ids.append(offer.id)

    orchestrate(offer_ids=offer_ids)


def indexing_offers_in_algolia(client: Redis) -> None:
    offer_ids = get_offer_ids(client=client)
    orchestrate(offer_ids=offer_ids)
    delete_offer_ids(client=client)


def batch_indexing_offers_in_algolia(limit: int = 10000) -> None:
    page = 0
    has_still_offers = True

    while has_still_offers:
        offer_ids_as_tuple = get_paginated_offer_ids(limit, page)
        offer_ids_as_int = _converter(offer_ids_as_tuple)

        if len(offer_ids_as_int) > 0:
            orchestrate(offer_ids=offer_ids_as_int)
            logger.info(f'[ALGOLIA] Indexing offers from page {page}...')
        else:
            has_still_offers = False
            logger.info('[ALGOLIA] Indexing offers finished!')
        page += 1


def _converter(offer_ids: List[tuple]) -> List[int]:
    return [offer[0] for offer in offer_ids]

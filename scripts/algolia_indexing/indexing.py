from typing import List

from redis import Redis

from algolia.orchestrator import orchestrate, orchestrate_from_local_providers
from connectors.redis import get_offer_ids_from_redis, delete_offer_ids_from_redis, get_venue_ids, delete_venue_ids, \
    get_venue_providers_from_redis, delete_venue_providers_from_redis
from repository.offer_queries import get_paginated_offer_ids
from repository.offer_queries import get_paginated_offer_ids_for_venue_id
from utils.logger import logger


def indexing_offers_in_algolia(client: Redis) -> None:
    offer_ids = get_offer_ids_from_redis(client=client)
    orchestrate(offer_ids=offer_ids)
    delete_offer_ids_from_redis(client=client)


def batch_indexing_offers_in_algolia_by_venue_ids(client: Redis, limit: int = 10000) -> None:
    venue_ids = get_venue_ids(client=client)
    for venue_id in venue_ids:
        page = 0
        has_still_offers = True
        while has_still_offers:
            offer_ids_as_tuple = get_paginated_offer_ids_for_venue_id(venue_id, limit, page)
            offer_ids_as_int = _converter(offer_ids_as_tuple)
            if len(offer_ids_as_int) > 0:
                orchestrate(offer_ids=offer_ids_as_int)
                logger.info(f'[ALGOLIA] Indexing offers for venue {venue_id} from page {page}...')
            else:
                has_still_offers = False
                logger.info(f'[ALGOLIA] Indexing offers for venue {venue_id} finished!')
            page += 1

    delete_venue_ids(client=client)


def indexing_offers_in_algolia_from_local_providers(client: Redis) -> None:
    venue_providers = get_venue_providers_from_redis(client=client)
    orchestrate_from_local_providers(venue_providers=venue_providers)
    delete_venue_providers_from_redis(client=client)


def batch_indexing_offers_in_algolia_from_database(limit: int = 10000) -> None:
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

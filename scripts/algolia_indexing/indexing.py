import os

from redis import Redis

from algolia.orchestrator import orchestrate, orchestrate_from_venue_providers, orchestrate_delete_expired_offers
from connectors.redis import get_offer_ids, delete_offer_ids, get_venue_ids, delete_venue_ids, \
    get_venue_providers, delete_venue_providers
from repository import offer_queries
from utils.converter import from_tuple_to_int
from utils.logger import logger

ALGOLIA_DELETING_OFFERS_CHUNK_SIZE = int(os.environ.get('ALGOLIA_DELETING_OFFERS_CHUNK_SIZE', '10000'))
ALGOLIA_OFFERS_BY_VENUE_CHUNK_SIZE = int(os.environ.get('ALGOLIA_OFFERS_BY_VENUE_CHUNK_SIZE', '10000'))


def batch_indexing_offers_in_algolia_by_offer(client: Redis) -> None:
    offer_ids = get_offer_ids(client=client)
    orchestrate(offer_ids=offer_ids)
    delete_offer_ids(client=client)


def batch_indexing_offers_in_algolia_by_venue(client: Redis) -> None:
    venue_ids = get_venue_ids(client=client)
    for venue_id in venue_ids:
        page = 0
        has_still_offers = True
        while has_still_offers:
            offer_ids_as_tuple = offer_queries.get_paginated_offer_ids_by_venue_id(
                limit=ALGOLIA_OFFERS_BY_VENUE_CHUNK_SIZE,
                page=page,
                venue_id=venue_id
            )
            offer_ids_as_int = from_tuple_to_int(offer_ids_as_tuple)

            if len(offer_ids_as_int) > 0:
                orchestrate(offer_ids=offer_ids_as_int)
                logger.info(f'[ALGOLIA] Indexing offers for venue {venue_id} from page {page}...')
            else:
                has_still_offers = False
                logger.info(f'[ALGOLIA] Indexing offers for venue {venue_id} finished!')
            page += 1

    delete_venue_ids(client=client)


def batch_indexing_offers_in_algolia_by_venue_provider(client: Redis) -> None:
    venue_providers = get_venue_providers(client=client)
    orchestrate_from_venue_providers(venue_providers=venue_providers)
    delete_venue_providers(client=client)


def batch_indexing_offers_in_algolia_from_database(limit: int = 10000, page: int = 0) -> None:
    has_still_offers = True
    page_number = page
    while has_still_offers:
        offer_ids_as_tuple = offer_queries.get_paginated_active_offer_ids(limit=limit, page=page_number)
        offer_ids_as_int = from_tuple_to_int(offer_ids=offer_ids_as_tuple)

        if len(offer_ids_as_int) > 0:
            orchestrate(offer_ids=offer_ids_as_int)
            logger.info(f'[ALGOLIA] Indexing offers from page {page_number}...')
        else:
            has_still_offers = False
            logger.info('[ALGOLIA] Indexing offers finished!')
        page_number += 1


def batch_deleting_expired_offers_in_algolia() -> None:
    page = 0
    has_still_offers = True
    while has_still_offers:
        expired_offer_ids_as_tuple = offer_queries.get_paginated_expired_offer_ids(
            limit=ALGOLIA_DELETING_OFFERS_CHUNK_SIZE,
            page=page
        )
        expired_offer_ids_as_int = from_tuple_to_int(offer_ids=expired_offer_ids_as_tuple)

        if len(expired_offer_ids_as_int) > 0:
            orchestrate_delete_expired_offers(offer_ids=expired_offer_ids_as_int)
            logger.info(f'[ALGOLIA] delete offers from page {page}...')
        else:
            has_still_offers = False
            logger.info('[ALGOLIA] delete offers finished!')
        page += 1

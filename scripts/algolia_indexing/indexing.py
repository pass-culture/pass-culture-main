import os

from redis import Redis

from algolia.usecase.orchestrator import process_eligible_offers, delete_expired_offers
from connectors.redis import get_venue_ids, delete_venue_ids, \
    get_venue_providers, delete_venue_providers, get_offer_ids
from repository import offer_queries
from utils.converter import from_tuple_to_int
from utils.logger import logger

ALGOLIA_DELETING_OFFERS_CHUNK_SIZE = int(os.environ.get('ALGOLIA_DELETING_OFFERS_CHUNK_SIZE', 10000))
ALGOLIA_OFFERS_BY_VENUE_CHUNK_SIZE = int(os.environ.get('ALGOLIA_OFFERS_BY_VENUE_CHUNK_SIZE', 10000))
ALGOLIA_OFFERS_BY_VENUE_PROVIDER_CHUNK_SIZE = int(os.environ.get('ALGOLIA_OFFERS_BY_VENUE_PROVIDER_CHUNK_SIZE', 10000))


def batch_indexing_offers_in_algolia_by_offer(client: Redis) -> None:
    offer_ids = get_offer_ids(client=client)

    if len(offer_ids) > 0:
        process_eligible_offers(client=client, offer_ids=offer_ids, from_provider_update=False)


def batch_indexing_offers_in_algolia_by_venue_provider(client: Redis) -> None:
    venue_providers = get_venue_providers(client=client)

    if len(venue_providers) > 0:
        delete_venue_providers(client=client)
        for venue_provider in venue_providers:
            provider_id = venue_provider['providerId']
            venue_id = int(venue_provider['venueId'])
            _process_venue_provider(client, provider_id, venue_id)


def batch_indexing_offers_in_algolia_by_venue(client: Redis) -> None:
    venue_ids = get_venue_ids(client=client)

    if len(venue_ids) > 0:
        delete_venue_ids(client=client)
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
                    process_eligible_offers(client=client, offer_ids=offer_ids_as_int, from_provider_update=False)
                    logger.info(f'[ALGOLIA] indexing offers for venue {venue_id} from page {page}...')
                else:
                    has_still_offers = False
                    logger.info(f'[ALGOLIA] indexing offers for venue {venue_id} finished!')
                page += 1


def batch_indexing_offers_in_algolia_from_database(client: Redis, limit: int = 10000, page: int = 0) -> None:
    page_number = page
    has_still_offers = True

    while has_still_offers:
        offer_ids_as_tuple = offer_queries.get_paginated_active_offer_ids(limit=limit, page=page_number)
        offer_ids_as_int = from_tuple_to_int(offer_ids=offer_ids_as_tuple)

        if len(offer_ids_as_int) > 0:
            process_eligible_offers(client=client, offer_ids=offer_ids_as_int, from_provider_update=False)
            logger.info(f'[ALGOLIA] indexing offers of database from page {page_number}...')
        else:
            has_still_offers = False
            logger.info('[ALGOLIA] indexing offers of database finished!')
        page_number += 1


def batch_deleting_expired_offers_in_algolia(client: Redis) -> None:
    page = 0
    has_still_offers = True

    while has_still_offers:
        expired_offer_ids_as_tuple = offer_queries.get_paginated_expired_offer_ids(
            limit=ALGOLIA_DELETING_OFFERS_CHUNK_SIZE,
            page=page
        )
        expired_offer_ids_as_int = from_tuple_to_int(offer_ids=expired_offer_ids_as_tuple)

        if len(expired_offer_ids_as_int) > 0:
            delete_expired_offers(client=client, offer_ids=expired_offer_ids_as_int)
            logger.info(f'[ALGOLIA] deleted expired offers from page {page}...')
        else:
            has_still_offers = False
            logger.info('[ALGOLIA] deleting expired offers finished!')
        page += 1


def _process_venue_provider(client: Redis, provider_id: str, venue_id: int) -> None:
    has_still_offers = True
    page = 0
    while has_still_offers is True:
        offer_ids_as_tuple = offer_queries.get_paginated_offer_ids_by_venue_id_and_last_provider_id(
            last_provider_id=provider_id,
            limit=ALGOLIA_OFFERS_BY_VENUE_PROVIDER_CHUNK_SIZE,
            page=page,
            venue_id=venue_id
        )
        offer_ids_as_int = from_tuple_to_int(offer_ids_as_tuple)

        if len(offer_ids_as_tuple) > 0:
            process_eligible_offers(client=client, offer_ids=offer_ids_as_int, from_provider_update=True)
            logger.info(
                f'[ALGOLIA] indexing offers for (venue {venue_id} / provider {provider_id}) from page {page}...')
            page += 1
        else:
            has_still_offers = False
            logger.info(
                f'[ALGOLIA] indexing offers for (venue {venue_id} / provider {provider_id}) finished!')

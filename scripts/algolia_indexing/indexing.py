import os

from redis import Redis

from algolia.orchestrator import orchestrate_from_offer, orchestrate_delete_expired_offers, \
    orchestrate_from_venue_provider
from connectors.redis import get_offer_ids, delete_offer_ids, get_venue_ids, delete_venue_ids, \
    get_venue_providers, delete_venue_providers, get_offer_ids_from_set, delete_offer_ids_from_set, add_offer_ids_to_set
from repository import offer_queries
from utils.converter import from_tuple_to_int
from utils.logger import logger

ALGOLIA_DELETING_OFFERS_CHUNK_SIZE = int(os.environ.get('ALGOLIA_DELETING_OFFERS_CHUNK_SIZE', 10000))
ALGOLIA_OFFERS_BY_VENUE_CHUNK_SIZE = int(os.environ.get('ALGOLIA_OFFERS_BY_VENUE_CHUNK_SIZE', 10000))
ALGOLIA_OFFERS_BY_VENUE_PROVIDER_CHUNK_SIZE = int(os.environ.get('ALGOLIA_OFFERS_BY_VENUE_PROVIDER_CHUNK_SIZE', 10000))


def batch_indexing_offers_in_algolia_by_offer(client: Redis) -> None:
    offer_ids = get_offer_ids(client=client)
    indexed_offer_ids = get_offer_ids_from_set(client=client)
    indexing_offer_ids, deleting_offer_ids = orchestrate_from_offer(offer_ids=offer_ids,
                                                                    indexed_offer_ids=indexed_offer_ids)
    if len(indexing_offer_ids) > 0:
        add_offer_ids_to_set(client=client, offer_ids=indexing_offer_ids)
    if len(deleting_offer_ids) > 0:
        delete_offer_ids_from_set(client=client, offer_ids=deleting_offer_ids)
    delete_offer_ids(client=client)


def batch_indexing_offers_in_algolia_by_venue_provider(client: Redis) -> None:
    venue_providers = get_venue_providers(client=client)
    indexed_offer_ids = get_offer_ids_from_set(client=client)

    for venue_provider in venue_providers:
        has_still_offers = True
        page = 0
        while has_still_offers is True:
            provider_id = venue_provider['providerId']
            venue_id = int(venue_provider['venueId'])
            offer_ids_as_tuple = offer_queries.get_paginated_offer_ids_by_venue_id_and_last_provider_id(
                last_provider_id=provider_id,
                limit=ALGOLIA_OFFERS_BY_VENUE_PROVIDER_CHUNK_SIZE,
                page=page,
                venue_id=venue_id
            )
            offer_ids_as_int = from_tuple_to_int(offer_ids_as_tuple)

            if len(offer_ids_as_tuple) > 0:
                indexing_offer_ids, deleting_offer_ids = orchestrate_from_venue_provider(offer_ids=offer_ids_as_int,
                                                                                         indexed_offer_ids=indexed_offer_ids)

                if len(indexing_offer_ids) > 0:
                    add_offer_ids_to_set(client=client, offer_ids=indexing_offer_ids)
                if len(deleting_offer_ids) > 0:
                    print('heyhey')
                    print(deleting_offer_ids)
                    delete_offer_ids_from_set(client=client, offer_ids=deleting_offer_ids)
                page += 1
            else:
                has_still_offers = False
    delete_venue_providers(client=client)


def batch_indexing_offers_in_algolia_by_venue(client: Redis) -> None:
    venue_ids = get_venue_ids(client=client)
    indexed_offer_ids = get_offer_ids_from_set(client=client)

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
                indexing_offer_ids, deleting_offer_ids = orchestrate_from_offer(offer_ids=offer_ids_as_int,
                                                                                indexed_offer_ids=indexed_offer_ids)
                if len(indexing_offer_ids) > 0:
                    add_offer_ids_to_set(client=client, offer_ids=indexing_offer_ids)
                if len(deleting_offer_ids) > 0:
                    delete_offer_ids_from_set(client=client, offer_ids=deleting_offer_ids)
                logger.info(f'[ALGOLIA] Indexing offers for venue {venue_id} from page {page}...')
            else:
                has_still_offers = False
                logger.info(f'[ALGOLIA] Indexing offers for venue {venue_id} finished!')
            page += 1

    delete_venue_ids(client=client)


def batch_indexing_offers_in_algolia_from_database(client: Redis, limit: int = 10000, page: int = 0) -> None:
    has_still_offers = True
    page_number = page
    indexed_offer_ids = get_offer_ids_from_set(client=client)

    while has_still_offers:
        offer_ids_as_tuple = offer_queries.get_paginated_active_offer_ids(limit=limit, page=page_number)
        offer_ids_as_int = from_tuple_to_int(offer_ids=offer_ids_as_tuple)

        if len(offer_ids_as_int) > 0:
            indexing_offer_ids, deleting_offer_ids = orchestrate_from_offer(offer_ids=offer_ids_as_int,
                                                                            indexed_offer_ids=indexed_offer_ids)
            if len(indexing_offer_ids) > 0:
                add_offer_ids_to_set(client=client, offer_ids=indexing_offer_ids)
            if len(deleting_offer_ids) > 0:
                delete_offer_ids_from_set(client=client, offer_ids=deleting_offer_ids)
            logger.info(f'[ALGOLIA] Indexing offers from page {page_number}...')
        else:
            has_still_offers = False
            logger.info('[ALGOLIA] Indexing offers finished!')
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
            orchestrate_delete_expired_offers(offer_ids=expired_offer_ids_as_int)
            delete_offer_ids_from_set(client=client, offer_ids=expired_offer_ids_as_int)
            logger.info(f'[ALGOLIA] delete offers from page {page}...')
        else:
            has_still_offers = False
            logger.info('[ALGOLIA] delete offers finished!')
        page += 1

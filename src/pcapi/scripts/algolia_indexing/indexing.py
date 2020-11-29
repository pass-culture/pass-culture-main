from datetime import datetime
from datetime import timedelta
import os

from redis import Redis

from pcapi.algolia.usecase.orchestrator import delete_expired_offers
from pcapi.algolia.usecase.orchestrator import process_eligible_offers
from pcapi.connectors.redis import delete_offer_ids
from pcapi.connectors.redis import delete_offer_ids_in_error
from pcapi.connectors.redis import delete_venue_ids
from pcapi.connectors.redis import delete_venue_provider_currently_in_sync
from pcapi.connectors.redis import delete_venue_providers
from pcapi.connectors.redis import get_offer_ids
from pcapi.connectors.redis import get_offer_ids_in_error
from pcapi.connectors.redis import get_venue_ids
from pcapi.connectors.redis import get_venue_providers
from pcapi.repository import offer_queries
from pcapi.utils.converter import from_tuple_to_int
from pcapi.utils.logger import logger


ALGOLIA_DELETING_OFFERS_CHUNK_SIZE = int(os.environ.get("ALGOLIA_DELETING_OFFERS_CHUNK_SIZE", 10000))
ALGOLIA_OFFERS_BY_VENUE_CHUNK_SIZE = int(os.environ.get("ALGOLIA_OFFERS_BY_VENUE_CHUNK_SIZE", 10000))
ALGOLIA_OFFERS_BY_VENUE_PROVIDER_CHUNK_SIZE = int(os.environ.get("ALGOLIA_OFFERS_BY_VENUE_PROVIDER_CHUNK_SIZE", 10000))


def batch_indexing_offers_in_algolia_by_offer(client: Redis) -> None:
    offer_ids = get_offer_ids(client=client)

    if len(offer_ids) > 0:
        logger.info("[ALGOLIA] processing %i offers...", len(offer_ids))
        process_eligible_offers(client=client, offer_ids=offer_ids, from_provider_update=False)
        delete_offer_ids(client=client)
        logger.info("[ALGOLIA] %i offers processed!", len(offer_ids))


def batch_indexing_offers_in_algolia_by_venue_provider(client: Redis) -> None:
    venue_providers = get_venue_providers(client=client)

    if len(venue_providers) > 0:
        delete_venue_providers(client=client)
        for venue_provider in venue_providers:
            venue_provider_id = venue_provider["id"]
            provider_id = venue_provider["providerId"]
            venue_id = int(venue_provider["venueId"])
            _process_venue_provider(
                client=client, provider_id=provider_id, venue_id=venue_id, venue_provider_id=venue_provider_id
            )


def batch_indexing_offers_in_algolia_by_venue(client: Redis) -> None:
    venue_ids = get_venue_ids(client=client)

    if len(venue_ids) > 0:
        for venue_id in venue_ids:
            page = 0
            has_still_offers = True

            while has_still_offers:
                offer_ids_as_tuple = offer_queries.get_paginated_offer_ids_by_venue_id(
                    limit=ALGOLIA_OFFERS_BY_VENUE_CHUNK_SIZE, page=page, venue_id=venue_id
                )
                offer_ids_as_int = from_tuple_to_int(offer_ids_as_tuple)

                if len(offer_ids_as_int) > 0:
                    logger.info("[ALGOLIA] processing offers for venue %s from page %s...", venue_id, page)
                    process_eligible_offers(client=client, offer_ids=offer_ids_as_int, from_provider_update=False)
                    logger.info("[ALGOLIA] offers for venue %s from page %s processed!", venue_id, page)
                else:
                    has_still_offers = False
                    logger.info("[ALGOLIA] processing of offers for venue %s finished!", venue_id)
                page += 1
        delete_venue_ids(client=client)


def batch_indexing_offers_in_algolia_from_database(
    client: Redis, ending_page: int = None, limit: int = 10000, starting_page: int = 0
) -> None:
    page_number = starting_page
    has_still_offers = True

    while has_still_offers:
        if ending_page:
            if ending_page == page_number:
                break

        offer_ids_as_tuple = offer_queries.get_paginated_active_offer_ids(limit=limit, page=page_number)
        offer_ids_as_int = from_tuple_to_int(offer_ids=offer_ids_as_tuple)

        if len(offer_ids_as_int) > 0:
            logger.info("[ALGOLIA] processing offers of database from page %s...", page_number)
            process_eligible_offers(client=client, offer_ids=offer_ids_as_int, from_provider_update=False)
            logger.info("[ALGOLIA] offers of database from page %s processed!", page_number)
        else:
            has_still_offers = False
            logger.info("[ALGOLIA] processing of offers from database finished!")
        page_number += 1


def batch_deleting_expired_offers_in_algolia(client: Redis, process_all_expired: bool = False) -> None:
    page = 0
    has_still_offers = True
    one_day_before_now = datetime.utcnow() - timedelta(days=1)
    two_days_before_now = datetime.utcnow() - timedelta(days=2)
    arbitrary_oldest_date = datetime(2000, 1, 1)
    from_date = two_days_before_now if not process_all_expired else arbitrary_oldest_date

    while has_still_offers:
        expired_offer_ids_as_tuple = offer_queries.get_paginated_offer_ids_given_booking_limit_datetime_interval(
            limit=ALGOLIA_DELETING_OFFERS_CHUNK_SIZE, page=page, from_date=from_date, to_date=one_day_before_now
        )
        expired_offer_ids_as_int = from_tuple_to_int(offer_ids=expired_offer_ids_as_tuple)

        if len(expired_offer_ids_as_int) > 0:
            logger.info("[ALGOLIA] processing deletion of expired offers from page %s...", page)
            delete_expired_offers(client=client, offer_ids=expired_offer_ids_as_int)
            logger.info("[ALGOLIA] expired offers from page %s processed!", page)
        else:
            has_still_offers = False
            logger.info("[ALGOLIA] deleting expired offers finished!")
        page += 1


def batch_processing_offer_ids_in_error(client: Redis):
    offer_ids_in_error = get_offer_ids_in_error(client=client)
    if len(offer_ids_in_error) > 0:
        process_eligible_offers(client=client, offer_ids=offer_ids_in_error, from_provider_update=False)
        delete_offer_ids_in_error(client=client)


def _process_venue_provider(client: Redis, provider_id: str, venue_provider_id: int, venue_id: int) -> None:
    has_still_offers = True
    page = 0
    try:
        while has_still_offers is True:
            offer_ids_as_tuple = offer_queries.get_paginated_offer_ids_by_venue_id_and_last_provider_id(
                last_provider_id=provider_id,
                limit=ALGOLIA_OFFERS_BY_VENUE_PROVIDER_CHUNK_SIZE,
                page=page,
                venue_id=venue_id,
            )
            offer_ids_as_int = from_tuple_to_int(offer_ids_as_tuple)

            if len(offer_ids_as_tuple) > 0:
                logger.info(
                    "[ALGOLIA] processing offers for (venue %s / provider %s) from page %s...",
                    venue_id,
                    provider_id,
                    page,
                )
                process_eligible_offers(client=client, offer_ids=offer_ids_as_int, from_provider_update=True)
                logger.info(
                    "[ALGOLIA] offers for (venue %s / provider %s) from page %s processed",
                    venue_id,
                    provider_id,
                    page,
                )
                page += 1
            else:
                has_still_offers = False
                logger.info(
                    "[ALGOLIA] processing of offers for (venue %s / provider %s) finished!", venue_id, provider_id
                )
    except Exception as error:
        logger.exception(
            "[ALGOLIA] processing of offers for (venue %s / provider %s) failed! %s",
            venue_id,
            provider_id,
            error,
        )
    finally:
        delete_venue_provider_currently_in_sync(client=client, venue_provider_id=venue_provider_id)

import datetime
import logging

from redis import Redis

from pcapi import settings
from pcapi.algolia.usecase.orchestrator import delete_expired_offers
from pcapi.algolia.usecase.orchestrator import process_eligible_offers
from pcapi.connectors.redis import RedisBucket
from pcapi.connectors.redis import delete_offer_ids_in_error
from pcapi.connectors.redis import delete_venue_ids
from pcapi.connectors.redis import get_offer_ids_in_error
from pcapi.connectors.redis import get_venue_ids
from pcapi.connectors.redis import pop_offer_ids
from pcapi.core.offers.models import Offer
import pcapi.core.offers.repository as offers_repository
from pcapi.repository import offer_queries
from pcapi.utils.converter import from_tuple_to_int


logger = logging.getLogger(__name__)


def batch_indexing_offers_in_algolia_by_offer(client: Redis, stop_only_when_empty=False) -> None:
    """Reindex offers.

    If `stop_only_when_empty` is False (i.e. if called as a cron
    command), we pop from the queue at least once, and stop when there
    is less than REDIS_OFFER_IDS_CHUNK_SIZE in the queue (otherwise
    the cron job may never stop). It means that a cron job may run for
    a long time if the queue has many items. In fact, a subsequent
    cron job may run in parallel if the previous one has not finished.
    It's fine because they both pop from the queue.

    If `stop_only_when_empty` is True (i.e. if called from the
    `process_offers` Flask command), we pop from the queue and stop
    only when the queue is empty.
    """
    while True:
        # We must pop and not get-and-delete. Otherwise two concurrent
        # cron jobs could delete the wrong offers from the queue:
        # 1. Cron job 1 gets the first 1.000 offers from the queue.
        # 2. Cron job 2 gets the same 1.000 offers from the queue.
        # 3. Cron job 1 finishes processing the batch and deletes the
        #    first 1.000 offers from the queue. OK.
        # 4. Cron job 2 finishes processing the batch and also deletes
        #    the first 1.000 offers from the queue. Not OK, these are
        #    not the same offers it just processed!
        offer_ids = pop_offer_ids(client=client)
        if not offer_ids:
            break

        logger.info("[ALGOLIA] processing %i offers...", len(offer_ids))
        try:
            process_eligible_offers(client=client, offer_ids=offer_ids, from_provider_update=False)
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception(
                "Exception while reindexing offers, must fix manually",
                extra={
                    "exc": str(exc),
                    "offer_ids": offer_ids,
                },
            )
        logger.info("[ALGOLIA] %i offers processed!", len(offer_ids))

        left_to_process = client.llen(RedisBucket.REDIS_LIST_OFFER_IDS_NAME.value)
        if not stop_only_when_empty and left_to_process < settings.REDIS_OFFER_IDS_CHUNK_SIZE:
            break


def batch_indexing_offers_in_algolia_by_venue(client: Redis) -> None:
    venue_ids = get_venue_ids(client=client)

    if len(venue_ids) > 0:
        for venue_id in venue_ids:
            page = 0
            has_still_offers = True

            while has_still_offers:
                offer_ids_as_tuple = offer_queries.get_paginated_offer_ids_by_venue_id(
                    limit=settings.ALGOLIA_OFFERS_BY_VENUE_CHUNK_SIZE, page=page, venue_id=venue_id
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
    """Request an asynchronous unindex of offers that have expired within
    the last 2 days.

    For example, if run on Thursday (whatever the time), this function
    handles offers that have expired between Tuesday 00:00 and
    Wednesday 23:59 (included).
    """
    start_of_day = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
    interval = [start_of_day - datetime.timedelta(days=2), start_of_day]
    if process_all_expired:
        interval[0] = datetime.datetime(2000, 1, 1)  # arbitrary old date

    page = 0
    limit = settings.ALGOLIA_DELETING_OFFERS_CHUNK_SIZE
    while True:
        offers = offers_repository.get_expired_offers(interval)
        offers = offers.offset(page * limit).limit(limit)
        offer_ids = [offer_id for offer_id, in offers.with_entities(Offer.id)]

        if not offer_ids:
            break

        logger.info("[ALGOLIA] Found %d expired offers to unindex", len(offer_ids))
        delete_expired_offers(client=client, offer_ids=offer_ids)
        page += 1


def batch_processing_offer_ids_in_error(client: Redis):
    offer_ids_in_error = get_offer_ids_in_error(client=client)
    if len(offer_ids_in_error) > 0:
        process_eligible_offers(client=client, offer_ids=offer_ids_in_error, from_provider_update=False)
        delete_offer_ids_in_error(client=client)

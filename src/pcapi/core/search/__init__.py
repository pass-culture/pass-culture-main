import logging
from typing import Iterable

from pcapi import settings
from pcapi.core.search.backends import base
from pcapi.models import Offer
from pcapi.models import Venue
from pcapi.repository import offer_queries
from pcapi.utils.module_loading import import_string


logger = logging.getLogger(__name__)


# FIXME (dbaty, 2021-06-24): during the migration, we'll have a double
# run with two backends on prod. Once it's done, there will be one and
# only one backend and we can:
# - rename `_get_backends()` as `_get_backend()`;
# - simplify code by merging wrapper methods and private methods (that
#   start with `_`);
# - remove `backend` from "extra" log argument
def _get_backends() -> list[base.SearchBackend]:
    backend_classes = [import_string(path) for path in settings.SEARCH_BACKEND.split(",")]
    return [backend_class() for backend_class in backend_classes]


def async_index_offer_ids(offer_ids: Iterable[int]) -> None:
    """Ask for an asynchronous reindexation of the given list of
    ``Offer.id``.

    This function returns quickly. The "real" reindexation will be
    done later through a cron job.
    """
    backends = _get_backends()
    for backend in backends:
        try:
            backend.enqueue_offer_ids(offer_ids)
        except Exception:  # pylint: disable=broad-except
            if settings.IS_RUNNING_TESTS:
                raise
            logger.exception(
                "Could not enqueue offer ids to index", extra={"offers": offer_ids, "backend": str(backend)}
            )


def async_index_venue_ids(venue_ids: Iterable[int]) -> None:
    """Ask for an asynchronous reindexation of the given list of
    ``Venue.id``.

    This function returns quickly. The "real" reindexation will be
    done later through a cron job.
    """
    backends = _get_backends()
    for backend in backends:
        try:
            backend.enqueue_venue_ids(venue_ids)
        except Exception:  # pylint: disable=broad-except
            if settings.IS_RUNNING_TESTS:
                raise
            logger.exception(
                "Could not enqueue venue ids to index", extra={"venues": venue_ids, "backend": str(backend)}
            )


def async_index_offers_of_venue_ids(venue_ids: Iterable[int]) -> None:
    """Ask for an asynchronous reindexation of the offers attached to venues
    from the list of ``Venue.id``.

    This function returns quickly. The "real" reindexation will be
    done later through a cron job.
    """
    backends = _get_backends()
    for backend in backends:
        try:
            backend.enqueue_venue_ids_for_offers(venue_ids)
        except Exception:  # pylint: disable=broad-except
            if settings.IS_RUNNING_TESTS:
                raise
            logger.exception(
                "Could not enqueue venue ids to index their offers",
                extra={"venues": venue_ids, "backend": str(backend)},
            )


def index_offers_in_queue(stop_only_when_empty: bool = False, from_error_queue: bool = False) -> None:
    """Pop offers from indexation queue and reindex them.

    If ``from_error_queue`` is True, pop offers from the error queue
    instead of the "standard" indexation queue.

    If ``stop_only_when_empty`` is False (i.e. if called as a cron
    command), we pop from the queue at least once, and stop when there
    is less than REDIS_OFFER_IDS_CHUNK_SIZE in the queue (otherwise
    the cron job may never stop). It means that a cron job may run for
    a long time if the queue has many items. In fact, a subsequent
    cron job may run in parallel if the previous one has not finished.
    It's fine because they both pop from the queue.

    If ``stop_only_when_empty`` is True (i.e. if called from the
    ``process_offers`` Flask command), we pop from the queue and stop
    only when the queue is empty.
    """
    backends = _get_backends()
    for backend in backends:
        try:
            _index_offers_in_queue(
                backend, stop_only_when_empty=stop_only_when_empty, from_error_queue=from_error_queue
            )
        except Exception:  # pylint: disable=broad-except
            if settings.IS_RUNNING_TESTS:
                raise
            logger.exception("Could not index offers from queue", extra={"backend": str(backend)})


def _index_offers_in_queue(
    backend: base.SearchBackend, stop_only_when_empty: bool = False, from_error_queue: bool = False
) -> None:
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
        offer_ids = backend.pop_offer_ids_from_queue(
            count=settings.REDIS_OFFER_IDS_CHUNK_SIZE, from_error_queue=from_error_queue
        )
        if not offer_ids:
            break

        logger.info("Fetched offers from indexation queue", extra={"count": len(offer_ids), "backend": str(backend)})
        try:
            _reindex_offer_ids(backend, offer_ids)
        except Exception as exc:  # pylint: disable=broad-except
            if settings.IS_RUNNING_TESTS:
                raise
            logger.exception(
                "Exception while reindexing offers, must fix manually",
                extra={
                    "exc": str(exc),
                    "offers": offer_ids,
                    "backend": str(backend),
                },
            )
        else:
            logger.info(
                "Reindexed offers from queue",
                extra={"count": len(offer_ids), "from_error_queue": from_error_queue, "backend": str(backend)},
            )

        left_to_process = backend.count_offers_to_index_from_queue(from_error_queue=from_error_queue)
        if not stop_only_when_empty and left_to_process < settings.REDIS_OFFER_IDS_CHUNK_SIZE:
            break


def index_venues_in_queue() -> None:
    """Pop venues from indexation queue and reindex them."""
    backends = _get_backends()
    for backend in backends:
        try:
            _index_venues_in_queue(backend)
        except Exception as exc:  # pylint: disable=broad-except
            if settings.IS_RUNNING_TESTS:
                raise
            logger.exception("Could not index venues from queue", extra={"backend": str(backend), "exc": str(exc)})


def _index_venues_in_queue(backend: base.SearchBackend) -> None:
    venue_ids = backend.get_venue_ids_from_queue(count=settings.REDIS_VENUE_IDS_CHUNK_SIZE)
    if not venue_ids:
        return

    logger.info("Starting to index venues", extra={"count": len(venue_ids), "backend": str(backend)})

    venues = Venue.query.filter(Venue.id.in_(venue_ids))
    backend.index_venues(venues)

    logger.info("Finished indexing venues", extra={"count": len(venue_ids), "backend": str(backend)})
    backend.delete_venue_ids_from_queue(venue_ids)


def index_offers_of_venues_in_queue() -> None:
    """Pop venues from indexation queue and reindex their offers."""
    backends = _get_backends()
    for backend in backends:
        try:
            _index_offers_of_venues_in_queue(backend)
        except Exception:  # pylint: disable=broad-except
            if settings.IS_RUNNING_TESTS:
                raise
            logger.exception("Could not index offers of venues from queue", extra={"backend": str(backend)})


def _index_offers_of_venues_in_queue(backend: base.SearchBackend) -> None:
    venue_ids = backend.get_venue_ids_for_offers_from_queue(count=settings.REDIS_VENUE_IDS_CHUNK_SIZE)
    for venue_id in venue_ids:
        page = 0
        logger.info("Starting to index offers of venue", extra={"venue": venue_id, "backend": str(backend)})
        while True:
            offer_ids = offer_queries.get_paginated_offer_ids_by_venue_id(
                limit=settings.ALGOLIA_OFFERS_BY_VENUE_CHUNK_SIZE, page=page, venue_id=venue_id
            )
            if not offer_ids:
                break
            _reindex_offer_ids(backend, offer_ids)
            page += 1
        logger.info("Finished indexing offers of venue", extra={"venue": venue_id, "backend": str(backend)})

    backend.delete_venue_ids_for_offers_from_queue(venue_ids)


def reindex_offer_ids(offer_ids: Iterable[int]) -> None:
    """Given a list of `Offer.id`, reindex or unindex each offer
    (i.e. request the external indexation service an update or a
    removal).

    This function calls the external indexation service and may thus
    be slow. It should not be called by usual code. You should rather
    call `async_index_offer_ids()` instead to return quickly.
    """
    backends = _get_backends()
    for backend in backends:
        try:
            _reindex_offer_ids(backend, offer_ids)
        except Exception:  # pylint: disable=broad-except
            if settings.IS_RUNNING_TESTS:
                raise
            logger.exception("Could not reindex offers", extra={"offers": offer_ids, "backend": str(backend)})


def _reindex_offer_ids(backend: base.SearchBackend, offer_ids: Iterable[int]) -> None:
    to_add = []
    to_delete = []
    # FIXME (dbaty, 2021-07-05): join-load Stock, Venue, Offerer,
    # etc. to avoid N+1 queries on each offer. See related comment in
    # test_serialize_appsearch:test_check_number_of_sql_queries
    offers = Offer.query.filter(Offer.id.in_(offer_ids))
    for offer in offers:
        if offer and offer.isBookable:
            to_add.append(offer)
        elif backend.check_offer_is_indexed(offer):
            to_delete.append(offer)
        else:
            # FIXME (dbaty, 2021-06-24). I think we could safely do
            # without the hashmap in Redis. Check the logs and see if
            # I am right!
            logger.info(
                "Redis 'indexed_offers' set avoided unnecessary request to indexation service",
                extra={"source": "reindex_offer_ids", "offer": offer.id, "backend": str(backend)},
            )

    # Handle new or updated available offers
    try:
        backend.index_offers(to_add)
    except Exception as exc:  # pylint: disable=broad-except
        if settings.IS_RUNNING_TESTS:
            raise
        logger.warning(
            "Could not reindex offers, will automatically retry",
            extra={"exc": str(exc), "offers": [offer.id for offer in to_add], "backend": str(backend)},
            exc_info=True,
        )
        backend.enqueue_offer_ids_in_error([offer.id for offer in to_add])

    # Handle unavailable offers (deleted, expired, sold out, etc.)
    try:
        backend.unindex_offer_ids([offer.id for offer in to_delete])
    except Exception as exc:  # pylint: disable=broad-except
        if settings.IS_RUNNING_TESTS:
            raise
        logger.warning(
            "Could not unindex offers, will automatically retry",
            extra={"exc": str(exc), "offers": [offer.id for offer in to_delete], "backend": str(backend)},
            exc_info=True,
        )
        backend.enqueue_offer_ids_in_error([offer.id for offer in to_delete])


def unindex_offer_ids(offer_ids: Iterable[int]) -> None:
    backends = _get_backends()
    for backend in backends:
        try:
            backend.unindex_offer_ids(offer_ids)
        except Exception:  # pylint: disable=broad-except
            if settings.IS_RUNNING_TESTS:
                raise
            logger.exception("Could not unindex offers", extra={"offers": offer_ids, "backend": str(backend)})


def unindex_all_offers() -> None:
    if settings.IS_PROD:
        raise ValueError("It is forbidden to unindex all offers on this environment")
    backends = _get_backends()
    for backend in backends:
        try:
            backend.unindex_all_offers()
        except Exception:  # pylint: disable=broad-except
            if settings.IS_RUNNING_TESTS:
                raise
            logger.exception("Could not unindex all offers", extra={"backend": str(backend)})

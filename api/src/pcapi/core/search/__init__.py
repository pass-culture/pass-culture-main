from collections.abc import Collection
import logging
from typing import Iterable

from sqlalchemy.orm import joinedload

from pcapi import settings
from pcapi.core.educational import models as educational_models
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.models import Offer
from pcapi.core.search.backends import base
from pcapi.models.feature import FeatureToggle
from pcapi.repository import offer_queries
from pcapi.utils.module_loading import import_string


logger = logging.getLogger(__name__)


def _get_backend() -> base.SearchBackend:
    backend_class = import_string(settings.SEARCH_BACKEND)
    return backend_class()


def async_index_offer_ids(offer_ids: Iterable[int]) -> None:
    """Ask for an asynchronous reindexation of the given list of
    ``Offer.id``.

    This function returns quickly. The "real" reindexation will be
    done later through a cron job.
    """
    backend = _get_backend()
    try:
        backend.enqueue_offer_ids(offer_ids)
    except Exception:  # pylint: disable=broad-except
        if settings.IS_RUNNING_TESTS:
            raise
        logger.exception("Could not enqueue offer ids to index", extra={"offers": offer_ids})


def async_index_collective_offer_ids(collective_offer_ids: Iterable[int]) -> None:
    """Ask for an asynchronous reindexation of the given list of
    ``CollectiveOffer.id``.

    This function returns quickly. The "real" reindexation will be
    done later through a cron job.
    """
    backend = _get_backend()
    try:
        backend.enqueue_collective_offer_ids(collective_offer_ids)
    except Exception:  # pylint: disable=broad-except
        if settings.IS_RUNNING_TESTS:
            raise
        logger.exception(
            "Could not enqueue collective offer ids to index",
            extra={
                "collective_offers": collective_offer_ids,
            },
        )


def async_index_collective_offer_template_ids(collective_offer_template_ids: Iterable[int]) -> None:
    """Ask for an asynchronous reindexation of the given list of
    ``CollectiveOfferTemplate.id``.

    This function returns quickly. The "real" reindexation will be
    done later through a cron job.
    """
    backend = _get_backend()
    try:
        backend.enqueue_collective_offer_template_ids(collective_offer_template_ids)
    except Exception:  # pylint: disable=broad-except
        if settings.IS_RUNNING_TESTS:
            raise
        logger.exception(
            "Could not enqueue collective offer template ids to index",
            extra={
                "collective_offer_template_ids": collective_offer_template_ids,
            },
        )


def async_index_venue_ids(venue_ids: Iterable[int]) -> None:
    """Ask for an asynchronous reindexation of the given list of
    permanent ``Venue`` ids.

    This function returns quickly. The "real" reindexation will be
    done later through a cron job.
    """
    backend = _get_backend()
    try:
        backend.enqueue_venue_ids(venue_ids)
    except Exception:  # pylint: disable=broad-except
        if settings.IS_RUNNING_TESTS:
            raise
        logger.exception("Could not enqueue venue ids to index", extra={"venues": venue_ids})


def async_index_offers_of_venue_ids(venue_ids: Iterable[int]) -> None:
    """Ask for an asynchronous reindexation of the offers attached to venues
    from the list of ``Venue.id``.

    This function returns quickly. The "real" reindexation will be
    done later through a cron job.
    """
    backend = _get_backend()
    try:
        backend.enqueue_venue_ids_for_offers(venue_ids)
    except Exception:  # pylint: disable=broad-except
        if settings.IS_RUNNING_TESTS:
            raise
        logger.exception(
            "Could not enqueue venue ids to index their offers",
            extra={"venues": venue_ids},
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
    backend = _get_backend()
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

        logger.info("Fetched offers from indexation queue", extra={"count": len(offer_ids)})
        try:
            reindex_offer_ids(offer_ids)
        except Exception as exc:  # pylint: disable=broad-except
            if settings.IS_RUNNING_TESTS:
                raise
            logger.exception(
                "Exception while reindexing offers, must fix manually",
                extra={"exc": str(exc), "offers": offer_ids},
            )
        else:
            logger.info(
                "Reindexed offers from queue",
                extra={"count": len(offer_ids), "from_error_queue": from_error_queue},
            )

        left_to_process = backend.count_offers_to_index_from_queue(from_error_queue=from_error_queue)
        if not stop_only_when_empty and left_to_process < settings.REDIS_OFFER_IDS_CHUNK_SIZE:
            break


def index_collective_offers_in_queue(from_error_queue: bool = False) -> None:
    """Pop collective offers from indexation queue and reindex them."""
    backend = _get_backend()
    try:
        chunk_size = settings.REDIS_COLLECTIVE_OFFER_IDS_CHUNK_SIZE
        collective_offer_ids = backend.pop_collective_offer_ids_from_queue(
            count=chunk_size,
            from_error_queue=from_error_queue,
        )

        if not collective_offer_ids:
            return

        _reindex_collective_offer_ids(backend, collective_offer_ids)

    except Exception as exc:  # pylint: disable=broad-except
        if settings.IS_RUNNING_TESTS:
            raise
        logger.exception("Could not index collective offers from queue", extra={"exc": str(exc)})


def index_all_collective_offers_and_templates() -> None:
    """Pop collective offers from indexation queue and reindex them."""
    backend = _get_backend()

    collective_offers = educational_models.CollectiveOffer.query.with_entities(
        educational_models.CollectiveOffer.id
    ).all()
    collective_offer_templates = educational_models.CollectiveOfferTemplate.query.with_entities(
        educational_models.CollectiveOfferTemplate.id
    ).all()
    _reindex_collective_offer_ids(backend, [offer.id for offer in collective_offers])
    _reindex_collective_offer_template_ids(backend, [template.id for template in collective_offer_templates])


def index_collective_offers_templates_in_queue(from_error_queue: bool = False) -> None:
    """Pop collective offers template from indexation queue and reindex them."""
    backend = _get_backend()
    try:
        chunk_size = settings.REDIS_COLLECTIVE_OFFER_TEMPLATE_IDS_CHUNK_SIZE
        collective_offer_template_ids = backend.pop_collective_offer_template_ids_from_queue(
            count=chunk_size, from_error_queue=from_error_queue
        )

        if not collective_offer_template_ids:
            return

        _reindex_collective_offer_template_ids(backend, collective_offer_template_ids)

    except Exception as exc:  # pylint: disable=broad-except
        if settings.IS_RUNNING_TESTS:
            raise
        logger.exception("Could not index collective offers template from queue", extra={"exc": str(exc)})


def index_venues_in_queue(from_error_queue: bool = False) -> None:
    """Pop venues from indexation queue and reindex them."""
    backend = _get_backend()
    try:
        chunk_size = settings.REDIS_VENUE_IDS_CHUNK_SIZE
        venue_ids = backend.pop_venue_ids_from_queue(count=chunk_size, from_error_queue=from_error_queue)

        if not venue_ids:
            return

        _reindex_venue_ids(backend, venue_ids)

    except Exception as exc:  # pylint: disable=broad-except
        if settings.IS_RUNNING_TESTS:
            raise
        logger.exception("Could not index venues from queue", extra={"exc": str(exc)})


def _reindex_venue_ids(backend: base.SearchBackend, venue_ids: Collection[int]) -> None:
    logger.info("Starting to index venues", extra={"count": len(venue_ids)})
    venues = (
        Venue.query.filter(Venue.id.in_(venue_ids))
        .options(joinedload(Venue.managingOfferer))
        .options(joinedload(Venue.contact))
        .options(joinedload(Venue.criteria))
    )

    to_add = []
    to_delete_ids = []

    for venue in venues:
        if venue.is_eligible_for_search:
            to_add.append(venue)
        else:
            to_delete_ids.append(venue.id)

    to_add_ids = [venue.id for venue in to_add]

    try:
        backend.index_venues(to_add)
    except Exception as exc:  # pylint: disable=broad-except
        backend.enqueue_venue_ids_in_error(to_add_ids)
        logger.warning(
            "Could not reindex venues, will automatically retry",
            extra={"exc": str(exc), "venues": to_add_ids},
            exc_info=True,
        )
    else:
        logger.info("Finished indexing venues", extra={"count": len(to_add)})

    if to_delete_ids:
        unindex_venue_ids(to_delete_ids)
        logger.info("Finished unindexing venues", extra={"count": len(to_delete_ids)})


def _reindex_collective_offer_ids(backend: base.SearchBackend, collective_offer_ids: Collection[int]) -> None:
    logger.info("Starting to index collective offers", extra={"count": len(collective_offer_ids)})
    collective_offers = educational_models.CollectiveOffer.query.filter(
        educational_models.CollectiveOffer.id.in_(collective_offer_ids)
    ).options(
        joinedload(educational_models.CollectiveOffer.collectiveStock).joinedload(
            educational_models.CollectiveStock.collectiveBookings
        ),
        joinedload(educational_models.CollectiveOffer.venue, innerjoin=True).joinedload(
            Venue.managingOfferer, innerjoin=True
        ),
    )

    to_add = [collective_offer for collective_offer in collective_offers if collective_offer.is_eligible_for_search]
    to_add_ids = [collective_offer.id for collective_offer in to_add]
    to_delete_ids = [
        collective_offer.id for collective_offer in collective_offers if not collective_offer.is_eligible_for_search
    ]

    try:
        backend.index_collective_offers(to_add)
    except Exception as exc:  # pylint: disable=broad-except
        backend.enqueue_collective_offer_ids_in_error(to_add_ids)
        logger.warning(
            "Could not reindex collective offers, will automatically retry",
            extra={"exc": str(exc), "collective_offers": to_add_ids},
            exc_info=True,
        )
    else:
        logger.info("Finished indexing collective offers", extra={"count": len(to_add)})

    if to_delete_ids:
        unindex_collective_offer_ids(to_delete_ids)
        logger.info("Finished unindexing collective offers", extra={"count": len(to_delete_ids)})


def _reindex_collective_offer_template_ids(
    backend: base.SearchBackend, collective_offer_template_ids: Collection[int]
) -> None:
    logger.info("Starting to index collective offers templates", extra={"count": len(collective_offer_template_ids)})
    collective_offers_templates = educational_models.CollectiveOfferTemplate.query.filter(
        educational_models.CollectiveOfferTemplate.id.in_(collective_offer_template_ids)
    ).options(
        joinedload(educational_models.CollectiveOfferTemplate.venue, innerjoin=True).joinedload(
            Venue.managingOfferer, innerjoin=True
        ),
    )

    to_add = [
        collective_offers_template
        for collective_offers_template in collective_offers_templates
        if collective_offers_template.is_eligible_for_search
    ]
    to_add_ids = [collective_offers_template.id for collective_offers_template in to_add]
    to_delete_ids = [
        collective_offers_template.id
        for collective_offers_template in collective_offers_templates
        if not collective_offers_template.is_eligible_for_search
    ]

    try:
        backend.index_collective_offer_templates(to_add)
    except Exception as exc:  # pylint: disable=broad-except
        backend.enqueue_collective_offer_template_ids_in_error(to_add_ids)
        logger.warning(
            "Could not reindex collective offers templates, will automatically retry",
            extra={"exc": str(exc), "collective_offers_templates": to_add_ids},
            exc_info=True,
        )
    else:
        logger.info("Finished indexing collective offers templates", extra={"count": len(to_add)})

    if to_delete_ids:
        unindex_collective_offer_template_ids(to_delete_ids)
        logger.info("Finished unindexing collective offers templates", extra={"count": len(to_delete_ids)})


def index_offers_of_venues_in_queue() -> None:
    """Pop venues from indexation queue and reindex their offers."""
    backend = _get_backend()
    try:
        venue_ids = backend.pop_venue_ids_for_offers_from_queue(count=settings.REDIS_VENUE_IDS_FOR_OFFERS_CHUNK_SIZE)
        for venue_id in venue_ids:
            page = 0
            logger.info("Starting to index offers of venue", extra={"venue": venue_id})
            while True:
                offer_ids = offer_queries.get_paginated_offer_ids_by_venue_id(
                    limit=settings.ALGOLIA_OFFERS_BY_VENUE_CHUNK_SIZE, page=page, venue_id=venue_id
                )
                if not offer_ids:
                    break
                reindex_offer_ids(offer_ids)
                page += 1
            logger.info("Finished indexing offers of venue", extra={"venue": venue_id})
    except Exception:  # pylint: disable=broad-except
        if settings.IS_RUNNING_TESTS:
            raise
        logger.exception("Could not index offers of venues from queue")


def reindex_offer_ids(offer_ids: Iterable[int]) -> None:
    """Given a list of `Offer.id`, reindex or unindex each offer
    (i.e. request the external indexation service an update or a
    removal).

    This function calls the external indexation service and may thus
    be slow. It should not be called by usual code. You should rather
    call `async_index_offer_ids()` instead to return quickly.
    """
    backend = _get_backend()

    to_add = []
    to_delete_ids = []
    offers = (
        Offer.query.options(joinedload(Offer.venue).joinedload(Venue.managingOfferer))
        .options(joinedload(Offer.criteria))
        .options(joinedload(Offer.mediations))
        .options(joinedload(Offer.product))
        .options(joinedload(Offer.stocks))
        .filter(Offer.id.in_(offer_ids))
    )

    for offer in offers:
        if offer and offer.is_eligible_for_search:
            to_add.append(offer)
        elif backend.check_offer_is_indexed(offer):
            to_delete_ids.append(offer.id)
        else:
            # FIXME (dbaty, 2021-06-24). I think we could safely do
            # without the hashmap in Redis. Check the logs and see if
            # I am right!
            logger.info(
                "Redis 'indexed_offers' set avoided unnecessary request to indexation service",
                extra={"source": "reindex_offer_ids", "offer": offer.id},
            )

    # Handle new or updated available offers
    try:
        backend.index_offers(to_add)
    except Exception as exc:  # pylint: disable=broad-except
        if settings.IS_RUNNING_TESTS:
            raise
        logger.warning(
            "Could not reindex offers, will automatically retry",
            extra={"exc": str(exc), "offers": [offer.id for offer in to_add]},
            exc_info=True,
        )
        backend.enqueue_offer_ids_in_error([offer.id for offer in to_add])

    # Handle unavailable offers (deleted, expired, sold out, etc.)
    try:
        backend.unindex_offer_ids(to_delete_ids)
    except Exception as exc:  # pylint: disable=broad-except
        if settings.IS_RUNNING_TESTS:
            raise
        logger.warning(
            "Could not unindex offers, will automatically retry",
            extra={"exc": str(exc), "offers": to_delete_ids},
            exc_info=True,
        )
        backend.enqueue_offer_ids_in_error(to_delete_ids)

    # some offers changes might make some venue ineligible for search
    _reindex_venues_from_offers(offer_ids)


def unindex_offer_ids(offer_ids: Iterable[int]) -> None:
    backend = _get_backend()
    try:
        backend.unindex_offer_ids(offer_ids)
    except Exception:  # pylint: disable=broad-except
        if settings.IS_RUNNING_TESTS:
            raise
        logger.exception("Could not unindex offers", extra={"offers": offer_ids})

    # some offers changes might make some venue ineligible for search
    _reindex_venues_from_offers(offer_ids)


def unindex_all_offers() -> None:
    if settings.IS_PROD:
        raise ValueError("It is forbidden to unindex all offers on this environment")
    backend = _get_backend()
    try:
        backend.unindex_all_offers()
    except Exception:  # pylint: disable=broad-except
        if settings.IS_RUNNING_TESTS:
            raise
        logger.exception("Could not unindex all offers")


def _reindex_venues_from_offers(offer_ids: Iterable[int]) -> None:
    """
    Get the offers' venue ids and reindex them
    """
    if not FeatureToggle.ENABLE_VENUE_STRICT_SEARCH.is_active():
        return

    query = Offer.query.filter(Offer.id.in_(offer_ids)).with_entities(Offer.venueId).distinct()
    venue_ids = [row[0] for row in query]

    logger.info("Starting to reindex venues from offers", extra={"venues_count": len(venue_ids)})
    async_index_venue_ids(venue_ids)


def reindex_venue_ids(venue_ids: Collection[int]) -> None:
    """Given a list of `Venue.id`, reindex or unindex each venue
    (i.e. request the external indexation service an update or a
    removal).

    This function calls the external indexation service and may thus
    be slow. It should not be called by usual code. You should rather
    call `async_index_venue_ids()` instead to return quickly.
    """
    backend = _get_backend()
    try:
        _reindex_venue_ids(backend, venue_ids)
    except Exception:  # pylint: disable=broad-except
        if settings.IS_RUNNING_TESTS:
            raise
        logger.exception("Could not reindex venues", extra={"venues": venue_ids})


def unindex_venue_ids(venue_ids: Iterable[int]) -> None:
    if not venue_ids:
        return
    backend = _get_backend()
    try:
        backend.unindex_venue_ids(venue_ids)
    except Exception:  # pylint: disable=broad-except
        if settings.IS_RUNNING_TESTS:
            raise
        logger.exception("Could not unindex venues", extra={"venues": venue_ids})


def unindex_all_collective_offers() -> None:
    if settings.IS_PROD:
        raise ValueError("It is forbidden to unindex all collective offers on this environment")
    backend = _get_backend()
    try:
        backend.unindex_all_collective_offers()
    except Exception:  # pylint: disable=broad-except
        if settings.IS_RUNNING_TESTS:
            raise
        logger.exception("Could not unindex all offers")


def unindex_all_collective_offer_templates() -> None:
    # this is a no-op while collective and templates are in the same index
    pass


def unindex_collective_offer_ids(collective_offer_ids: Iterable[int]) -> None:
    if not collective_offer_ids:
        return
    backend = _get_backend()
    try:
        backend.unindex_collective_offer_ids(collective_offer_ids)
    except Exception:  # pylint: disable=broad-except
        if settings.IS_RUNNING_TESTS:
            raise
        logger.exception("Could not unindex collective offers", extra={"collective_offers": collective_offer_ids})


def unindex_collective_offer_template_ids(collective_offer_template_ids: Iterable[int]) -> None:
    if not collective_offer_template_ids:
        return
    backend = _get_backend()
    try:
        backend.unindex_collective_offer_template_ids(collective_offer_template_ids)
    except Exception:  # pylint: disable=broad-except
        if settings.IS_RUNNING_TESTS:
            raise
        logger.exception(
            "Could not unindex collective offer templates",
            extra={"collective_offer_templates": collective_offer_template_ids},
        )


def unindex_all_venues() -> None:
    if settings.IS_PROD:
        raise ValueError("It is forbidden to unindex all venues on this environment")
    backend = _get_backend()
    try:
        backend.unindex_all_venues()
    except Exception:  # pylint: disable=broad-except
        if settings.IS_RUNNING_TESTS:
            raise
        logger.exception("Could not unindex all venues")

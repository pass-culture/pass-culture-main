from collections.abc import Collection
import datetime
import enum
import logging
from typing import Iterable

from flask_sqlalchemy import BaseQuery
import sqlalchemy as sa

from pcapi import settings
from pcapi.connectors.big_query import queries as big_query_queries
from pcapi.connectors.big_query.queries.last_30_days_booking import Last30DaysBookingsModel
from pcapi.core.bookings import models as bookings_models
from pcapi.core.categories import subcategories_v2
from pcapi.core.educational import models as educational_models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
import pcapi.core.offers.repository as offers_repository
from pcapi.core.search.backends import base
from pcapi.models import db
from pcapi.models.feature import FeatureToggle
from pcapi.utils import requests
from pcapi.utils.module_loading import import_string


logger = logging.getLogger(__name__)


class IndexationReason(enum.Enum):
    BOOKING_CANCELLATION = "booking-cancellation"
    BOOKING_COUNT_CHANGE = "booking-count-change"
    BOOKING_CREATION = "booking-creation"
    BOOKING_UNCANCELLATION = "booking-uncancellation"
    CINEMA_STOCK_QUANTITY_UPDATE = "cinema-stock-quantity-update"
    CRITERIA_LINK = "criteria-link"
    GOOGLE_PLACES_BANNER_SYNCHRONIZATION = "google-places-banner-synchronization"
    MEDIATION_CREATION = "mediation-creation"
    MEDIATION_DELETION = "mediation-deletion"
    # Offer-related reasons apply to individual and collective offers and templates
    OFFER_BATCH_UPDATE = "offer-batch-update"
    OFFER_BATCH_VALIDATION = "offer-batch-validation"
    OFFER_CREATION = "offer-publication"
    OFFER_PUBLICATION = "offer-publication"
    OFFER_MANUAL_REINDEXATION = "offer-manual-reindexation"
    OFFER_REINDEXATION = "offer-reindexation"  # reason for the reindexation of venues
    OFFER_UPDATE = "offer-update"
    OFFERER_VALIDATION = "offerer-validation"
    PRODUCT_DEACTIVATION = "product-deactivation"
    PRODUCT_REJECTION = "product-rejection"
    PRODUCT_UPDATE = "product-update"
    PRODUCT_WHITELIST_ADDITION = "product-whitelist-addition"
    STOCK_CREATION = "stock-creation"
    STOCK_DELETION = "stock-deletion"
    STOCK_SYNCHRONIZATION = "stock-synchronization"
    STOCK_UPDATE = "stock-update"
    VENUE_BATCH_UPDATE = "venue-batch-update"
    VENUE_CREATION = "venue-creation"
    VENUE_UPDATE = "venue-update"
    VENUE_BANNER_DELETION = "venue-banner-deletion"
    VENUE_BANNER_UPDATE = "venue-banner-update"
    VENUE_PROVIDER_CREATION = "venue-provider-creation"


def _get_backend() -> base.SearchBackend:
    backend_class = import_string(settings.SEARCH_BACKEND)
    return backend_class()


def _log_async_request(
    resource_type: str,
    ids: Iterable[int],
    reason: IndexationReason,
    extra: dict | None,
) -> None:
    extra = extra or {}
    logger.info(
        "Request to asynchronously reindex %s",
        resource_type,
        extra={
            "resource_type": resource_type,
            "reason": reason.value,
            # FIXME (dbaty, 2023-11-24) change `ids` to be a `Sequence[int]`
            "count": len(ids),  # type: ignore [arg-type]
            "partial_ids": list(ids)[:50],  # avoid huge log
        }
        | extra,
    )


def _log_indexation_error(
    resource_type: str,
    ids: Iterable[int],
    exc: Exception,
    from_error_queue: bool,
) -> None:
    """Log upon indexation error.

    If it's a network issue, there is nothing we can do: log as info.

    If the error occurred on the "main" queue, the erroring items
    will be moved to the error queue and automatically retried:
    there is nothing we should do, log as info.

    Otherwise, it could be a bug and we should thus analyze the issue:
    log as an exception.
    """
    if from_error_queue and not isinstance(exc, requests.exceptions.RequestException):
        log = logger.exception
    else:
        log = logger.info
    log(
        "Could not reindex %s, will automatically retry",
        resource_type,
        extra={"exc": str(exc), "ids": ids},
        exc_info=True,
    )


def async_index_offer_ids(
    offer_ids: Iterable[int],
    reason: IndexationReason,
    log_extra: dict | None = None,
) -> None:
    """Ask for an asynchronous reindexation of the given list of
    ``Offer.id``.

    This function returns quickly. The "real" reindexation will be
    done later through a cron job.
    """
    _log_async_request("offers", offer_ids, reason, log_extra)
    backend = _get_backend()
    try:
        backend.enqueue_offer_ids(offer_ids)
    except Exception:  # pylint: disable=broad-except
        if not settings.CATCH_INDEXATION_EXCEPTIONS:
            raise
        logger.exception("Could not enqueue offer ids to index", extra={"offers": offer_ids})


def async_index_collective_offer_template_ids(
    collective_offer_template_ids: Iterable[int],
    reason: IndexationReason,
    log_extra: dict | None = None,
) -> None:
    """Ask for an asynchronous reindexation of the given list of
    ``CollectiveOfferTemplate.id``.

    This function returns quickly. The "real" reindexation will be
    done later through a cron job.
    """
    _log_async_request("collective offer templates", collective_offer_template_ids, reason, log_extra)
    backend = _get_backend()
    try:
        backend.enqueue_collective_offer_template_ids(collective_offer_template_ids)
    except Exception:  # pylint: disable=broad-except
        if not settings.CATCH_INDEXATION_EXCEPTIONS:
            raise
        logger.exception(
            "Could not enqueue collective offer template ids to index",
            extra={
                "collective_offer_template_ids": collective_offer_template_ids,
            },
        )


def async_index_venue_ids(
    venue_ids: Iterable[int],
    reason: IndexationReason,
    log_extra: dict | None = None,
) -> None:
    """Ask for an asynchronous reindexation of the given list of
    permanent ``Venue`` ids.

    This function returns quickly. The "real" reindexation will be
    done later through a cron job.
    """
    _log_async_request("venues", venue_ids, reason, log_extra)
    backend = _get_backend()
    try:
        backend.enqueue_venue_ids(venue_ids)
    except Exception:  # pylint: disable=broad-except
        if not settings.CATCH_INDEXATION_EXCEPTIONS:
            raise
        logger.exception("Could not enqueue venue ids to index", extra={"venues": venue_ids})


def async_index_offers_of_venue_ids(
    venue_ids: Iterable[int],
    reason: IndexationReason,
    log_extra: dict | None = None,
) -> None:
    """Ask for an asynchronous reindexation of the offers attached to venues
    from the list of ``Venue.id``.

    This function returns quickly. The "real" reindexation will be
    done later through a cron job.
    """
    _log_async_request("offers of venues", venue_ids, reason, log_extra)
    backend = _get_backend()
    try:
        backend.enqueue_venue_ids_for_offers(venue_ids)
    except Exception:  # pylint: disable=broad-except
        if not settings.CATCH_INDEXATION_EXCEPTIONS:
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

    If ``stop_only_when_empty`` is True (i.e. if called manually to
    process the whole queue), we pop from the queue and stop only when
    the queue is empty.
    """
    backend = _get_backend()
    while True:
        with backend.pop_offer_ids_from_queue(
            count=settings.REDIS_OFFER_IDS_CHUNK_SIZE,
            from_error_queue=from_error_queue,
        ) as offer_ids:
            if not offer_ids:
                break

            logger.info(
                "Fetched offer ids from indexation queue",
                extra={"count": len(offer_ids), "offer_ids": offer_ids},
            )
            try:
                reindex_offer_ids(offer_ids, from_error_queue=from_error_queue)
            except Exception as exc:  # pylint: disable=broad-except
                if not settings.CATCH_INDEXATION_EXCEPTIONS:
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


def index_all_collective_offers_and_templates() -> None:
    """Force reindexation of all collective offers and templates."""
    backend = _get_backend()

    collective_offer_templates = educational_models.CollectiveOfferTemplate.query.with_entities(
        educational_models.CollectiveOfferTemplate.id
    ).all()
    _reindex_collective_offer_template_ids(
        backend,
        [template.id for template in collective_offer_templates],
        from_error_queue=False,
    )


def index_collective_offers_templates_in_queue(from_error_queue: bool = False) -> None:
    """Pop collective offers template from indexation queue and reindex them."""
    backend = _get_backend()
    try:
        chunk_size = settings.REDIS_COLLECTIVE_OFFER_TEMPLATE_IDS_CHUNK_SIZE
        with backend.pop_collective_offer_template_ids_from_queue(
            count=chunk_size,
            from_error_queue=from_error_queue,
        ) as collective_offer_template_ids:
            if not collective_offer_template_ids:
                return
            _reindex_collective_offer_template_ids(backend, collective_offer_template_ids, from_error_queue)

    except Exception as exc:  # pylint: disable=broad-except
        if not settings.CATCH_INDEXATION_EXCEPTIONS:
            raise
        logger.exception("Could not index collective offers template from queue", extra={"exc": str(exc)})


def index_venues_in_queue(from_error_queue: bool = False) -> None:
    """Pop venues from indexation queue and reindex them."""
    backend = _get_backend()
    try:
        chunk_size = settings.REDIS_VENUE_IDS_CHUNK_SIZE
        with backend.pop_venue_ids_from_queue(
            count=chunk_size,
            from_error_queue=from_error_queue,
        ) as venue_ids:
            if not venue_ids:
                return
            _reindex_venue_ids(backend, venue_ids, from_error_queue)

    except Exception as exc:  # pylint: disable=broad-except
        if not settings.CATCH_INDEXATION_EXCEPTIONS:
            raise
        logger.exception("Could not index venues from queue", extra={"exc": str(exc)})


def _reindex_venue_ids(
    backend: base.SearchBackend,
    venue_ids: Collection[int],
    from_error_queue: bool = False,
) -> None:
    logger.info("Starting to index venues", extra={"count": len(venue_ids)})
    venues = (
        offerers_models.Venue.query.filter(offerers_models.Venue.id.in_(venue_ids))
        .options(sa.orm.joinedload(offerers_models.Venue.managingOfferer))
        .options(sa.orm.joinedload(offerers_models.Venue.contact))
        .options(sa.orm.joinedload(offerers_models.Venue.criteria))
        .options(sa.orm.joinedload(offerers_models.Venue.googlePlacesInfo))
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
        _log_indexation_error(
            "venues",
            ids=to_add_ids,
            exc=exc,
            from_error_queue=from_error_queue,
        )
    else:
        logger.info("Finished indexing venues", extra={"count": len(to_add)})

    if to_delete_ids:
        unindex_venue_ids(to_delete_ids)
        logger.info("Finished unindexing venues", extra={"count": len(to_delete_ids)})


def _reindex_collective_offer_template_ids(
    backend: base.SearchBackend,
    collective_offer_template_ids: Collection[int],
    from_error_queue: bool = False,
) -> None:
    logger.info("Starting to index collective offers templates", extra={"count": len(collective_offer_template_ids)})
    collective_offers_templates = educational_models.CollectiveOfferTemplate.query.filter(
        educational_models.CollectiveOfferTemplate.id.in_(collective_offer_template_ids)
    ).options(
        sa.orm.joinedload(educational_models.CollectiveOfferTemplate.venue, innerjoin=True).joinedload(
            offerers_models.Venue.managingOfferer, innerjoin=True
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
        _log_indexation_error(
            "collective offer templates",
            ids=to_add_ids,
            exc=exc,
            from_error_queue=from_error_queue,
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
        with backend.pop_venue_ids_for_offers_from_queue(
            count=settings.REDIS_VENUE_IDS_FOR_OFFERS_CHUNK_SIZE,
        ) as venue_ids:
            for venue_id in venue_ids:
                page = 0
                logger.info("Starting to index offers of venue", extra={"venue": venue_id})
                while True:
                    offer_ids = offers_repository.get_paginated_offer_ids_by_venue_id(
                        limit=settings.ALGOLIA_OFFERS_BY_VENUE_CHUNK_SIZE,
                        page=page,
                        venue_id=venue_id,
                    )
                    if not offer_ids:
                        break
                    reindex_offer_ids(offer_ids, from_error_queue=False)
                    page += 1
                logger.info("Finished indexing offers of venue", extra={"venue": venue_id})
    except Exception:  # pylint: disable=broad-except
        if not settings.CATCH_INDEXATION_EXCEPTIONS:
            raise
        logger.exception("Could not index offers of venues from queue")


def get_base_query_for_collective_template_offer_indexation() -> BaseQuery:
    return educational_models.CollectiveOfferTemplate.query.options(
        sa.orm.joinedload(educational_models.CollectiveOfferTemplate.venue, innerjoin=True).joinedload(
            offerers_models.Venue.managingOfferer, innerjoin=True
        ),
    )


def get_base_query_for_offer_indexation() -> BaseQuery:
    return (
        # We are only interested in bookable stocks, which means that
        # we can exclude past stocks (which are numerous for recurrent
        # offers and use too much memory). However, we do want to
        # return offers that don't have future stocks, which is why
        # the condition is in the _outer_ join, and not in a "where"
        # clause through `filter()`.
        offers_models.Offer.query.outerjoin(
            offers_models.Stock,
            (offers_models.Stock.offerId == offers_models.Offer.id) & offers_models.Stock._bookable,
        )
        .options(sa.orm.contains_eager(offers_models.Offer.stocks))
        .options(sa.orm.joinedload(offers_models.Offer.venue).joinedload(offerers_models.Venue.managingOfferer))
        .options(sa.orm.joinedload(offers_models.Offer.criteria))
        .options(sa.orm.joinedload(offers_models.Offer.mediations))
        .options(sa.orm.joinedload(offers_models.Offer.product))
    )


DEFAULT_DAYS_FOR_LAST_BOOKINGS = 30


def get_offers_booking_count_by_id(
    offer_ids: Iterable[int], days: int = DEFAULT_DAYS_FOR_LAST_BOOKINGS
) -> dict[int, int]:
    offer_booked_since_x_days = (
        offers_models.Offer.query.join(offers_models.Offer.stocks)
        .outerjoin(offers_models.Offer.product)
        .join(offers_models.Stock.bookings)
        .filter(
            offers_models.Offer.id.in_(offer_ids),
            offers_models.Offer.isActive.is_(True),
            bookings_models.Booking.dateCreated >= datetime.datetime.utcnow() - datetime.timedelta(days=days),
            bookings_models.Booking.status != bookings_models.BookingStatus.CANCELLED,
        )
        .group_by(offers_models.Offer.id)
        .with_entities(offers_models.Offer.id, sa.func.count(bookings_models.Booking.id))
    )
    return dict(offer_booked_since_x_days)


def get_last_x_days_booking_count_by_offer(offers: Iterable[offers_models.Offer]) -> dict[int, int]:
    offers_with_product = []
    offers_without_product = []

    if not FeatureToggle.ALGOLIA_BOOKINGS_NUMBER_COMPUTATION.is_active():
        return {}

    for offer in offers:
        if offer.product:
            offers_with_product.append(offer)
        else:
            offers_without_product.append(offer)

    default_dict = get_offers_booking_count_by_id([offer.id for offer in offers_without_product])

    for offer in offers_with_product:
        default_dict[offer.id] = offer.product.last_30_days_booking if offer.product.last_30_days_booking else 0

    return default_dict


def reindex_offer_ids(offer_ids: Iterable[int], from_error_queue: bool = False) -> None:
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

    offers = get_base_query_for_offer_indexation().filter(offers_models.Offer.id.in_(offer_ids))

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
    last_x_days_bookings_count_by_offer = get_last_x_days_booking_count_by_offer(to_add)
    try:
        backend.index_offers(to_add, last_x_days_bookings_count_by_offer)
    except Exception as exc:  # pylint: disable=broad-except
        if not settings.CATCH_INDEXATION_EXCEPTIONS:
            raise
        _log_indexation_error(
            "offers",
            ids=[offer.id for offer in to_add],
            exc=exc,
            from_error_queue=from_error_queue,
        )
        backend.enqueue_offer_ids_in_error([offer.id for offer in to_add])

    # Handle unavailable offers (deleted, expired, sold out, etc.)
    try:
        backend.unindex_offer_ids(to_delete_ids)
    except Exception as exc:  # pylint: disable=broad-except
        if not settings.CATCH_INDEXATION_EXCEPTIONS:
            raise
        _log_indexation_error(
            "offers",
            ids=to_delete_ids,
            exc=exc,
            from_error_queue=from_error_queue,
        )
        backend.enqueue_offer_ids_in_error(to_delete_ids)

    # some offers changes might make some venue ineligible for search
    _reindex_venues_from_offers(offer_ids)


def unindex_offer_ids(offer_ids: Iterable[int]) -> None:
    backend = _get_backend()
    try:
        backend.unindex_offer_ids(offer_ids)
    except Exception:  # pylint: disable=broad-except
        if not settings.CATCH_INDEXATION_EXCEPTIONS:
            raise
        logger.exception("Could not unindex offers", extra={"offers": offer_ids})

    # some offers changes might make some venue ineligible for search
    _reindex_venues_from_offers(offer_ids)


def unindex_all_offers() -> None:
    if not settings.ENABLE_UNINDEXING_ALL:
        raise ValueError("It is forbidden to unindex all offers on this environment")
    backend = _get_backend()
    try:
        backend.unindex_all_offers()
    except Exception:  # pylint: disable=broad-except
        if not settings.CATCH_INDEXATION_EXCEPTIONS:
            raise
        logger.exception("Could not unindex all offers")


def _reindex_venues_from_offers(offer_ids: Iterable[int]) -> None:
    """
    Get the offers' venue ids and reindex them
    """
    if not FeatureToggle.ENABLE_VENUE_STRICT_SEARCH.is_active():
        return

    query = (
        offers_models.Offer.query.filter(offers_models.Offer.id.in_(offer_ids))
        .with_entities(offers_models.Offer.venueId)
        .distinct()
    )
    venue_ids = [row[0] for row in query]

    logger.info("Starting to reindex venues from offers", extra={"venues_count": len(venue_ids)})
    async_index_venue_ids(venue_ids, reason=IndexationReason.OFFER_REINDEXATION)


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
        _reindex_venue_ids(backend, venue_ids, from_error_queue=False)
    except Exception:  # pylint: disable=broad-except
        if not settings.CATCH_INDEXATION_EXCEPTIONS:
            raise
        logger.exception("Could not reindex venues", extra={"venues": venue_ids})


def unindex_venue_ids(venue_ids: Iterable[int]) -> None:
    if not venue_ids:
        return
    backend = _get_backend()
    try:
        backend.unindex_venue_ids(venue_ids)
    except Exception:  # pylint: disable=broad-except
        if not settings.CATCH_INDEXATION_EXCEPTIONS:
            raise
        logger.exception("Could not unindex venues", extra={"venues": venue_ids})


def unindex_all_collective_offer_templates() -> None:
    if not settings.ENABLE_UNINDEXING_ALL:
        raise ValueError("It is forbidden to unindex all collective offer templates on this environment")
    backend = _get_backend()
    try:
        backend.unindex_all_collective_offer_templates()
    except Exception:  # pylint: disable=broad-except
        if not settings.CATCH_INDEXATION_EXCEPTIONS:
            raise
        logger.exception("Could not unindex all offers")


def unindex_collective_offer_template_ids(collective_offer_template_ids: Iterable[int]) -> None:
    if not collective_offer_template_ids:
        return
    backend = _get_backend()
    try:
        backend.unindex_collective_offer_template_ids(collective_offer_template_ids)
    except Exception:  # pylint: disable=broad-except
        if not settings.CATCH_INDEXATION_EXCEPTIONS:
            raise
        logger.exception(
            "Could not unindex collective offer templates",
            extra={"collective_offer_templates": collective_offer_template_ids},
        )


def unindex_all_venues() -> None:
    if not settings.ENABLE_UNINDEXING_ALL:
        raise ValueError("It is forbidden to unindex all venues on this environment")
    backend = _get_backend()
    try:
        backend.unindex_all_venues()
    except Exception:  # pylint: disable=broad-except
        if not settings.CATCH_INDEXATION_EXCEPTIONS:
            raise
        logger.exception("Could not unindex all venues")


def get_last_30_days_bookings_for_eans() -> dict[str, int]:
    logger.info("Getting eans with bookings in the last 30 days")
    rows: Iterable[Last30DaysBookingsModel] = big_query_queries.Last30DaysBookings().execute()
    ean_booking_count = {row.ean: row.booking_count for row in rows if row.ean}
    logger.info("Got %s eans with bookings in the last 30 days", len(ean_booking_count))
    return ean_booking_count


def get_last_x_days_bookings_for_movies(days: int = 30) -> dict[int, int]:
    result = db.session.execute(
        sa.select(offers_models.Product.id, sa.func.count())
        .select_from(bookings_models.Booking)
        .join(bookings_models.Booking.stock)
        .join(offers_models.Stock.offer)
        .join(offers_models.Offer.product)
        .filter(
            offers_models.Product.subcategoryId == subcategories_v2.SEANCE_CINE.id,
            bookings_models.Booking.status != bookings_models.BookingStatus.CANCELLED,
            bookings_models.Booking.dateCreated > datetime.date.today() - datetime.timedelta(days=days),
        )
        .group_by(offers_models.Product.id)
    )
    return {row[0]: row[1] for row in result}


def update_products_last_30_days_booking_count(batch_size: int = 1000) -> None:
    updated_products = update_booking_count_by_product()
    if not updated_products:
        return

    offer_ids_to_reindex_query = offers_models.Offer.query.filter(
        offers_models.Offer.productId.in_([product.id for product in updated_products])
    ).with_entities(offers_models.Offer.id)

    logger.info("Starting to reindex offers with product booked recently. Product count: %s", len(updated_products))

    offer_ids_to_reindex = set()
    for (offer_id,) in offer_ids_to_reindex_query.yield_per(batch_size):
        offer_ids_to_reindex.add(offer_id)
        if len(offer_ids_to_reindex) == batch_size:
            logger.info("Reindexing offers with product booked recently. Batch count: %s", len(offer_ids_to_reindex))
            async_index_offer_ids(
                offer_ids_to_reindex,
                reason=IndexationReason.BOOKING_COUNT_CHANGE,
            )
            offer_ids_to_reindex = set()
    if offer_ids_to_reindex:
        async_index_offer_ids(
            offer_ids_to_reindex,
            reason=IndexationReason.BOOKING_COUNT_CHANGE,
        )


def update_last_30_days_bookings_for_eans() -> list[offers_models.Product]:
    booking_count_by_ean = get_last_30_days_bookings_for_eans()
    updated_products = []
    current_product_batch = []

    batch_size = 100
    eans = list(booking_count_by_ean.keys())
    for batch in range(0, len(booking_count_by_ean), batch_size):
        ean_batch = eans[batch : batch + batch_size]
        for product in db.session.query(offers_models.Product).filter(
            offers_models.Product.extraData["ean"].astext.in_(ean_batch)
        ):
            ean = product.extraData["ean"]
            old_last_x_days_booking = product.last_30_days_booking
            updated_last_x_days_booking = booking_count_by_ean.get(ean)

            if old_last_x_days_booking != updated_last_x_days_booking:
                product.last_30_days_booking = updated_last_x_days_booking
                updated_products.append(product)
                current_product_batch.append(product)
        db.session.add_all(current_product_batch)
        db.session.commit()
        logger.info("Updated %s products", len(current_product_batch))
        current_product_batch = []

    return updated_products


def update_last_30_days_bookings_for_movies() -> list[offers_models.Product]:
    booking_count_by_product = get_last_x_days_bookings_for_movies(days=30)
    updated_products = []
    current_product_batch = []

    batch_size = 100
    product_ids = list(booking_count_by_product.keys())
    for start in range(0, len(product_ids), batch_size):
        batch = offers_models.Product.query.filter(
            offers_models.Product.id.in_(product_ids[start : start + batch_size])
        )
        for product in batch:
            old_last_x_days_booking = product.last_30_days_booking
            updated_last_x_days_booking = booking_count_by_product.get(product.id)

            if old_last_x_days_booking != updated_last_x_days_booking:
                product.last_30_days_booking = updated_last_x_days_booking
                updated_products.append(product)
                current_product_batch.append(product)

        db.session.add_all(current_product_batch)
        db.session.commit()
        logger.info("Updated %s products", len(current_product_batch))
        current_product_batch = []

    return updated_products


def update_booking_count_by_product() -> list[offers_models.Product]:
    updated_products = update_last_30_days_bookings_for_eans()
    updated_products += update_last_30_days_bookings_for_movies()

    return updated_products


def clean_processing_queues() -> None:
    backend = _get_backend()
    backend.clean_processing_queues()

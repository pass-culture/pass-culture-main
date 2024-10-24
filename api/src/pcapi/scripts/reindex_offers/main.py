import datetime
import logging
import statistics
import time

import pytz

from pcapi import settings
from pcapi.app import app
from pcapi.core import search
import pcapi.core.offers.models as offers_models
from pcapi.core.search.backends import base
from pcapi.utils.module_loading import import_string


app.app_context().push()

BATCH_SIZE = 1_000
REPORT_EVERY = 10_000
REDIS_HASHMAP_INDEXED_OFFERS_NAME = "indexed_offers"

logger = logging.getLogger(__name__)


def _get_eta(end: int, current: int, elapsed_per_batch: list[int]) -> str:
    left_to_do = end - current
    eta_seconds = left_to_do / BATCH_SIZE * statistics.mean(elapsed_per_batch)
    eta_datetime = datetime.datetime.utcnow() + datetime.timedelta(seconds=eta_seconds)
    eta_datetime = eta_datetime.astimezone(pytz.timezone("Europe/Paris"))
    return eta_datetime.strftime("%d/%m/%Y %H:%M:%S")


def _enqueue_or_index(
    backend: base.SearchBackend,
    q: list,
    offer: offers_models.Offer | None,
    last_30_days_bookings: dict[int, int] | None,
    force_index: bool = False,
) -> None:
    if offer and last_30_days_bookings is not None:
        q.append((offer, last_30_days_bookings.get(offer.id) or 0))
    if force_index or len(q) > BATCH_SIZE:
        try:
            backend.index_offers([offer for offer, _ in q], {offer.id: n_bookings for offer, n_bookings in q})
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception(
                "Full offer reindexation: error while reindexing from %d to %d: %s", q[0][0].id, q[-1][0].id, exc
            )
        q.clear()


def _process_eligible_offers(backend: base.SearchBackend, queue: list, offers: list[offers_models.Offer]) -> None:
    last_x_days_bookings_count_by_offer = search.get_last_x_days_booking_count_by_offer(offers)
    for offer in offers:
        if offer.is_eligible_for_search:
            _enqueue_or_index(backend, queue, offer, last_x_days_bookings_count_by_offer)


def _report_progress(items_count: int, current: int, elapsed_per_batch: list, last_report: int) -> int:
    eta = _get_eta(items_count, current, elapsed_per_batch)
    if current - last_report >= REPORT_EVERY:
        logger.info("  => OK: %d | eta = %s", current, eta)
        return current

    return last_report


def _get_backend() -> base.SearchBackend:
    backend_class = import_string(settings.SEARCH_BACKEND)
    return backend_class()


def full_reindex_indexed_offers() -> None:
    """Reindex all already indexed offers.

    It behaves the same as `full_index_offers` excepts that it iterates over
    all offers contained in `REDIS_HASHMAP_INDEXED_OFFERS_NAME`, which keeps
    track of offers already indexed.
    """

    backend = _get_backend()
    queue: list[tuple] = []

    start = 0
    last_report = 0
    elapsed_per_batch = []
    try:
        offer_ids_to_index = sorted(
            [int(offer_id) for offer_id in backend.redis_client.hkeys(REDIS_HASHMAP_INDEXED_OFFERS_NAME)]  # type: ignore
        )
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Error while fetching indexed offers: %s", exc)
        return

    while start <= len(offer_ids_to_index):
        start_time = time.perf_counter()
        offers = (
            search.get_base_query_for_offer_indexation()
            .filter(
                offers_models.Offer.isActive.is_(True),
                offers_models.Offer.id.in_(offer_ids_to_index[start : start + BATCH_SIZE]),
            )
            .order_by(offers_models.Offer.id)
        )
        _process_eligible_offers(backend, queue, offers)
        elapsed_per_batch.append(int(time.perf_counter() - start_time))
        start = start + BATCH_SIZE
        last_report = _report_progress(len(offer_ids_to_index), start, elapsed_per_batch, last_report)
    _enqueue_or_index(backend, queue, offer=None, last_30_days_bookings=None, force_index=True)
    logger.info("Done")


if __name__ == "__main__":
    full_reindex_indexed_offers()

import datetime
import logging
import statistics
import time

import pytz

from pcapi.app import app
from pcapi.core import search
import pcapi.core.offers.models as offers_models
from pcapi.core.search.backends.algolia import AlgoliaBackend
from pcapi.core.search.backends.algolia import REDIS_HASHMAP_INDEXED_OFFERS_NAME


logger = logging.getLogger(__name__)

BATCH_SIZE = 1_000
REPORT_EVERY = 10_000


def serialize_offer_without_none_fields(cls, offer: offers_models.Offer, last_30_days_bookings: int) -> dict:  # type: ignore[no-untyped-def]
    result = AlgoliaBackend._original_serialize_offer(offer, last_30_days_bookings)  # type: ignore[attr-defined]
    for section in ("offer", "offerer", "venue"):
        result[section] = {key: value for key, value in result[section].items() if value is not None}
    return result


AlgoliaBackend._original_serialize_offer = AlgoliaBackend.serialize_offer  # type: ignore[attr-defined]
AlgoliaBackend.serialize_offer = serialize_offer_without_none_fields  # type: ignore[method-assign, assignment]


def _get_eta(end: int, current: int, elapsed_per_batch: list[int]) -> str:
    left_to_do = end - current
    eta_seconds = left_to_do / BATCH_SIZE * statistics.mean(elapsed_per_batch)
    eta_datetime = datetime.datetime.utcnow() + datetime.timedelta(seconds=eta_seconds)
    eta_datetime = eta_datetime.astimezone(pytz.timezone("Europe/Paris"))
    return eta_datetime.strftime("%d/%m/%Y %H:%M:%S")


def full_reindex_offers() -> None:
    backend = AlgoliaBackend()
    queue: list[tuple] = []

    def enqueue_or_index(
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

    start = 0
    to_report = 0
    elapsed_per_batch = []
    offer_ids_to_index = [int(offer_id) for offer_id in backend.redis_client.hkeys(REDIS_HASHMAP_INDEXED_OFFERS_NAME)]
    offer_ids_to_index.sort()

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
        for offer in offers:
            enqueue_or_index(queue, offer, {})

        elapsed_per_batch.append(int(time.perf_counter() - start_time))
        start = start + BATCH_SIZE
        eta = _get_eta(len(offer_ids_to_index), start, elapsed_per_batch)
        to_report += BATCH_SIZE
        if to_report >= REPORT_EVERY:
            to_report = 0
            print(f"  => OK: {start} | eta = {eta}")
    enqueue_or_index(queue, offer=None, last_30_days_bookings=None, force_index=True)
    print("Done")


if __name__ == "__main__":
    with app.app_context():
        full_reindex_offers()

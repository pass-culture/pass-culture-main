import datetime
import logging
import statistics
import time

import pytz

from pcapi.core import search
import pcapi.core.offers.models as offers_models
from pcapi.core.search.backends import algolia
from pcapi.utils.blueprint import Blueprint


BATCH_SIZE = 1_000
REPORT_EVERY = 10_000

logger = logging.getLogger(__name__)
blueprint = Blueprint(__name__, __name__)


def _get_eta(end: int, current: int, elapsed_per_batch: list[int]) -> str:
    left_to_do = end - current
    eta_seconds = left_to_do / BATCH_SIZE * statistics.mean(elapsed_per_batch)
    eta_datetime = datetime.datetime.utcnow() + datetime.timedelta(seconds=eta_seconds)
    eta_datetime = eta_datetime.astimezone(pytz.timezone("Europe/Paris"))
    return eta_datetime.strftime("%d/%m/%Y %H:%M:%S")


@blueprint.cli.command("full_reindex_indexed_offers")
def full_reindex_indexed_offers() -> None:
    backend = algolia.AlgoliaBackend()
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
    offer_ids_to_index = [
        int(offer_id) for offer_id in backend.redis_client.hkeys(algolia.REDIS_HASHMAP_INDEXED_OFFERS_NAME)
    ]

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
            logger.info("  => OK: %d | eta = %s", start, eta)
    enqueue_or_index(queue, offer=None, last_30_days_bookings=None, force_index=True)
    logger.info("Done")

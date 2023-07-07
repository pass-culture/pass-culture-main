import datetime
import logging
import statistics
import time

import click
import pytz

from pcapi.core import search
import pcapi.core.offers.models as offers_models
from pcapi.core.search.backends import algolia
from pcapi.models import db
from pcapi.models.feature import FeatureToggle
from pcapi.utils.blueprint import Blueprint


BATCH_SIZE = 1_000
REPORT_EVERY = 10_000

logger = logging.getLogger(__name__)
blueprint = Blueprint(__name__, __name__)


def _get_eta(end, current, elapsed_per_batch):  # type: ignore [no-untyped-def]
    left_to_do = end - current
    eta = left_to_do / BATCH_SIZE * statistics.mean(elapsed_per_batch)
    eta = datetime.datetime.utcnow() + datetime.timedelta(seconds=eta)
    eta = eta.astimezone(pytz.timezone("Europe/Paris"))
    eta = eta.strftime("%d/%m/%Y %H:%M:%S")
    return eta


@blueprint.cli.command("full_index_offers")  # type: ignore [arg-type]
@click.argument("start", type=int, required=True)
@click.argument("end", type=int, required=True)
def full_index_offers(start, end):  # type: ignore [no-untyped-def]
    """Reindex all bookable offers.

    The script iterates over all active offers. For each offer, it
    indexes it on the backend (Algolia) if the offer is bookable.
    Otherwise, the offer is NOT unindexed, as we suppose that the
    offer has already been unindexed through the normally-run
    code. That way, this script skips a lot of unnecessary
    unindexation requests.

    This script processes batches of 1.000 offers and reports back
    every 10.000 offers.

    Errors are logged and are not blocking. You MUST check the logs
    for batches that failed and MUST re-run all these batches.

    Obviously, the script takes a lot of time. You should run multiple
    instances of it at the same time. 4 concurrent instances looks
    like a good compromise.

    Usage:

        $ flask full_index_offers.py 10_000_000 20_000_000

    Using "_" as thousands separator is supported (and encouraged for
    clarity).
    """
    if start > end:
        raise ValueError('"start" must be less than "end"')
    backend = algolia.AlgoliaBackend()

    queue = []

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

    to_report = 0
    elapsed_per_batch = []

    while start <= end:
        start_time = time.perf_counter()
        offers = (
            search.get_base_query_for_offer_indexation()
            .filter(
                offers_models.Offer.isActive.is_(True),
                offers_models.Offer.id.between(start, min(start + BATCH_SIZE, end)),
            )
            .order_by(offers_models.Offer.id)
        )
        if FeatureToggle.ALGOLIA_BOOKINGS_NUMBER_COMPUTATION.is_active():
            last_30_days_bookings = {
                row.offer_id: row.bookings_number
                for row in db.session.execute(
                    search.get_base_query_for_last_30_days_bookings().filter(
                        offers_models.Offer.isActive.is_(True),
                        offers_models.Offer.id.between(start, min(start + BATCH_SIZE, end)),
                    )
                ).all()
            }
        else:
            last_30_days_bookings = {}

        for offer in offers:
            if offer.is_eligible_for_search:
                enqueue_or_index(queue, offer, last_30_days_bookings)
        elapsed_per_batch.append(int(time.perf_counter() - start_time))
        start = start + BATCH_SIZE
        eta = _get_eta(end, start, elapsed_per_batch)
        to_report += BATCH_SIZE
        if to_report >= REPORT_EVERY:
            to_report = 0
            print(f"  => OK: {start} | eta = {eta}")
    enqueue_or_index(queue, offer=None, last_30_days_bookings=None, force_index=True)
    print("Done")

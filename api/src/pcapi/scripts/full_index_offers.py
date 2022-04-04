import datetime
import logging
import statistics
import time

import click
import pytz
from sqlalchemy.orm import joinedload

import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.models as offers_models
from pcapi.core.search.backends import algolia
from pcapi.utils.blueprint import Blueprint


BATCH_SIZE = 1_000
REPORT_EVERY = 10_000

logger = logging.getLogger(__name__)
blueprint = Blueprint(__name__, __name__)


def _get_eta(end, current, elapsed_per_batch):
    left_to_do = end - current
    eta = left_to_do / BATCH_SIZE * statistics.mean(elapsed_per_batch)
    eta = datetime.datetime.utcnow() + datetime.timedelta(seconds=eta)
    eta = eta.astimezone(pytz.timezone("Europe/Paris"))
    eta = eta.strftime("%d/%m/%Y %H:%M:%S")
    return eta


@blueprint.cli.command("full_index_offers")
@click.argument("start", type=int, required=True)
@click.argument("end", type=int, required=True)
def full_index_offers(start, end):
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

    def enqueue_or_index(q, offer, force_index=False):
        if offer:
            q.append(offer)
        if force_index or len(q) > BATCH_SIZE:
            try:
                backend.index_offers(q)
            except Exception as exc:  # pylint: disable=broad-except
                logger.exception(
                    "Full offer reindexation: error while reindexing from %d to %d: %s", q[0].id, q[-1].id, exc
                )
            q.clear()

    to_report = 0
    elapsed_per_batch = []

    while start <= end:
        start_time = time.perf_counter()
        offers = (
            offers_models.Offer.query.options(
                joinedload(offers_models.Offer.venue).joinedload(offerers_models.Venue.managingOfferer)
            )
            .options(joinedload(offers_models.Offer.criteria))
            .options(joinedload(offers_models.Offer.mediations))
            .options(joinedload(offers_models.Offer.product))
            .options(joinedload(offers_models.Offer.stocks))
            .filter(
                offers_models.Offer.isActive.is_(True),
                offers_models.Offer.id.between(start, min(start + BATCH_SIZE, end)),
            )
            .order_by(offers_models.Offer.id)
        )
        for offer in offers:
            if offer.is_eligible_for_search:
                enqueue_or_index(queue, offer)
        elapsed_per_batch.append(int(time.perf_counter() - start_time))
        start = start + BATCH_SIZE
        eta = _get_eta(end, start, elapsed_per_batch)
        to_report += BATCH_SIZE
        if to_report >= REPORT_EVERY:
            to_report = 0
            print(f"  => OK: {start} | eta = {eta}")
    enqueue_or_index(queue, offer=None, force_index=True)
    print("Done")

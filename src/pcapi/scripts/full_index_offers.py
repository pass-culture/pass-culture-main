"""Reindex all bookable offers.

The script iterates over all active offers. For each offer, it indexes
it on App Search if the offer is bookable. Otherwise, the offer is NOT
unindexed, as we suppose that the offer has already been unindexed
through the normally-run code. (That way, this script skips a lot of
unnecessary unindexation requests.)

This script processes batches of 1.000 offers (note that HTTP requests
to App Search cannot have include more than 100 offers) and reports
back every 10.000 offers.

Errors are logged and are not blocking. You can see the batch that
failed in the logs and should re-run any batch that failed.

Obviously, the script takes a lot of time. You should run multiple
instances of it at the same time.

Usage:

    $ python full_index_offers.py 10 10_000_000
    $ python full_index_offers.py 10_000_000 20_000_000

Using "_" as thousands separator is supported.
"""
# isort:skip_file
from pcapi.flask_app import app

app.app_context().push()

import argparse
import datetime
import logging
import statistics
import time

import pytz
from sqlalchemy.orm import joinedload

from pcapi.core.search.backends import appsearch
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.models as offers_models


appsearch.AppSearchBackend.unindex_offer_ids = lambda *args, **kwargs: 1

BATCH_SIZE = 1_000
REPORT_EVERY = 10_000

logger = logging.getLogger(__name__)


def _get_eta(end, current, elapsed_per_batch):
    left_to_do = end - current
    eta = left_to_do / BATCH_SIZE * statistics.mean(elapsed_per_batch)
    eta = datetime.datetime.now() + datetime.timedelta(seconds=eta)
    eta = eta.astimezone(pytz.timezone("Europe/Paris"))
    eta = eta.strftime("%d/%m/%Y %H:%M:%S")
    return eta


def full_index_offers(start, end):
    backend = appsearch.AppSearchBackend()

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
            .filter(offers_models.Offer.isActive == True, offers_models.Offer.id.between(start, start + BATCH_SIZE))
            .order_by(offers_models.Offer.id)
        )
        for offer in offers:
            if offer.isBookable:
                enqueue_or_index(queue, offer)
        elapsed_per_batch.append(int(time.perf_counter() - start_time))
        start = start + BATCH_SIZE
        eta = _get_eta(end, start, elapsed_per_batch)
        to_report += BATCH_SIZE
        if to_report > REPORT_EVERY:
            to_report = 0
            print(f"  => OK: {start} | eta = {eta}")
    enqueue_or_index(queue, offer=None, force_index=True)


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("start", type=int, help="Offer id to start from (included)")
    parser.add_argument("end", type=int, help="Offer id to end to (included)")
    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()
    assert args.start <= args.end
    full_index_offers(args.start, args.end)


if __name__ == "__main__":
    main()

"""Reindex all bookable offers.

The script iterates over all active offers. For each offer, it indexes
it on App Search if the offer is bookable. Otherwise, the offer is NOT
unindexed, as we suppose that the offer has already been unindexed
through the normally-run code. (That way, this script skips a lot of
unnecessary unindexation requests.)

This script processes batches of 1.000 offers (note that HTTP requests
to App Search cannot have include more than 100 offers) and report
back every 10.000 offers.

Errors are logged and are not blocking. You can see the batch that
failed in the logs and should re-run any batch that failed.

Obviously, the script takes a lot of time. You can run multiple
instances of it at the same time.

Usage:

    $ python full_index_offers.py asc  # starts from 1 until half of the table
    $ python full_index_offers.py desc # starts from max(id) until half of the table

FIXME (dbaty, 2021-07-22): The script should probably be adapted to
let the user specify the lower and upper bounds, to run more than 2
instances of the script, something like:

    <script> --start 1 --end 10000000
    <script> --start 10000000 --end 20000000
    <script> --start 20000000 --end 30000000
    <script> --start 30000000 --end 40000000
... or something like that.

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
from sqlalchemy import func
from sqlalchemy.orm import joinedload

from pcapi.core.search.backends import appsearch
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.models as offers_models
from pcapi.models import db


appsearch.AppSearchBackend.unindex_offer_ids = lambda *args, **kwargs: 1

BATCH_SIZE = 1_000
REPORT_EVERY = 10_000

logger = logging.getLogger(__name__)


def full_index_offers(direction, batch_start=None):
    backend = appsearch.AppSearchBackend()

    queue = []

    def enqueue_or_index(q, offer, force_index=False):
        if offer:
            q.append(offer)
        if force_index or len(q) > BATCH_SIZE:
            try:
                backend.index_offers(q)
            except Exception as exc:  # pylint: disable=broad-except
                # FIXME (dbaty): bug here. We don't fetch offers
                # sorted by their id, so the lower and upper bounds
                # are not necessarily in `q[0]` and `q[-1]`. We should
                # rather use `min(o.id for o in q)` and `max(o.id for o in q)`.
                logger.error(
                    "Full offer reindexation: error while reindexing from %d to %d: %s", q[0].id, q[-1].id, exc
                )
            q.clear()

    max_id = db.session.query(func.max(offers_models.Offer.id)).scalar()
    if direction == "asc":
        batch_start = batch_start or 1
        break_condition = lambda current_position: current_position > max_id / 2
        get_batch_range = lambda current_position: (current_position, current_position + BATCH_SIZE)
        get_left_to_do = lambda current_position: (max_id / 2) - current_position
    else:
        batch_start = batch_start or max_id
        break_condition = lambda current_position: current_position < max_id / 2
        get_batch_range = lambda current_position: (current_position, current_position - BATCH_SIZE)
        get_left_to_do = lambda current_position: current_position - (max_id / 2)

    to_report = 0
    elapsed_per_batch = []

    while not break_condition(batch_start):
        start_time = time.perf_counter()
        batch_range = get_batch_range(batch_start)
        offers = (
            offers_models.Offer.query.options(
                joinedload(offers_models.Offer.venue).joinedload(offerers_models.Venue.managingOfferer)
            )
            .options(joinedload(offers_models.Offer.criteria))
            .options(joinedload(offers_models.Offer.mediations))
            .options(joinedload(offers_models.Offer.product))
            .options(joinedload(offers_models.Offer.stocks))
            .filter(offers_models.Offer.isActive == True, offers_models.Offer.id.between(*batch_range, symmetric=True))
        )
        for offer in offers:
            if offer.isBookable:
                enqueue_or_index(queue, offer)
        batch_start = batch_range[1]
        elapsed_per_batch.append(int(time.perf_counter() - start_time))
        left_to_do = get_left_to_do(batch_start)
        eta = left_to_do / BATCH_SIZE * statistics.mean(elapsed_per_batch)
        eta = datetime.datetime.now() + datetime.timedelta(seconds=eta)
        eta = eta.astimezone(pytz.timezone("Europe/Paris"))
        eta = eta.strftime("%d/%m/%Y %H:%M:%S")
        to_report += BATCH_SIZE
        if to_report > REPORT_EVERY:
            to_report = 0
            print(f"  => OK: {batch_start} | eta = {eta}")
    enqueue_or_index(queue, offer=None, force_index=True)


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("direction", choices=["asc", "desc"])
    parser.add_argument("--start", type=int, default=None)
    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()
    full_index_offers(args.direction, args.start)


if __name__ == "__main__":
    main()

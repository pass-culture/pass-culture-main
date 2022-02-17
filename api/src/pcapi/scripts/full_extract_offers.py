import datetime
from decimal import Decimal
import json
import logging
import statistics
import time
from typing import Iterable

import click
import pytz
from sqlalchemy.orm import joinedload

import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.models as offers_models
from pcapi.core.search.backends import algolia
from pcapi.core.users import utils
from pcapi.utils.blueprint import Blueprint


# FIXME (apibrac, 2022-01-12): remove this file once the extract is done


BATCH_SIZE = 1_000
REPORT_EVERY = 10_000

logger = logging.getLogger(__name__)
blueprint = Blueprint(__name__, __name__)


folder_name = "extracted_offers"


def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


def save_offers(operation_id, offers: Iterable[offers_models.Offer]) -> None:
    serialized_offers = [
        json.dumps(algolia.AlgoliaBackend.serialize_offer(offer), default=decimal_default) for offer in offers
    ]
    serialized_offers.append("")  # Adds an empty line at the end of the file. Essential for file composition.
    file_content = "\n".join(serialized_offers)

    print(file_content)

    utils.store_object(folder_name, operation_id, file_content)


def _get_eta(end, current, elapsed_per_batch):
    left_to_do = end - current
    eta = left_to_do / BATCH_SIZE * statistics.mean(elapsed_per_batch)
    eta = datetime.datetime.now() + datetime.timedelta(seconds=eta)
    eta = eta.astimezone(pytz.timezone("Europe/Paris"))
    eta = eta.strftime("%d/%m/%Y %H:%M:%S")
    return eta


@blueprint.cli.command("full_extract_offers")
@click.argument("start", type=int, required=True)
@click.argument("end", type=int, required=True)
def full_extract_offers(start, end):
    """Extract all bookable offers.

    The script is a copy of "full_index_offers" except that
    it doesn't index offeres but write them in a bucket instead.

    Usage:

        $ flask full_extract_offers.py 10_000_000 20_000_000

    Using "_" as thousands separator is supported (and encouraged for
    clarity).
    """
    if start > end:
        raise ValueError('"start" must be less than "end"')

    queue = []
    operation_id = str(start) + "_" + str(end)

    def enqueue_or_index(q, offer, force_index=False):
        if offer:
            q.append(offer)
        if force_index:
            try:
                save_offers(operation_id, q)
            except Exception as exc:  # pylint: disable=broad-except
                logger.exception(
                    "Full offer extraction: error while extracting from %d to %d: %s", q[0].id, q[-1].id, exc
                )

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

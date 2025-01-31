import logging
import time
import typing

from pcapi.app import app
from pcapi.core import search
from pcapi.core.categories import subcategories_v2
from pcapi.core.offers.models import Offer


BATCH_SIZE = 1000

logger = logging.getLogger(__name__)


def get_offer_ids() -> typing.Generator[list, None, None]:
    query = Offer.query.filter(
        Offer.subcategoryId.in_(subcategories_v2.MUSIC_SUBCATEGORIES), Offer.isActive.is_(True)
    ).with_entities(Offer.id)
    yield from query.yield_per(BATCH_SIZE)


def reindex_seance_cine_offers() -> None:
    batch = []
    start_time = time.time()
    prev_time = start_time
    for (offer_id,) in get_offer_ids():
        batch.append(offer_id)
        if len(batch) >= BATCH_SIZE:
            search.reindex_offer_ids(batch)
            next_time = time.time()
            logger.info(f"Batch loaded in {next_time - prev_time:.3f}s")
            prev_time = next_time
            batch = []

    search.reindex_offer_ids(batch)
    logger.info(f"Total in {time.time() - start_time:.2f}s")


with app.app_context():
    reindex_seance_cine_offers()

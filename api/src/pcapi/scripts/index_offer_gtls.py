import time

from sqlalchemy import func
from pcapi.app import app

from pcapi.core.offers.models import Offer
from pcapi.core.search import IndexationReason
from pcapi.core.search import async_index_offer_ids
from pcapi.repository import db


BATCH_SIZE = 1_000


def _log_time(current: int, end: int, start_time: float) -> None:
    if not current or not end:
        return

    ellapsed_time = time.time() - start_time
    print(
        f"{current} / {end} ({current / end * 100:.2f}%) - "
        f"Ellapsed time: {ellapsed_time:.2f}s - ETA {ellapsed_time / (current / end):.2f}s"
    )


def get_offer_batch(from_id: int, to_id: int) -> list[int]:
    return [
        offer_id[0]
        for offer_id in Offer.query.filter(
            Offer.id.between(from_id, to_id), Offer.extraData["gtl_id"].is_not(None), Offer.isActive.is_(True)
        ).with_entities(Offer.id)
    ]


def index_offers_with_gtl(dry_run: bool = True) -> None:
    start_time = time.time()
    total_offers_to_index = 0
    end_id = db.session.query(func.max(Offer.id)).scalar()
    for from_id in range(0, end_id, BATCH_SIZE):
        _log_time(from_id, end_id, start_time)
        batch = get_offer_batch(from_id, from_id + BATCH_SIZE)
        total_offers_to_index += len(batch)
        print(
            f"{len(batch)} offers between {from_id} and {from_id + BATCH_SIZE} to index. Total: {total_offers_to_index}"
        )
        if not dry_run:
            async_index_offer_ids(batch, IndexationReason.OFFER_BATCH_UPDATE)


with app.app_context():
    index_offers_with_gtl(dry_run=False)

import logging
from typing import Iterable

from pcapi.core import search
from pcapi.core.offers.models import Offer
from pcapi.models import db


logger = logging.getLogger(__name__)


def process_batch(offer_ids: list[str]) -> None:
    logger.info("Bulk-deactivating offers as incompatible", extra={"offers": offer_ids})
    offers = Offer.query.filter(Offer.id.in_(offer_ids))
    offer_ids = [offer_id for offer_id, in offers.with_entities(Offer.id)]
    offers.update({"isActive": False}, synchronize_session=False)
    db.session.commit()
    search.unindex_offer_ids(offer_ids)  # type: ignore[arg-type]


def bulk_inactivate_offers(iterable: Iterable[str], batch_size: int) -> None:
    total = 0
    batch = []

    for line in iterable:
        offer_id = line.strip()
        batch.append(offer_id)
        total += 1
        if len(batch) == batch_size:
            process_batch(batch)
            batch = []
            print("Count: %i", total)
    process_batch(batch)
    print("Count: %i", total)


def bulk_mark_incompatible_from_path(path: str, batch_size: int) -> None:
    with open(path, encoding="utf-8") as fp:
        return bulk_inactivate_offers(fp, batch_size)

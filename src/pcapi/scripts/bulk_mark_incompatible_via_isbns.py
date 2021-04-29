import logging
from typing import Iterable

from pcapi.algolia.usecase.orchestrator import _process_deleting
from pcapi.core.offers.models import Offer
from pcapi.flask_app import app
from pcapi.models import Product
from pcapi.models.db import db
from pcapi.models.feature import FeatureToggle
from pcapi.repository import feature_queries


logger = logging.getLogger(__name__)


def process_batch(isbns: list[str], synchronize_algolia: bool) -> None:
    logger.info("Bulk-marking products as incompatible", extra={"isbns": isbns})
    products = Product.query.filter(Product.extraData["isbn"].astext.in_(isbns))
    products.update({"isGcuCompatible": False}, synchronize_session=False)
    offers = Offer.query.filter(Offer.productId.in_(products.with_entities(Product.id)))
    offer_ids = [offer_id for offer_id, in offers.with_entities(Offer.id)]
    offers.update({"isActive": False}, synchronize_session=False)
    db.session.commit()
    if synchronize_algolia:
        _process_deleting(app.redis_client, offer_ids)


def bulk_mark_incompatible_via_isbns(iterable: Iterable[str], batch_size: int) -> None:
    total = 0
    batch = []
    synchronize_algolia = feature_queries.is_active(FeatureToggle.SYNCHRONIZE_ALGOLIA)

    for line in iterable:
        isbn = line.strip()
        batch.append(isbn)
        total += 1
        if len(batch) == batch_size:
            process_batch(batch, synchronize_algolia)
            batch = []
            print("Count: %i", total)
    process_batch(batch, synchronize_algolia)
    print("Count: %i", total)


def bulk_mark_incompatible_from_path(path: str, batch_size: int) -> None:
    with open(path) as fp:
        return bulk_mark_incompatible_via_isbns(fp, batch_size)

from typing import Iterable

from pcapi.core.offers import models as offers_models
from pcapi.models import db


CHUNK = 0
CHUNK_SIZE = 1000

TOTAL_PRODUCTS_ROWS = products_to_delete = offers_models.Product.query.filter(
    offers_models.Product.extraData["ean"].astext.is_not(None), offers_models.Product.owningOffererId.is_not(None)
).count()

MAX_CHUNKS = TOTAL_PRODUCTS_ROWS / CHUNK_SIZE

while CHUNK < MAX_CHUNKS:
    products_to_delete = (
        offers_models.Product.query.filter(
            offers_models.Product.extraData["ean"].astext.is_not(None),
            offers_models.Product.owningOffererId.is_not(None),
        )
        .offset(CHUNK * CHUNK_SIZE)
        .limit(CHUNK_SIZE)
        .all()
    )

    offers: Iterable[offers_models.Offer] = [product.offers for product in products_to_delete]

    for offer in offers:
        offer.productId = None

    db.session.bulk_save_objects(offers)
    products_to_delete.delete()
    db.session.commit()

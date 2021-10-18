import logging
from typing import Iterable

from pcapi.core import search
from pcapi.core.offers.models import Offer
from pcapi.models import Product
from pcapi.models.db import db


logger = logging.getLogger(__name__)


def process_batch(isbns: list[str], is_compatible: bool) -> None:
    logger.info("Bulk-update products isGcuCompatible=%s", is_compatible, extra={"isbns": isbns})
    products = Product.query.filter(Product.extraData["isbn"].astext.in_(isbns))
    updated_products_count = products.update({"isGcuCompatible": is_compatible}, synchronize_session=False)
    offer_ids = []
    updated_offers_count = 0
    if not is_compatible:
        offers = Offer.query.filter(Offer.productId.in_(products.with_entities(Product.id)))
        offer_ids = [offer_id for offer_id, in offers.with_entities(Offer.id)]
        updated_offers_count = offers.update({"isActive": False}, synchronize_session=False)
    db.session.commit()
    if offer_ids:
        search.unindex_offer_ids(offer_ids)
    logger.info(
        "Finished bulk-update products isGcuCompatible=%s",
        is_compatible,
        extra={
            "isbns": isbns,
            "updated_products_count": updated_products_count,
            "updated_offers_count": updated_offers_count,
        },
    )


def bulk_update_is_gcu_compatible_via_isbns(iterable: Iterable[str], batch_size: int, is_compatible: bool) -> None:
    total = 0
    batch = []

    for line in iterable:
        isbn = line.strip()
        batch.append(isbn)
        total += 1
        if len(batch) == batch_size:
            process_batch(batch, is_compatible=is_compatible)
            batch = []
            print("Count: %i", total)
    if batch:
        process_batch(batch, is_compatible=is_compatible)
        print("Count: %i", total)


def bulk_mark_incompatible_from_path(path: str, batch_size: int) -> None:
    """Script à lancer en passant en premier paramètre le path d'un fichier csv avec une colonne contenant les isbns
    à désactiver"""
    with open(path) as fp:
        return bulk_update_is_gcu_compatible_via_isbns(fp, batch_size, is_compatible=False)


def bulk_mark_compatible_from_path(path: str, batch_size: int) -> None:
    """Script à lancer en passant en premier paramètre le path d'un fichier csv avec une colonne contenant les isbns
    à activer"""
    with open(path) as fp:
        return bulk_update_is_gcu_compatible_via_isbns(fp, batch_size, is_compatible=True)

import logging
from typing import Iterable

from pcapi.core import search
import pcapi.core.offers.models as offers_models
from pcapi.models import db


logger = logging.getLogger(__name__)


def process_batch(isbns: list[str], is_compatible: bool) -> None:
    logger.info("Bulk-update products isGcuCompatible=%s", is_compatible, extra={"isbns": isbns})
    products = offers_models.Product.query.filter(offers_models.Product.extraData["isbn"].astext.in_(isbns))
    updated_products_count = products.update({"isGcuCompatible": is_compatible}, synchronize_session=False)
    offer_ids = []
    updated_offers_count = 0
    if not is_compatible:
        offers = offers_models.Offer.query.filter(
            offers_models.Offer.productId.in_(products.with_entities(offers_models.Product.id))
        )
        offer_ids = [offer_id for offer_id, in offers.with_entities(offers_models.Offer.id)]
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
    with open(path, encoding="utf-8") as fp:
        return bulk_update_is_gcu_compatible_via_isbns(fp, batch_size, is_compatible=False)


def bulk_mark_compatible_from_path(path: str, batch_size: int) -> None:
    """Script à lancer en passant en premier paramètre le path d'un fichier csv avec une colonne contenant les isbns
    à activer"""
    with open(path, encoding="utf-8") as fp:
        return bulk_update_is_gcu_compatible_via_isbns(fp, batch_size, is_compatible=True)

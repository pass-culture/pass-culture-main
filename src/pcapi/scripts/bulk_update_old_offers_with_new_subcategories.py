from sqlalchemy.orm import Query

from pcapi.core.categories.conf import get_subcategory_from_type
from pcapi.models import Offer
from pcapi.repository import repository


def bulk_update_old_offers_with_new_subcategories(batch_size: int = 10000) -> None:
    empty_subcategory_offers = find_empty_subcategory_offers().limit(batch_size).all()

    while empty_subcategory_offers:
        for offer in empty_subcategory_offers:
            offer.subcategoryId = get_subcategory_from_type(offer.type, offer.isDigital)
        repository.save(*empty_subcategory_offers)
        empty_subcategory_offers = find_empty_subcategory_offers().limit(batch_size).all()


def find_empty_subcategory_offers() -> Query:
    return Offer.query.filter(Offer.subcategoryId.is_(None))

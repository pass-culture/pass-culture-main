from typing import Optional

from pcapi.core.categories import subcategories
import pcapi.core.offers.repository as offers_repository
from pcapi.core.users.repository import get_favorites_for_offers
from pcapi.domain.offers import update_is_active_status
from pcapi.models import Booking
from pcapi.models import Offer
from pcapi.models import Product
from pcapi.models import Stock
from pcapi.repository import repository
from pcapi.repository.mediation_queries import get_mediations_for_offers
from pcapi.repository.offer_queries import get_offers_by_product_id


class ProductWithBookingsException(Exception):
    pass


def delete_unwanted_existing_product(isbn: str):
    product_has_at_least_one_booking = (
        Product.query.filter_by(idAtProviders=isbn).join(Offer).join(Stock).join(Booking).count() > 0
    )
    product = find_active_book_product_by_isbn(isbn)

    if not product:
        return

    if product_has_at_least_one_booking:
        offers = get_offers_by_product_id(product.id)
        product.isGcuCompatible = False
        product.isSynchronizationCompatible = False
        offers = update_is_active_status(offers, False)
        repository.save(*offers, product)
        raise ProductWithBookingsException

    objects_to_delete = []
    objects_to_delete.append(product)
    offers = get_offers_by_product_id(product.id)
    offer_ids = [offer.id for offer in offers]
    objects_to_delete = objects_to_delete + offers
    stocks = offers_repository.get_stocks_for_offers(offer_ids)
    objects_to_delete = objects_to_delete + stocks
    mediations = get_mediations_for_offers(offer_ids)
    objects_to_delete = objects_to_delete + mediations
    favorites = get_favorites_for_offers(offer_ids)
    objects_to_delete = objects_to_delete + favorites
    repository.delete(*objects_to_delete)


def find_active_book_product_by_isbn(isbn: str) -> Optional[Product]:
    return (
        Product.query.filter(Product.can_be_synchronized)
        .filter(Product.subcategoryId == subcategories.LIVRE_PAPIER.id)
        .filter(Product.idAtProviders == isbn)
        .one_or_none()
    )

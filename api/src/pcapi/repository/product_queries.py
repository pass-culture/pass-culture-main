import pcapi.core.bookings.models as bookings_models
from pcapi.core.categories import subcategories
import pcapi.core.offers.models as offers_models
import pcapi.core.offers.repository as offers_repository
from pcapi.core.users.repository import get_favorites_for_offers
from pcapi.models import db
from pcapi.repository import repository
from pcapi.repository.mediation_queries import get_mediations_for_offers
from pcapi.repository.offer_queries import get_offers_by_product_id


class ProductWithBookingsException(Exception):
    pass


def delete_unwanted_existing_product(isbn: str) -> None:
    product_has_at_least_one_booking = (
        offers_models.Product.query.filter_by(idAtProviders=isbn)
        .join(offers_models.Offer)
        .join(offers_models.Stock)
        .join(bookings_models.Booking)
        .count()
        > 0
    )
    product = find_active_book_product_by_isbn(isbn)

    if not product:
        return

    if product_has_at_least_one_booking:
        offers = offers_models.Offer.query.filter_by(productId=product.id)
        offers.update({"isActive": False}, synchronize_session=False)
        db.session.commit()
        product.isGcuCompatible = False
        product.isSynchronizationCompatible = False
        repository.save(product)
        raise ProductWithBookingsException()

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


def find_active_book_product_by_isbn(isbn: str) -> offers_models.Product | None:
    return (
        offers_models.Product.query.filter(offers_models.Product.can_be_synchronized)
        .filter_by(subcategoryId=subcategories.LIVRE_PAPIER.id)
        .filter_by(idAtProviders=isbn)
        .one_or_none()
    )

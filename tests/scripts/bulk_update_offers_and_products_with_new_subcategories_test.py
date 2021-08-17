import pytest

from pcapi.core.offers.factories import OfferFactory
from pcapi.core.offers.factories import ProductFactory
from pcapi.core.offers.models import Offer
from pcapi.models import Product
from pcapi.models import db
from pcapi.scripts.bulk_update_offers_and_products_with_new_subcategories import (
    bulk_update_old_offers_with_new_subcategories,
)
from pcapi.scripts.bulk_update_offers_and_products_with_new_subcategories import bulk_update_products_with_subcategories


class UpdateOffersSubcatTest:
    @pytest.mark.usefixtures("db_session")
    def test_update_offers_subcategory(self):
        # Given
        book_offers = OfferFactory.create_batch(size=3)
        for offer in book_offers:
            offer.subcategoryId = None
            offer.type = "ThingType.LIVRE_EDITION"
            db.session.add(offer)
        digital_book_offer = OfferFactory(url="http://moncatalogue.com/123")
        digital_book_offer.subcategoryId = None
        digital_book_offer.type = "ThingType.LIVRE_EDITION"
        db.session.add(digital_book_offer)
        concert_offers = OfferFactory.create_batch(size=2)
        for offer in concert_offers:
            offer.subcategoryId = None
            offer.type = "EventType.MUSIQUE"
            db.session.add(offer)
        db.session.commit()

        # When
        bulk_update_old_offers_with_new_subcategories()

        # Then
        assert Offer.query.filter(Offer.subcategoryId == "LIVRE_PAPIER").count() == 3
        assert Offer.query.filter(Offer.subcategoryId == "LIVRE_NUMERIQUE").count() == 1
        assert Offer.query.filter(Offer.subcategoryId == "CONCERT").count() == 2


class UpdateProductsSubcatTest:
    @pytest.mark.usefixtures("db_session")
    def test_update_products_subcategory(self):
        # Given
        book_products = ProductFactory.create_batch(size=3)
        for product in book_products:
            product.subcategoryId = None
            product.type = "ThingType.LIVRE_EDITION"
            db.session.add(product)
        digital_book_product = ProductFactory(url="http://moncatalogue.com/123")
        digital_book_product.subcategoryId = None
        digital_book_product.type = "ThingType.LIVRE_EDITION"
        db.session.add(digital_book_product)
        concert_products = ProductFactory.create_batch(size=2, url="http://moncatalogue.com/123")
        for product in concert_products:
            product.subcategoryId = None
            product.type = "EventType.MUSIQUE"
            db.session.add(product)
        db.session.commit()

        # When
        bulk_update_products_with_subcategories()

        # Then
        assert Product.query.filter(Product.subcategoryId == "LIVRE_PAPIER").count() == 3
        assert Product.query.filter(Product.subcategoryId == "LIVRE_NUMERIQUE").count() == 1
        assert Product.query.filter(Product.subcategoryId == "CONCERT").count() == 2

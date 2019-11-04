import pytest

from models import Product, PcObject, Offer, Stock, Mediation, Recommendation, Favorite
from repository.product_queries import delete_unwanted_existing_product
from tests.conftest import clean_database
from tests.test_utils import create_product_with_thing_type, create_offerer, create_venue, \
    create_offer_with_thing_product, create_stock, create_booking, create_user, create_recommendation, create_mediation, \
    create_favorite


class DeleteUnwantedExistingProductTest:
    @clean_database
    def test_should_delete_product_when_isbn_found(self, app):
        # Given
        isbn = '1111111111111'
        product = create_product_with_thing_type(id_at_providers=isbn)
        PcObject.save(product)

        # When
        delete_unwanted_existing_product('1111111111111')

        # Then
        assert Product.query.count() == 0

    @clean_database
    def test_should_not_delete_product_when_isbn_not_found(self, app):
        # Given
        isbn = '1111111111111'
        product = create_product_with_thing_type(id_at_providers=isbn)
        PcObject.save(product)

        # When
        delete_unwanted_existing_product('2222222222222')

        # Then
        assert Product.query.count() == 1

    @clean_database
    def test_should_delete_product_when_it_has_offers_but_no_stocks_and_no_booking(self, app):
        # Given
        isbn = '1111111111111'
        offerer = create_offerer(siren='775671464')
        venue = create_venue(offerer, name='Librairie Titelive', siret='77567146400110')
        product = create_product_with_thing_type(id_at_providers=isbn)
        offer = create_offer_with_thing_product(venue, product=product)
        PcObject.save(venue, product, offer)

        # When
        delete_unwanted_existing_product('1111111111111')

        # Then
        assert Product.query.count() == 0
        assert Offer.query.count() == 0

    @clean_database
    def test_should_delete_product_when_it_has_offer_and_stock_but_not_booked(self, app):
        # Given
        isbn = '1111111111111'
        offerer = create_offerer(siren='775671464')
        venue = create_venue(offerer, name='Librairie Titelive', siret='77567146400110')
        product = create_product_with_thing_type(id_at_providers=isbn)
        offer = create_offer_with_thing_product(venue, product=product)
        stock = create_stock(offer=offer, price=0)
        PcObject.save(venue, product, offer, stock)

        # When
        delete_unwanted_existing_product('1111111111111')

        # Then
        assert Product.query.count() == 0
        assert Offer.query.count() == 0
        assert Stock.query.count() == 0

    @clean_database
    def test_should_not_delete_product_when_bookings_related_to_offer(self, app):
        # Given
        isbn = '1111111111111'
        user = create_user()
        offerer = create_offerer(siren='775671464')
        venue = create_venue(offerer, name='Librairie Titelive', siret='77567146400110')
        product = create_product_with_thing_type(id_at_providers=isbn)
        offer = create_offer_with_thing_product(venue, product=product)
        stock = create_stock(offer=offer, price=0)
        booking = create_booking(user=user, stock=stock)
        PcObject.save(venue, product, offer, stock, booking, user)

        # When
        with pytest.raises(Exception):
            delete_unwanted_existing_product('1111111111111')

        # Then
        assert Product.query.one() == product

    @clean_database
    def test_should_delete_product_when_related_offer_is_on_user_favorite_list(self, app):
        # Given
        isbn = '1111111111111'
        user = create_user()
        offerer = create_offerer(siren='775671464')
        venue = create_venue(offerer, name='Librairie Titelive', siret='77567146400110')
        product = create_product_with_thing_type(id_at_providers=isbn)
        offer = create_offer_with_thing_product(venue, product=product)
        stock = create_stock(offer=offer, price=0)
        mediation = create_mediation(offer=offer)
        recommendation = create_recommendation(offer=offer, user=user, mediation=mediation)
        favorite = create_favorite(mediation=mediation, offer=offer, user=user)

        PcObject.save(venue, product, offer, stock, user, mediation, recommendation, favorite)

        # When
        delete_unwanted_existing_product('1111111111111')

        # Then
        assert Product.query.count() == 0
        assert Offer.query.count() == 0
        assert Stock.query.count() == 0
        assert Mediation.query.count() == 0
        assert Recommendation.query.count() == 0
        assert Favorite.query.count() == 0

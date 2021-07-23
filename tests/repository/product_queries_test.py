import pytest

from pcapi.core.offers.models import Mediation
from pcapi.core.users import factories as users_factories
from pcapi.model_creators.generic_creators import create_booking
from pcapi.model_creators.generic_creators import create_favorite
from pcapi.model_creators.generic_creators import create_mediation
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_stock
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.model_creators.specific_creators import create_product_with_thing_type
from pcapi.models import Favorite
from pcapi.models import Offer
from pcapi.models import Product
from pcapi.models import Stock
from pcapi.models.offer_type import ThingType
from pcapi.repository import repository
from pcapi.repository.product_queries import delete_unwanted_existing_product
from pcapi.repository.product_queries import find_active_book_product_by_isbn


class DeleteUnwantedExistingProductTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_delete_product_when_isbn_found(self, app):
        # Given
        isbn = "1111111111111"
        product = create_product_with_thing_type(id_at_providers=isbn)
        repository.save(product)

        # When
        delete_unwanted_existing_product("1111111111111")

        # Then
        assert Product.query.count() == 0

    @pytest.mark.usefixtures("db_session")
    def test_should_not_delete_product_when_isbn_not_found(self, app):
        # Given
        isbn = "1111111111111"
        product = create_product_with_thing_type(id_at_providers=isbn)
        repository.save(product)

        # When
        delete_unwanted_existing_product("2222222222222")

        # Then
        assert Product.query.count() == 1

    @pytest.mark.usefixtures("db_session")
    def test_should_delete_nothing_when_product_not_found(self, app):
        # Given
        isbn = "1111111111111"
        product = create_product_with_thing_type(
            id_at_providers=isbn,
            is_gcu_compatible=False,
            thing_type=ThingType.LIVRE_EDITION,
        )
        repository.save(product)

        # When
        delete_unwanted_existing_product(isbn)

        # Then
        assert Product.query.count() == 1

    @pytest.mark.usefixtures("db_session")
    def test_should_delete_product_when_it_has_offer_and_stock_but_not_booked(self, app):
        # Given
        isbn = "1111111111111"
        offerer = create_offerer(siren="775671464")
        venue = create_venue(offerer, name="Librairie Titelive", siret="77567146400110")
        product = create_product_with_thing_type(id_at_providers=isbn)
        offer = create_offer_with_thing_product(venue, product=product)
        stock = create_stock(offer=offer, price=0)
        repository.save(venue, product, offer, stock)

        # When
        delete_unwanted_existing_product("1111111111111")

        # Then
        assert Product.query.count() == 0
        assert Offer.query.count() == 0
        assert Stock.query.count() == 0

    @pytest.mark.usefixtures("db_session")
    def test_should_set_isGcuCompatible_at_false_in_product_and_deactivate_offer_when_bookings_related_to_offer(
        self, app
    ):
        # Given
        isbn = "1111111111111"
        user = users_factories.UserFactory()
        offerer = create_offerer(siren="775671464")
        venue = create_venue(offerer, name="Librairie Titelive", siret="77567146400110")
        product = create_product_with_thing_type(id_at_providers=isbn, is_gcu_compatible=True)
        offer = create_offer_with_thing_product(venue, product=product, is_active=True)
        stock = create_stock(offer=offer, price=0)
        booking = create_booking(user=user, is_cancelled=True, stock=stock)
        repository.save(venue, product, offer, stock, booking)

        # When
        with pytest.raises(Exception):
            delete_unwanted_existing_product("1111111111111")

        # Then
        offer = Offer.query.one()
        assert offer.isActive is False
        assert Product.query.one() == product
        assert not product.isGcuCompatible

    @pytest.mark.usefixtures("db_session")
    def test_should_delete_product_when_related_offer_has_mediation(self, app):
        # Given
        isbn = "1111111111111"
        user = users_factories.UserFactory()
        offerer = create_offerer(siren="775671464")
        venue = create_venue(offerer, name="Librairie Titelive", siret="77567146400110")
        product = create_product_with_thing_type(id_at_providers=isbn)
        offer = create_offer_with_thing_product(venue, product=product)
        stock = create_stock(offer=offer, price=0)
        mediation = create_mediation(offer=offer)

        repository.save(venue, product, offer, stock, mediation)

        # When
        delete_unwanted_existing_product("1111111111111")

        # Then
        assert Product.query.count() == 0
        assert Offer.query.count() == 0
        assert Stock.query.count() == 0
        assert Mediation.query.count() == 0

    @pytest.mark.usefixtures("db_session")
    def test_should_delete_product_when_related_offer_is_on_user_favorite_list(self, app):
        # Given
        isbn = "1111111111111"
        user = users_factories.UserFactory()
        offerer = create_offerer(siren="775671464")
        venue = create_venue(offerer, name="Librairie Titelive", siret="77567146400110")
        product = create_product_with_thing_type(id_at_providers=isbn)
        offer = create_offer_with_thing_product(venue, product=product)
        stock = create_stock(offer=offer, price=0)
        mediation = create_mediation(offer=offer)
        favorite = create_favorite(mediation=mediation, offer=offer, user=user)

        repository.save(venue, product, offer, stock, mediation, favorite)

        # When
        delete_unwanted_existing_product("1111111111111")

        # Then
        assert Product.query.count() == 0
        assert Offer.query.count() == 0
        assert Stock.query.count() == 0
        assert Mediation.query.count() == 0
        assert Favorite.query.count() == 0


class FindActiveBookProductByIsbnTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_return_active_book_product_when_existing_isbn_is_given(self, app):
        # Given
        isbn = "1111111111111"
        product = create_product_with_thing_type(id_at_providers=isbn, thing_type=ThingType.LIVRE_EDITION)
        repository.save(product)

        # When
        existing_product = find_active_book_product_by_isbn("1111111111111")

        # Then
        assert existing_product == product

    @pytest.mark.usefixtures("db_session")
    def test_should_return_nothing_when_non_existing_isbn_is_given(self, app):
        # Given
        invalid_isbn = "99999999999"
        valid_isbn = "1111111111111"
        product = create_product_with_thing_type(id_at_providers=valid_isbn, thing_type=ThingType.LIVRE_EDITION)
        repository.save(product)

        # When
        existing_product = find_active_book_product_by_isbn(invalid_isbn)

        # Then
        assert existing_product is None

    @pytest.mark.usefixtures("db_session")
    def test_should_not_return_not_gcu_compatible_product(self, app):
        # Given
        valid_isbn = "1111111111111"
        product = create_product_with_thing_type(
            id_at_providers=valid_isbn, thing_type=ThingType.LIVRE_EDITION, is_gcu_compatible=False
        )
        repository.save(product)

        # When
        existing_product = find_active_book_product_by_isbn(valid_isbn)

        # Then
        assert existing_product is None

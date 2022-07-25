import pytest

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.categories import subcategories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.offers.models as offers_models
from pcapi.core.offers.models import Mediation
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.core.users import factories as users_factories
from pcapi.core.users.models import Favorite
from pcapi.repository.product_queries import ProductWithBookingsException
from pcapi.repository.product_queries import delete_unwanted_existing_product
from pcapi.repository.product_queries import find_active_book_product_by_isbn


class DeleteUnwantedExistingProductTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_delete_product_when_isbn_found(self):
        # Given
        isbn = "1111111111111"
        _to_delete = offers_factories.ProductFactory(
            idAtProviders=isbn,
            isSynchronizationCompatible=True,
            subcategoryId=subcategories.LIVRE_PAPIER.id,
        )
        keep_other_isbn = offers_factories.ProductFactory(
            idAtProviders="something-else",
            isSynchronizationCompatible=True,
            subcategoryId=subcategories.LIVRE_PAPIER.id,
        )

        # When
        delete_unwanted_existing_product("1111111111111")

        # Then
        assert offers_models.Product.query.all() == [keep_other_isbn]

    @pytest.mark.usefixtures("db_session")
    def test_should_delete_product_when_it_has_offer_and_stock_but_not_booked(self):
        # Given
        isbn = "1111111111111"
        offers_factories.StockFactory(
            offer__product__idAtProviders=isbn,
            offer__product__subcategoryId=subcategories.LIVRE_PAPIER.id,
        )

        # When
        delete_unwanted_existing_product("1111111111111")

        # Then
        assert offers_models.Product.query.count() == 0
        assert Offer.query.count() == 0
        assert Stock.query.count() == 0

    @pytest.mark.usefixtures("db_session")
    def test_should_set_isGcuCompatible_and_isSynchronizationCompatible_at_false_in_product_and_deactivate_offer_when_bookings_related_to_offer(
        self, app
    ):
        # Given
        isbn = "1111111111111"
        product = offers_factories.ProductFactory(
            idAtProviders=isbn,
            isGcuCompatible=True,
            isSynchronizationCompatible=True,
            subcategoryId=subcategories.LIVRE_PAPIER.id,
        )
        bookings_factories.BookingFactory(stock__offer__product=product)

        # When
        with pytest.raises(ProductWithBookingsException):
            delete_unwanted_existing_product("1111111111111")

        # Then
        offer = Offer.query.one()
        assert offer.isActive is False
        assert offers_models.Product.query.one() == product
        assert not product.isGcuCompatible
        assert not product.isSynchronizationCompatible

    @pytest.mark.usefixtures("db_session")
    def test_should_delete_product_when_related_offer_has_mediation(self, app):
        # Given
        isbn = "1111111111111"
        offer = offers_factories.StockFactory(
            offer__product__idAtProviders=isbn,
            offer__product__subcategoryId=subcategories.LIVRE_PAPIER.id,
        ).offer
        offers_factories.MediationFactory(offer=offer)

        # When
        delete_unwanted_existing_product("1111111111111")

        # Then
        assert offers_models.Product.query.count() == 0
        assert Offer.query.count() == 0
        assert Stock.query.count() == 0
        assert Mediation.query.count() == 0

    @pytest.mark.usefixtures("db_session")
    def test_should_delete_product_when_related_offer_is_on_user_favorite_list(self, app):
        # Given
        isbn = "1111111111111"
        offer = offers_factories.StockFactory(
            offer__product__idAtProviders=isbn,
            offer__product__subcategoryId=subcategories.LIVRE_PAPIER.id,
        ).offer
        users_factories.FavoriteFactory(offer=offer)

        # When
        delete_unwanted_existing_product("1111111111111")

        # Then
        assert offers_models.Product.query.count() == 0
        assert Offer.query.count() == 0
        assert Stock.query.count() == 0
        assert Favorite.query.count() == 0


class FindActiveBookProductByIsbnTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_return_active_book_product_when_existing_isbn_is_given(self, app):
        # Given
        isbn = "1111111111111"
        product = offers_factories.ProductFactory(
            idAtProviders=isbn,
            isGcuCompatible=True,
            isSynchronizationCompatible=True,
            subcategoryId=subcategories.LIVRE_PAPIER.id,
        )

        # When
        existing_product = find_active_book_product_by_isbn(isbn)

        # Then
        assert existing_product == product

    @pytest.mark.usefixtures("db_session")
    def test_should_return_nothing_when_non_existing_isbn_is_given(self, app):
        # Given
        isbn = "1111111111111"
        offers_factories.ProductFactory(
            idAtProviders=isbn,
            isGcuCompatible=True,
            isSynchronizationCompatible=True,
            subcategoryId=subcategories.LIVRE_PAPIER.id,
        )

        # When
        existing_product = find_active_book_product_by_isbn("unknown isbn")

        # Then
        assert existing_product is None

    @pytest.mark.usefixtures("db_session")
    def test_should_not_return_not_gcu_compatible_product(self, app):
        # Given
        isbn = "1111111111111"
        offers_factories.ProductFactory(
            idAtProviders=isbn,
            isGcuCompatible=False,
            isSynchronizationCompatible=True,
            subcategoryId=subcategories.LIVRE_PAPIER.id,
        )

        # When
        existing_product = find_active_book_product_by_isbn(isbn)

        # Then
        assert existing_product is None

    @pytest.mark.usefixtures("db_session")
    def test_should_not_return_not_synchronization_compatible_product(self, app):
        valid_isbn = "1111111111111"
        offers_factories.ProductFactory(
            idAtProviders=valid_isbn,
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            isGcuCompatible=True,
            isSynchronizationCompatible=False,
        )

        existing_product = find_active_book_product_by_isbn(valid_isbn)

        assert existing_product is None

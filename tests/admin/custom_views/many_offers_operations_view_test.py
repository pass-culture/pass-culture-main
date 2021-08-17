from unittest.mock import patch

import pytest

from pcapi.admin.custom_views.many_offers_operations_view import _get_current_criteria_on_active_offers
from pcapi.admin.custom_views.many_offers_operations_view import _get_products_compatible_status
import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.models import Offer
import pcapi.core.users.factories as users_factories
from pcapi.models.criterion import Criterion
from pcapi.models.product import Product

from tests.conftest import TestClient


@pytest.mark.usefixtures("db_session")
class ManyOffersOperationsViewTest:
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_search_product_from_isbn(self, mocked_validate_csrf_token, app):
        # Given
        users_factories.AdminFactory(email="admin@example.com")

        data = dict(isbn="978-3-16-148410-0")

        # When
        client = TestClient(app.test_client()).with_session_auth("admin@example.com")
        response = client.post("/pc/back-office/many_offers_operations/", form=data)

        # Then
        assert response.status_code == 302
        assert (
            response.headers["location"]
            == "http://localhost/pc/back-office/many_offers_operations/edit?isbn=9783161484100"
        )

    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_search_product_from_visa(self, mocked_validate_csrf_token, app):
        # Given
        users_factories.AdminFactory(email="admin@example.com")

        data = dict(visa="978148")

        # When
        client = TestClient(app.test_client()).with_session_auth("admin@example.com")
        response = client.post("/pc/back-office/many_offers_operations/", form=data)

        # Then
        assert response.status_code == 302
        assert response.headers["location"] == "http://localhost/pc/back-office/many_offers_operations/edit?visa=978148"

    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_search_product_from_isbn_with_invalid_isbn(self, mocked_validate_csrf_token, app):
        # Given
        users_factories.AdminFactory(email="admin@example.com")

        data = dict(
            isbn="978-3-16-14840-0",
        )

        # When
        client = TestClient(app.test_client()).with_session_auth("admin@example.com")
        response = client.post("/pc/back-office/many_offers_operations/", form=data)

        # Then
        assert response.status_code == 200

    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_search_product_with_no_isbn_nor_visa(self, mocked_validate_csrf_token, app):
        # Given
        users_factories.AdminFactory(email="admin@example.com")

        data = dict()

        # When
        client = TestClient(app.test_client()).with_session_auth("admin@example.com")
        response = client.post("/pc/back-office/many_offers_operations/", form=data)

        # Then
        assert response.status_code == 200

    @patch("pcapi.core.search.async_index_offer_ids")
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_edit_product_offers_criteria_from_isbn(
        self, mocked_validate_csrf_token, mocked_async_index_offer_ids, app
    ):
        # Given
        users_factories.AdminFactory(email="admin@example.com")
        product = offers_factories.ProductFactory(extraData={"isbn": "9783161484100"})
        offer1 = offers_factories.OfferFactory(product=product, extraData={"isbn": "9783161484100"})
        offer2 = offers_factories.OfferFactory(product=product, extraData={"isbn": "9783161484100"})
        inactive_offer = offers_factories.OfferFactory(
            product=product, extraData={"isbn": "9783161484100"}, isActive=False
        )
        unmatched_offer = offers_factories.OfferFactory()
        criterion1 = offers_factories.CriterionFactory(name="Pretty good books")
        criterion2 = offers_factories.CriterionFactory(name="Other pretty good books")

        data = dict(
            criteria=[criterion1.id, criterion2.id],
        )

        # When
        client = TestClient(app.test_client()).with_session_auth("admin@example.com")
        response = client.post(
            "/pc/back-office/many_offers_operations/add_criteria_to_offers?isbn=9783161484100", form=data
        )

        # Then
        assert response.status_code == 302
        assert response.headers["location"] == "http://localhost/pc/back-office/many_offers_operations/"
        assert offer1.criteria == [criterion1, criterion2]
        assert offer2.criteria == [criterion1, criterion2]
        assert not inactive_offer.criteria
        assert not unmatched_offer.criteria
        mocked_async_index_offer_ids.assert_called_once_with([offer1.id, offer2.id])

    @patch("pcapi.core.search.async_index_offer_ids")
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_edit_product_offers_criteria_from_visa(
        self, mocked_validate_csrf_token, mocked_async_index_offer_ids, app
    ):
        # Given
        users_factories.AdminFactory(email="admin@example.com")
        product = offers_factories.ProductFactory(extraData={"visa": "9783161484100"})
        offer1 = offers_factories.OfferFactory(product=product, extraData={"visa": "9783161484100"})
        offer2 = offers_factories.OfferFactory(product=product, extraData={"visa": "9783161484100"})
        inactive_offer = offers_factories.OfferFactory(
            product=product, extraData={"visa": "9783161484100"}, isActive=False
        )
        unmatched_offer = offers_factories.OfferFactory()
        criterion1 = offers_factories.CriterionFactory(name="Pretty good books")
        criterion2 = offers_factories.CriterionFactory(name="Other pretty good books")

        data = dict(
            criteria=[criterion1.id, criterion2.id],
        )

        # When
        client = TestClient(app.test_client()).with_session_auth("admin@example.com")
        response = client.post(
            "/pc/back-office/many_offers_operations/add_criteria_to_offers?visa=9783161484100", form=data
        )

        # Then
        assert response.status_code == 302
        assert response.headers["location"] == "http://localhost/pc/back-office/many_offers_operations/"
        assert offer1.criteria == [criterion1, criterion2]
        assert offer2.criteria == [criterion1, criterion2]
        assert not inactive_offer.criteria
        assert not unmatched_offer.criteria
        mocked_async_index_offer_ids.called_once_with([offer1.id, offer2.id])

    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_edit_product_offers_criteria_from_isbn_without_offers(self, mocked_validate_csrf_token, app):
        # Given
        users_factories.AdminFactory(email="admin@example.com")

        # When
        client = TestClient(app.test_client()).with_session_auth("admin@example.com")
        response = client.get("/pc/back-office/many_offers_operations/edit?isbn=9783161484100")

        # Then
        assert response.status_code == 302
        assert response.headers["location"] == "http://localhost/pc/back-office/many_offers_operations/"

    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_edit_product_offers_criteria_from_visa_without_offers(self, mocked_validate_csrf_token, app):
        # Given
        users_factories.AdminFactory(email="admin@example.com")

        # When
        client = TestClient(app.test_client()).with_session_auth("admin@example.com")
        response = client.get("/pc/back-office/many_offers_operations/edit?visa=9783161484100")

        # Then
        assert response.status_code == 302
        assert response.headers["location"] == "http://localhost/pc/back-office/many_offers_operations/"

    def test_get_current_criteria_on_active_offers(self):
        # Given
        criterion1 = Criterion(name="One criterion")
        criterion2 = Criterion(name="Another criterion")
        offer1 = Offer(criteria=[criterion1], isActive=True)
        offer2 = Offer(criteria=[criterion1, criterion2], isActive=True)
        offer3 = Offer(criteria=[], isActive=True)
        offer4 = Offer(criteria=[criterion1, criterion2], isActive=False)
        expected_result = {
            "One criterion": {"count": 2, "criterion": criterion1},
            "Another criterion": {"count": 1, "criterion": criterion2},
        }

        # When
        result = _get_current_criteria_on_active_offers([offer1, offer2, offer3, offer4])

        # Then
        assert result == expected_result

    @patch("pcapi.core.search.async_index_offer_ids")
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_edit_product_gcu_compatibility(
        self, mocked_validate_csrf_token, mocked_async_index_offer_ids, app, db_session
    ):
        # Given
        users_factories.AdminFactory(email="admin@example.com")
        offerer = offers_factories.OffererFactory()
        product_1 = offers_factories.ThingProductFactory(
            description="premier produit inapproprié", extraData={"isbn": "isbn-de-test"}
        )
        venue = offers_factories.VenueFactory(managingOfferer=offerer)
        offers_factories.OfferFactory(product=product_1, venue=venue)
        offers_factories.OfferFactory(product=product_1, venue=venue)

        # When
        client = TestClient(app.test_client()).with_session_auth("admin@example.com")
        response = client.post("/pc/back-office/many_offers_operations/product_gcu_compatibility?isbn=isbn-de-test")

        # Then
        assert response.status_code == 302
        assert response.headers["location"] == "http://localhost/pc/back-office/many_offers_operations/"
        products = Product.query.all()
        offers = Offer.query.all()
        first_product = products[0]
        first_offer = offers[0]
        second_offer = offers[1]

        assert not first_product.isGcuCompatible
        assert not first_offer.isActive
        assert not second_offer.isActive
        mocked_async_index_offer_ids.assert_called_once_with([offer.id for offer in offers])

    def test_get_products_compatible_status(self):
        # Given
        products = []
        products.append(Product(isGcuCompatible=True))
        products.append(Product(isGcuCompatible=True))

        # Then
        assert _get_products_compatible_status(products) == {
            "status": "compatible_products",
            "text": "Oui",
        }

        products[0].isGcuCompatible = False
        assert _get_products_compatible_status(products) == {
            "status": "partially_incompatible_products",
            "text": "Partiellement",
        }

        products[1].isGcuCompatible = False
        assert _get_products_compatible_status(products) == {
            "status": "incompatible_products",
            "text": "Non",
        }

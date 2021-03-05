from unittest.mock import patch

from pcapi.admin.custom_views.many_offers_operations_view import _get_current_criteria_on_offers
import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.models import Offer
import pcapi.core.users.factories as users_factories
from pcapi.models.criterion import Criterion

from tests.conftest import TestClient
from tests.conftest import clean_database


class ManyOffersOperationsViewTest:
    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_search_product_from_isbn(self, mocked_validate_csrf_token, app):
        # Given
        users_factories.UserFactory(email="admin@example.com", isAdmin=True)

        data = dict(
            isbn="978-3-16-148410-0",
        )

        # When
        client = TestClient(app.test_client()).with_auth("admin@example.com")
        response = client.post("/pc/back-office/many_offers_operations/", form=data)

        # Then
        assert response.status_code == 302
        assert (
            response.headers["location"]
            == "http://localhost/pc/back-office/many_offers_operations/edit?isbn=9783161484100"
        )

    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_search_product_from_isbn_with_invalid_isbn(self, mocked_validate_csrf_token, app):
        # Given
        users_factories.UserFactory(email="admin@example.com", isAdmin=True)

        data = dict(
            isbn="978-3-16-14840-0",
        )

        # When
        client = TestClient(app.test_client()).with_auth("admin@example.com")
        response = client.post("/pc/back-office/many_offers_operations/", form=data)

        # Then
        assert response.status_code == 200

    @clean_database
    @patch("pcapi.connectors.redis.add_offer_id")
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_edit_product_offers_criteria(self, mocked_validate_csrf_token, mocked_add_offer_id, app):
        # Given
        users_factories.UserFactory(email="admin@example.com", isAdmin=True)
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
        client = TestClient(app.test_client()).with_auth("admin@example.com")
        response = client.post("/pc/back-office/many_offers_operations/edit?isbn=9783161484100", form=data)

        # Then
        assert response.status_code == 302
        assert response.headers["location"] == "http://localhost/pc/back-office/many_offers_operations/"
        assert offer1.criteria == [criterion1, criterion2]
        assert offer2.criteria == [criterion1, criterion2]
        assert not inactive_offer.criteria
        assert not unmatched_offer.criteria
        # fmt: off
        reindexed_offer_ids = {
            mocked_add_offer_id.call_args_list[i][1]["offer_id"]
            for i in range(mocked_add_offer_id.call_count)
        }
        # fmt: on
        assert reindexed_offer_ids == {offer1.id, offer2.id}

    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_edit_product_offers_criteria_without_offers(self, mocked_validate_csrf_token, app):
        # Given
        users_factories.UserFactory(email="admin@example.com", isAdmin=True)
        offers_factories.ProductFactory(extraData={"isbn": "9783161484100"})
        offers_factories.OfferFactory(extraData={"isbn": "9783161484200"})

        # When
        client = TestClient(app.test_client()).with_auth("admin@example.com")
        response = client.get("/pc/back-office/many_offers_operations/edit?isbn=9783161484100")

        # Then
        assert response.status_code == 302
        assert response.headers["location"] == "http://localhost/pc/back-office/many_offers_operations/"

    def test_get_current_criteria_on_offers(self):
        # Given
        criterion1 = Criterion(name="One criterion")
        criterion2 = Criterion(name="Another criterion")
        offer1 = Offer(criteria=[criterion1])
        offer2 = Offer(criteria=[criterion1, criterion2])
        offer3 = Offer(criteria=[])
        expected_result = {
            "One criterion": {"count": 2, "criterion": criterion1},
            "Another criterion": {"count": 1, "criterion": criterion2},
        }

        # When
        result = _get_current_criteria_on_offers(
            [
                offer1,
                offer2,
                offer3,
            ]
        )

        # Then
        assert result == expected_result

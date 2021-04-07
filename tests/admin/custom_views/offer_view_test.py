from unittest.mock import patch

import pytest

from pcapi.admin.custom_views.offer_view import OfferView
import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.models import OfferValidationStatus
import pcapi.core.users.factories as users_factories
from pcapi.models import Offer

from tests.conftest import TestClient


class BeneficiaryUserViewTest:
    def test_max_one_searchable_on_offer_view(self, db_session):
        # Given
        offer_view = OfferView(Offer, db_session)

        # Then
        assert offer_view.column_searchable_list is None or len(offer_view.column_searchable_list) == 0


@pytest.mark.usefixtures("db_session")
class OfferValidationViewTest:
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    @patch("pcapi.admin.custom_views.offer_view.get_offerer_legal_category")
    def test_approve_offer(self, mocked_get_offerer_legal_category, mocked_validate_csrf_token, app):
        users_factories.UserFactory(email="admin@example.com", isAdmin=True)
        offer = offers_factories.OfferFactory(validation=OfferValidationStatus.AWAITING)
        mocked_get_offerer_legal_category.return_value = {
            "legal_category_code": 5202,
            "legal_category_label": "Société en nom collectif",
        }
        data = dict(validation=OfferValidationStatus.APPROVED.value)
        client = TestClient(app.test_client()).with_auth("admin@example.com")
        response = client.post(f"/pc/back-office/validation/edit?id={offer.id}", form=data)

        assert response.status_code == 200
        assert offer.validation == OfferValidationStatus.APPROVED

    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    @patch("pcapi.admin.custom_views.offer_view.get_offerer_legal_category")
    def test_reject_offer(self, mocked_get_offerer_legal_category, mocked_validate_csrf_token, app):
        users_factories.UserFactory(email="admin@example.com", isAdmin=True)
        offer = offers_factories.OfferFactory(validation=OfferValidationStatus.AWAITING, isActive=True)
        mocked_get_offerer_legal_category.return_value = {
            "legal_category_code": 5202,
            "legal_category_label": "Société en nom collectif",
        }
        data = dict(validation=OfferValidationStatus.REJECTED.value)
        client = TestClient(app.test_client()).with_auth("admin@example.com")
        response = client.post(f"/pc/back-office/validation/edit?id={offer.id}", form=data)

        assert response.status_code == 200
        assert offer.validation == OfferValidationStatus.REJECTED
        assert offer.isActive is False

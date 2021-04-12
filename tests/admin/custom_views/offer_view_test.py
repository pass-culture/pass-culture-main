from unittest.mock import patch

import pytest

from pcapi.admin.custom_views.offer_view import OfferView
import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.factories import VenueFactory
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
        offer = offers_factories.OfferFactory(
            validation=OfferValidationStatus.PENDING, venue__bookingEmail="email@example.com"
        )
        mocked_get_offerer_legal_category.return_value = {
            "legal_category_code": 5202,
            "legal_category_label": "Société en nom collectif",
        }
        data = dict(validation=OfferValidationStatus.APPROVED.value, action="save")
        client = TestClient(app.test_client()).with_auth("admin@example.com")
        response = client.post(f"/pc/back-office/validation/edit?id={offer.id}", form=data)

        assert response.status_code == 200
        assert offer.validation == OfferValidationStatus.APPROVED

    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    @patch("pcapi.admin.custom_views.offer_view.get_offerer_legal_category")
    def test_reject_offer(self, mocked_get_offerer_legal_category, mocked_validate_csrf_token, app):
        users_factories.UserFactory(email="admin@example.com", isAdmin=True)
        offer = offers_factories.OfferFactory(
            validation=OfferValidationStatus.PENDING, isActive=True, venue__bookingEmail="email@example.com"
        )

        mocked_get_offerer_legal_category.return_value = {
            "legal_category_code": 5202,
            "legal_category_label": "Société en nom collectif",
        }
        data = dict(validation=OfferValidationStatus.REJECTED.value, action="save")
        client = TestClient(app.test_client()).with_auth("admin@example.com")
        response = client.post(f"/pc/back-office/validation/edit?id={offer.id}", form=data)

        assert response.status_code == 200
        assert offer.validation == OfferValidationStatus.REJECTED
        assert offer.isActive is False

    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    @patch("pcapi.admin.custom_views.offer_view.get_offerer_legal_category")
    def test_approve_offer_and_go_to_next_offer(
        self, mocked_get_offerer_legal_category, mocked_validate_csrf_token, app
    ):
        users_factories.UserFactory(email="admin@example.com", isAdmin=True)
        first_offer = offers_factories.OfferFactory(
            validation=OfferValidationStatus.PENDING, isActive=True, venue__bookingEmail="email1@example.com"
        )
        second_offer = offers_factories.OfferFactory(
            validation=OfferValidationStatus.PENDING, isActive=True, venue__bookingEmail="email2@example.com"
        )

        mocked_get_offerer_legal_category.return_value = {
            "legal_category_code": 5202,
            "legal_category_label": "Société en nom collectif",
        }

        data = dict(validation=OfferValidationStatus.APPROVED.value, action="save-and-go-next")
        client = TestClient(app.test_client()).with_auth("admin@example.com")
        response = client.post(f"/pc/back-office/validation/edit?id={first_offer.id}", form=data)

        assert first_offer.validation == OfferValidationStatus.APPROVED
        assert response.status_code == 302
        assert response.headers["location"] == f"http://localhost/pc/back-office/validation/edit/?id={second_offer.id}"

    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    @patch("pcapi.admin.custom_views.offer_view.get_offerer_legal_category")
    def test_approve_last_pending_offer_and_go_to_the_next_offer_redirect_to_validation_page(
        self, mocked_get_offerer_legal_category, mocked_validate_csrf_token, app
    ):
        users_factories.UserFactory(email="admin@example.com", isAdmin=True)
        offer = offers_factories.OfferFactory(
            validation=OfferValidationStatus.PENDING, isActive=True, venue__bookingEmail="email@example.com"
        )

        mocked_get_offerer_legal_category.return_value = {
            "legal_category_code": 5202,
            "legal_category_label": "Société en nom collectif",
        }

        data = dict(validation=OfferValidationStatus.APPROVED.value, action="save-and-go-next")
        client = TestClient(app.test_client()).with_auth("admin@example.com")
        response = client.post(f"/pc/back-office/validation/edit?id={offer.id}", form=data)

        assert offer.validation == OfferValidationStatus.APPROVED
        assert response.status_code == 302
        assert response.headers["location"] == "http://localhost/pc/back-office/validation/"

    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    @patch("pcapi.admin.custom_views.offer_view.get_offerer_legal_category")
    @patch("pcapi.admin.custom_views.offer_view.send_offer_validation_status_update_email")
    def test_approve_virtual_offer_and_send_mail_to_managing_offerer(
        self,
        mocked_send_offer_validation_status_update_email,
        mocked_get_offerer_legal_category,
        mocked_validate_csrf_token,
        app,
    ):
        # Given
        users_factories.UserFactory(email="admin@example.com", isAdmin=True)

        venue = VenueFactory()
        offerer = venue.managingOfferer
        pro_user = users_factories.UserFactory(email="pro@example.com")
        offers_factories.UserOffererFactory(user=pro_user, offerer=offerer)

        offer = offers_factories.OfferFactory(validation=OfferValidationStatus.PENDING, isActive=True, venue=venue)

        mocked_get_offerer_legal_category.return_value = {
            "legal_category_code": 5202,
            "legal_category_label": "Société en nom collectif",
        }
        data = dict(validation=OfferValidationStatus.APPROVED.value, action="save-and-go-next")
        client = TestClient(app.test_client()).with_auth("admin@example.com")

        # When
        client.post(f"/pc/back-office/validation/edit?id={offer.id}", form=data)

        # Then
        mocked_send_offer_validation_status_update_email.assert_called_once_with(
            offer, OfferValidationStatus.APPROVED, ["pro@example.com"]
        )

    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    @patch("pcapi.admin.custom_views.offer_view.get_offerer_legal_category")
    @patch("pcapi.admin.custom_views.offer_view.send_offer_validation_status_update_email")
    def test_approve_physical_offer_and_send_mail_to_venue_booking_email(
        self,
        mocked_send_offer_validation_status_update_email,
        mocked_get_offerer_legal_category,
        mocked_validate_csrf_token,
        app,
    ):
        # Given
        users_factories.UserFactory(email="admin@example.com", isAdmin=True)

        venue = VenueFactory(bookingEmail="venue@example.com")

        offer = offers_factories.OfferFactory(validation=OfferValidationStatus.PENDING, isActive=True, venue=venue)

        mocked_get_offerer_legal_category.return_value = {
            "legal_category_code": 5202,
            "legal_category_label": "Société en nom collectif",
        }
        data = dict(validation=OfferValidationStatus.APPROVED.value, action="save-and-go-next")
        client = TestClient(app.test_client()).with_auth("admin@example.com")

        # When
        client.post(f"/pc/back-office/validation/edit?id={offer.id}", form=data)

        # Then
        mocked_send_offer_validation_status_update_email.assert_called_once_with(
            offer, OfferValidationStatus.APPROVED, ["venue@example.com"]
        )

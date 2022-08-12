from unittest.mock import patch

import pytest

import pcapi.core.bookings.factories as booking_factories
from pcapi.core.bookings.models import BookingStatus
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offerers.models as offerers_models
from pcapi.core.users import testing as external_testing
import pcapi.core.users.factories as users_factories
from pcapi.models import db

from tests.conftest import clean_database


class OffererViewTest:
    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_edit_offerer_add_tags(self, mocked_validate_csrf_token, client):
        users_factories.AdminFactory(email="admin@example.com")

        offerer = offerers_factories.OffererFactory()
        tag1 = offerers_factories.OffererTagFactory(name="test_tag_1")
        tag2 = offerers_factories.OffererTagFactory(name="test_tag_2")

        api_client = client.with_session_auth("admin@example.com")

        response = api_client.post(
            f"/pc/back-office/offerer/edit/?id={offerer.id}",
            form={
                "name": "Updated offerer",
                "siren": offerer.siren,
                "city": offerer.city,
                "postalCode": offerer.postalCode,
                "address": offerer.address,
                "tags": [tag1.id, tag2.id],  # Add both tags
                "isActive": offerer.isActive,
            },
        )

        assert response.status_code == 302
        db.session.refresh(offerer)
        assert offerer.name == "Updated offerer"
        assert {tag.name for tag in offerer.tags} == {tag1.name, tag2.name}

        assert external_testing.zendesk_sell_requests == [{"action": "update", "type": "Offerer", "id": offerer.id}]

    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_edit_offerer_remove_tags(self, mocked_validate_csrf_token, client):
        users_factories.AdminFactory(email="admin@example.com")

        offerer = offerers_factories.OffererFactory(
            tags=[
                offerers_factories.OffererTagFactory(),
                offerers_factories.OffererTagFactory(),
            ]
        )
        api_client = client.with_session_auth("admin@example.com")

        response = api_client.post(
            f"/pc/back-office/offerer/edit/?id={offerer.id}",
            form={
                "name": "Updated offerer",
                "siren": offerer.siren,
                "city": offerer.city,
                "postalCode": offerer.postalCode,
                "address": offerer.address,
                "tags": [],  # Remove both tags
                "isActive": offerer.isActive,
            },
        )

        assert response.status_code == 302
        db.session.refresh(offerer)
        assert offerer.name == "Updated offerer"
        assert len(offerer.tags) == 0

        assert external_testing.zendesk_sell_requests == [{"action": "update", "type": "Offerer", "id": offerer.id}]

    @pytest.mark.parametrize(
        "booking_status", [None, BookingStatus.USED, BookingStatus.CANCELLED, BookingStatus.REIMBURSED]
    )
    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_deactivate_offerer(self, mocked_validate_csrf_token, client, booking_status):
        admin = users_factories.AdminFactory(email="user@example.com")
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        pro_user = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        if booking_status is not None:
            booking_factories.BookingFactory(stock__offer__venue=venue, status=booking_status)

        api_client = client.with_session_auth(admin.email)
        response = api_client.post(
            f"/pc/back-office/offerer/edit/?id={offerer.id}",
            form={
                "name": offerer.name,
                "siren": offerer.siren,
                "city": offerer.city,
                "postalCode": offerer.postalCode,
                "address": offerer.address,
                # "isActive" is not sent in request when unchecked
            },
        )

        assert response.status_code == 302

        db.session.refresh(offerer)
        db.session.refresh(venue)

        assert not offerer.isActive
        assert len(external_testing.sendinblue_requests) == 2
        assert {req["email"] for req in external_testing.sendinblue_requests} == {pro_user.email, venue.bookingEmail}
        assert external_testing.zendesk_sell_requests == [{"action": "update", "type": "Offerer", "id": offerer.id}]

    @pytest.mark.parametrize("booking_status", [BookingStatus.PENDING, BookingStatus.CONFIRMED])
    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_deactivate_offerer_rejected(self, mocked_validate_csrf_token, client, booking_status):
        admin = users_factories.AdminFactory(email="user@example.com")
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer)
        booking_factories.BookingFactory(stock__offer__venue=venue, status=booking_status)

        api_client = client.with_session_auth(admin.email)
        response = api_client.post(
            f"/pc/back-office/offerer/edit/?id={offerer.id}",
            form={
                "name": offerer.name,
                "siren": offerer.siren,
                "city": offerer.city,
                "postalCode": offerer.postalCode,
                "address": offerer.address,
                # "isActive" is not sent in request when unchecked
            },
        )

        assert response.status_code == 200
        assert (
            "Impossible de désactiver une structure juridique pour laquelle des réservations sont en cours."
            in response.data.decode("utf8")
        )

        db.session.refresh(offerer)
        db.session.refresh(venue)

        assert offerer.isActive
        assert len(external_testing.sendinblue_requests) == 0

    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_reactivate_offerer(self, mocked_validate_csrf_token, client):
        admin = users_factories.AdminFactory(email="user@example.com")
        offerer = offerers_factories.OffererFactory(isActive=False)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        pro_user = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)

        api_client = client.with_session_auth(admin.email)
        response = api_client.post(
            f"/pc/back-office/offerer/edit/?id={offerer.id}",
            form={
                "name": offerer.name,
                "siren": offerer.siren,
                "city": offerer.city,
                "postalCode": offerer.postalCode,
                "address": offerer.address,
                "isActive": "y",
            },
        )

        assert response.status_code == 302

        db.session.refresh(offerer)
        db.session.refresh(venue)

        assert offerer.isActive
        assert len(external_testing.sendinblue_requests) == 2
        assert {req["email"] for req in external_testing.sendinblue_requests} == {pro_user.email, venue.bookingEmail}
        assert external_testing.zendesk_sell_requests == [{"action": "update", "type": "Offerer", "id": offerer.id}]

    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_delete_offerer(self, mocked_validate_csrf_token, client):
        # Can delete offerer because there is no booking
        admin = users_factories.AdminFactory(email="user@example.com")
        venue = offerers_factories.VenueFactory(bookingEmail="booking@example.com")
        pro_user = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=venue.managingOfferer)

        api_client = client.with_session_auth(admin.email)
        response = api_client.post(
            "/pc/back-office/offerer/delete/", form={"id": venue.managingOfferer.id, "url": "/pc/back-office/offerer/"}
        )

        assert response.status_code == 302
        assert len(offerers_models.Offerer.query.all()) == 0
        assert len(external_testing.sendinblue_requests) == 2
        assert {req["email"] for req in external_testing.sendinblue_requests} == {
            pro_user.email,
            "booking@example.com",
        }

    @pytest.mark.parametrize(
        "booking_status",
        [
            BookingStatus.PENDING,
            BookingStatus.USED,
            BookingStatus.CONFIRMED,
            BookingStatus.CANCELLED,
            BookingStatus.REIMBURSED,
        ],
    )
    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_delete_offerer_rejected(self, mocked_validate_csrf_token, client, booking_status):
        admin = users_factories.AdminFactory(email="user@example.com")
        venue = offerers_factories.VenueFactory()
        booking_factories.BookingFactory(stock__offer__venue=venue, status=booking_status)
        offerers_factories.UserOffererFactory(offerer=venue.managingOfferer)

        api_client = client.with_session_auth(admin.email)
        response = api_client.post(
            "/pc/back-office/offerer/delete/", form={"id": venue.managingOfferer.id, "url": "/pc/back-office/offerer/"}
        )

        assert response.status_code == 302

        list_response = api_client.get(response.headers["location"])
        assert (
            "Impossible d&#39;effacer une structure juridique pour laquelle il existe des réservations."
            in list_response.data.decode("utf8")
        )

        assert len(offerers_models.Offerer.query.all()) == 1
        assert len(external_testing.sendinblue_requests) == 0

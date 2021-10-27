from datetime import datetime
from datetime import timedelta
from unittest import mock
from urllib.parse import urlencode

import pytest

from pcapi.core.bookings.factories import CancelledIndividualBookingFactory
from pcapi.core.bookings.factories import IndividualBookingFactory
from pcapi.core.bookings.factories import UsedIndividualBookingFactory
from pcapi.core.offers import factories as offers_factories
from pcapi.core.payments.factories import PaymentFactory
from pcapi.core.users import factories as users_factories
from pcapi.models import api_errors
from pcapi.routes.serialization import serialize
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


class Returns200Test:
    @pytest.mark.usefixtures("db_session")
    def when_user_has_rights_and_regular_offer(self, app):
        # Given
        user_admin = users_factories.AdminFactory(email="admin@example.com")
        user_offerer = offers_factories.UserOffererFactory(user=user_admin)
        booking = IndividualBookingFactory(stock__offer__venue__managingOfferer=user_offerer.offerer)
        url = f"/bookings/token/{booking.token}"

        # When
        response = TestClient(app.test_client()).with_session_auth(user_admin.email).get(url)

        # Then
        assert response.status_code == 200
        response_json = response.json
        assert response_json == {
            "bookingId": humanize(booking.id),
            "date": serialize(booking.stock.beginningDatetime),
            "email": booking.email,
            "isUsed": False,
            "offerName": booking.stock.offer.name,
            "userName": booking.publicName,
            "venueDepartementCode": booking.stock.offer.venue.departementCode,
        }

    @pytest.mark.usefixtures("db_session")
    def when_user_has_rights_and_regular_offer_and_token_in_lower_case(self, app):
        # Given
        user = users_factories.BeneficiaryGrant18Factory(email="user@example.com", publicName="John Doe")
        user_admin = users_factories.AdminFactory(email="admin@example.com")
        booking = IndividualBookingFactory(individualBooking__user=user)
        booking_token = booking.token.lower()
        url = f"/bookings/token/{booking_token}"

        # When
        response = TestClient(app.test_client()).with_session_auth(user_admin.email).get(url)

        # Then
        assert response.status_code == 200
        response_json = response.json
        assert response_json == {
            "bookingId": humanize(booking.id),
            "date": serialize(booking.stock.beginningDatetime),
            "email": booking.email,
            "isUsed": False,
            "offerName": booking.stock.offer.product.name,
            "userName": booking.publicName,
            "venueDepartementCode": booking.stock.offer.venue.departementCode,
        }

    @pytest.mark.usefixtures("db_session")
    def when_user_has_rights_and_email_with_special_characters_url_encoded(self, app):
        # Given
        user = users_factories.BeneficiaryGrant18Factory(email="user+plus@example.com")
        user_admin = users_factories.AdminFactory(email="admin@example.com")
        booking = IndividualBookingFactory(individualBooking__user=user)
        url_email = urlencode({"email": "user+plus@example.com"})
        url = f"/bookings/token/{booking.token}?{url_email}"

        # When
        response = TestClient(app.test_client()).with_session_auth(user_admin.email).get(url)

        # Then
        assert response.status_code == 200


@pytest.mark.usefixtures("db_session")
class Returns204Test:
    def when_user_not_logged_in_and_gives_right_email(self, app):
        # Given
        user = users_factories.BeneficiaryGrant18Factory(email="user@example.com")
        booking = IndividualBookingFactory(individualBooking__user=user)
        url = f"/bookings/token/{booking.token}?email={user.email}"

        # When
        response = TestClient(app.test_client()).get(url)

        # Then
        assert response.status_code == 204

    def when_user_not_logged_in_and_give_right_email_and_event_offer_id(self, app):
        # Given
        yesterday = datetime.utcnow() - timedelta(days=1)
        user = users_factories.BeneficiaryGrant18Factory(email="user@example.com")
        booking = IndividualBookingFactory(
            individualBooking__user=user, stock=offers_factories.EventStockFactory(), cancellation_limit_date=yesterday
        )
        url = f"/bookings/token/{booking.token}?email={user.email}&offer_id={humanize(booking.stock.offer.id)}"

        # When
        response = TestClient(app.test_client()).get(url)

        # Then
        assert response.status_code == 204

    def when_user_not_logged_in_and_give_right_email_and_offer_id_thing(self, app):
        # Given
        user = users_factories.BeneficiaryGrant18Factory(email="user@example.com")
        booking = IndividualBookingFactory(individualBooking__user=user, stock=offers_factories.ThingStockFactory())
        url = f"/bookings/token/{booking.token}?email={user.email}&offer_id={humanize(booking.stock.offerId)}"

        # When
        response = TestClient(app.test_client()).get(url)

        # Then
        assert response.status_code == 204


class Returns404Test:
    @pytest.mark.usefixtures("db_session")
    def when_token_user_has_rights_but_token_not_found(self, app):
        # Given
        user_admin = users_factories.AdminFactory(email="admin@example.com")
        url = "/bookings/token/12345"

        # When
        response = TestClient(app.test_client()).with_session_auth(user_admin.email).get(url)

        # Then
        assert response.status_code == 404
        assert response.json["global"] == ["Cette contremarque n'a pas été trouvée"]

    @pytest.mark.usefixtures("db_session")
    def when_user_not_logged_in_and_wrong_email(self, app):
        # Given
        user = users_factories.BeneficiaryGrant18Factory(email="user@example.com")
        user_admin = users_factories.AdminFactory(email="admin@example.com")
        booking = IndividualBookingFactory(individualBooking__user=user)

        url = f"/bookings/token/{booking.token}?email=toto@example.com"

        # When
        response = TestClient(app.test_client()).with_session_auth(user_admin.email).get(url)

        # Then
        assert response.status_code == 404
        assert response.json["global"] == ["Cette contremarque n'a pas été trouvée"]

    @pytest.mark.usefixtures("db_session")
    def when_user_not_logged_in_right_email_and_wrong_offer(self, app):
        # Given
        user = users_factories.BeneficiaryGrant18Factory(email="user@example.com")
        booking = IndividualBookingFactory(individualBooking__user=user)

        url = f"/bookings/token/{booking.token}?email={user.email}&offer_id={humanize(123)}"

        # When
        response = TestClient(app.test_client()).get(url)

        # Then
        assert response.status_code == 404
        assert response.json["global"] == ["Cette contremarque n'a pas été trouvée"]

    @pytest.mark.usefixtures("db_session")
    def when_user_has_rights_and_email_with_special_characters_not_url_encoded(self, app):
        # Given
        user = users_factories.BeneficiaryGrant18Factory(email="user+plus@example.com")
        user_admin = users_factories.AdminFactory(email="admin@example.com")
        booking = IndividualBookingFactory(individualBooking__user=user)
        url = f"/bookings/token/{booking.token}?email={user.email}"

        # When
        response = TestClient(app.test_client()).with_session_auth(user_admin.email).get(url)

        # Then
        assert response.status_code == 404


class Returns400Test:
    @pytest.mark.usefixtures("db_session")
    def when_user_not_logged_in_and_doesnt_give_email(self, app):
        # Given
        user = users_factories.BeneficiaryGrant18Factory(email="user@example.com")
        booking = IndividualBookingFactory(individualBooking__user=user)
        url = f"/bookings/token/{booking.token}"

        # When
        response = TestClient(app.test_client()).get(url)

        # Then
        assert response.status_code == 400
        error_message = response.json
        assert error_message["email"] == [
            "Vous devez préciser l'email de l'utilisateur quand vous n'êtes pas connecté(e)"
        ]

    @pytest.mark.usefixtures("db_session")
    def when_user_doesnt_have_rights_and_token_exists(self, app):
        # Given
        user = users_factories.BeneficiaryGrant18Factory(email="user@example.com")
        users_factories.BeneficiaryGrant18Factory(email="querying@example.com")
        booking = IndividualBookingFactory(individualBooking__user=user)
        url = f"/bookings/token/{booking.token}"

        # When
        response = TestClient(app.test_client()).with_session_auth("querying@example.com").get(url)

        # Then
        assert response.status_code == 400
        assert response.json["global"] == ["Cette contremarque n'a pas été trouvée"]


class Returns403Test:
    @mock.patch("pcapi.core.bookings.validation.check_is_usable")
    @pytest.mark.usefixtures("db_session")
    def when_booking_not_confirmed(self, mocked_check_is_usable, app):
        # Given
        unconfirmed_booking = IndividualBookingFactory(stock=offers_factories.EventStockFactory())
        url = (
            f"/bookings/token/{unconfirmed_booking.token}?email={unconfirmed_booking.individualBooking.user.email}"
            f"&offer_id={humanize(unconfirmed_booking.stock.offerId)}"
        )
        mocked_check_is_usable.side_effect = api_errors.ForbiddenError(errors={"booking": ["Not confirmed"]})

        # When
        response = TestClient(app.test_client()).get(url)

        # Then
        assert response.status_code == 403
        assert response.json["booking"] == ["Not confirmed"]

    @pytest.mark.usefixtures("db_session")
    def when_booking_is_cancelled(self, app):
        # Given
        user = users_factories.BeneficiaryGrant18Factory(email="user@example.com")
        booking = CancelledIndividualBookingFactory(individualBooking__user=user)
        url = f"/bookings/token/{booking.token}?email={user.email}&offer_id={humanize(booking.stock.offerId)}"

        # When
        response = TestClient(app.test_client()).get(url)

        # Then
        assert response.status_code == 403
        assert response.json["booking"] == ["Cette réservation a été annulée"]

    @pytest.mark.usefixtures("db_session")
    def when_booking_is_refunded(self, app):
        # Given
        booking = PaymentFactory(booking=UsedIndividualBookingFactory()).booking
        url = (
            f"/bookings/token/{booking.token}?"
            f"email={booking.individualBooking.user.email}&offer_id={humanize(booking.stock.offerId)}"
        )

        # When
        response = TestClient(app.test_client()).get(url)

        # Then
        assert response.status_code == 403
        assert response.json["payment"] == ["Cette réservation a été remboursée"]


class Returns410Test:
    @pytest.mark.usefixtures("db_session")
    def when_booking_is_already_validated(self, app):
        # Given
        user = users_factories.BeneficiaryGrant18Factory(email="user@example.com")
        booking = UsedIndividualBookingFactory(individualBooking__user=user)
        url = f"/bookings/token/{booking.token}?email={user.email}&offer_id={humanize(booking.stock.offerId)}"

        # When
        response = TestClient(app.test_client()).get(url)

        # Then
        assert response.status_code == 410
        assert response.json["booking"] == ["Cette réservation a déjà été validée"]

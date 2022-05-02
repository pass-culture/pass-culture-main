from datetime import datetime
from datetime import timedelta
from urllib.parse import urlencode

import pytest

from pcapi.core.bookings.factories import CancelledIndividualBookingFactory
from pcapi.core.bookings.factories import IndividualBookingFactory
from pcapi.core.bookings.factories import UsedIndividualBookingFactory
import pcapi.core.finance.factories as finance_factories
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.routes.serialization import serialize
from pcapi.utils.human_ids import humanize


class Returns200Test:
    @pytest.mark.usefixtures("db_session")
    def when_user_has_rights_and_regular_offer(self, client):
        # Given
        user_admin = users_factories.AdminFactory(email="admin@example.com")
        user_offerer = offerers_factories.UserOffererFactory(user=user_admin)
        booking = IndividualBookingFactory(stock__offer__venue__managingOfferer=user_offerer.offerer)
        url = f"/bookings/token/{booking.token}"

        # When
        response = client.with_session_auth(user_admin.email).get(url)

        # Then
        assert response.status_code == 200
        response_json = response.json
        assert response_json == {
            "bookingId": humanize(booking.id),
            "date": serialize(booking.stock.beginningDatetime),
            "email": booking.email,
            "isUsed": False,
            "offerName": booking.stock.offer.name,
            "userName": booking.userName,
            "venueDepartementCode": booking.stock.offer.venue.departementCode,
        }

    @pytest.mark.usefixtures("db_session")
    def when_user_has_rights_and_regular_offer_and_token_in_lower_case(self, client):
        # Given
        user = users_factories.BeneficiaryGrant18Factory(email="user@example.com", publicName="John Doe")
        user_admin = users_factories.AdminFactory(email="admin@example.com")
        booking = IndividualBookingFactory(individualBooking__user=user)
        booking_token = booking.token.lower()
        url = f"/bookings/token/{booking_token}"

        # When
        response = client.with_session_auth(user_admin.email).get(url)

        # Then
        assert response.status_code == 200
        response_json = response.json
        assert response_json == {
            "bookingId": humanize(booking.id),
            "date": serialize(booking.stock.beginningDatetime),
            "email": booking.email,
            "isUsed": False,
            "offerName": booking.stock.offer.product.name,
            "userName": booking.userName,
            "venueDepartementCode": booking.stock.offer.venue.departementCode,
        }

    @pytest.mark.usefixtures("db_session")
    def when_user_has_rights_and_email_with_special_characters_url_encoded(self, client):
        # Given
        user = users_factories.BeneficiaryGrant18Factory(email="user+plus@example.com")
        user_admin = users_factories.AdminFactory(email="admin@example.com")
        booking = IndividualBookingFactory(individualBooking__user=user)
        url_email = urlencode({"email": "user+plus@example.com"})
        url = f"/bookings/token/{booking.token}?{url_email}"

        # When
        response = client.with_session_auth(user_admin.email).get(url)

        # Then
        assert response.status_code == 200


@pytest.mark.usefixtures("db_session")
class Returns204Test:
    def when_user_not_logged_in_and_gives_right_email(self, client):
        # Given
        user = users_factories.BeneficiaryGrant18Factory(email="user@example.com")
        booking = IndividualBookingFactory(individualBooking__user=user)
        url = f"/bookings/token/{booking.token}?email={user.email}"

        # When
        response = client.get(url)

        # Then
        assert response.status_code == 204
        assert response.data == b""
        assert response.json == None

    def when_user_not_logged_in_and_give_right_email_and_event_offer_id(self, client):
        # Given
        yesterday = datetime.utcnow() - timedelta(days=1)
        user = users_factories.BeneficiaryGrant18Factory(email="user@example.com")
        booking = IndividualBookingFactory(
            individualBooking__user=user, stock=offers_factories.EventStockFactory(), cancellation_limit_date=yesterday
        )
        url = f"/bookings/token/{booking.token}?email={user.email}&offer_id={humanize(booking.stock.offer.id)}"

        # When
        response = client.get(url)

        # Then
        assert response.status_code == 204
        assert response.data == b""
        assert response.json == None

    def when_user_not_logged_in_and_give_right_email_and_offer_id_thing(self, client):
        # Given
        user = users_factories.BeneficiaryGrant18Factory(email="user@example.com")
        booking = IndividualBookingFactory(individualBooking__user=user, stock=offers_factories.ThingStockFactory())
        url = f"/bookings/token/{booking.token}?email={user.email}&offer_id={humanize(booking.stock.offerId)}"

        # When
        response = client.get(url)

        # Then
        assert response.status_code == 204
        assert response.data == b""
        assert response.json == None


class Returns404Test:
    @pytest.mark.usefixtures("db_session")
    def when_token_user_has_rights_but_token_not_found(self, client):
        # Given
        user_admin = users_factories.AdminFactory(email="admin@example.com")
        url = "/bookings/token/12345"

        # When
        response = client.with_session_auth(user_admin.email).get(url)

        # Then
        assert response.status_code == 404
        assert response.json["global"] == ["Cette contremarque n'a pas été trouvée"]

    @pytest.mark.usefixtures("db_session")
    def when_user_not_logged_in_and_wrong_email(self, client):
        # Given
        user = users_factories.BeneficiaryGrant18Factory(email="user@example.com")
        user_admin = users_factories.AdminFactory(email="admin@example.com")
        booking = IndividualBookingFactory(individualBooking__user=user)

        url = f"/bookings/token/{booking.token}?email=toto@example.com"

        # When
        response = client.with_session_auth(user_admin.email).get(url)

        # Then
        assert response.status_code == 404
        assert response.json["global"] == ["Cette contremarque n'a pas été trouvée"]

    @pytest.mark.usefixtures("db_session")
    def when_user_not_logged_in_right_email_and_wrong_offer(self, client):
        # Given

        user = users_factories.BeneficiaryGrant18Factory(email="user@example.com")
        booking = IndividualBookingFactory(individualBooking__user=user)

        url = f"/bookings/token/{booking.token}?email={user.email}&offer_id={humanize(0)}"

        # When
        response = client.get(url)

        # Then
        assert response.status_code == 404
        assert response.json["global"] == ["Cette contremarque n'a pas été trouvée"]

    @pytest.mark.usefixtures("db_session")
    def when_user_has_rights_and_email_with_special_characters_not_url_encoded(self, client):
        # Given
        user = users_factories.BeneficiaryGrant18Factory(email="user+plus@example.com")
        user_admin = users_factories.AdminFactory(email="admin@example.com")
        booking = IndividualBookingFactory(individualBooking__user=user)
        url = f"/bookings/token/{booking.token}?email={user.email}"

        # When
        response = client.with_session_auth(user_admin.email).get(url)

        # Then
        assert response.status_code == 404


class Returns400Test:
    @pytest.mark.usefixtures("db_session")
    def when_user_not_logged_in_and_doesnt_give_email(self, client):
        # Given
        user = users_factories.BeneficiaryGrant18Factory(email="user@example.com")
        booking = IndividualBookingFactory(individualBooking__user=user)
        url = f"/bookings/token/{booking.token}"

        # When
        response = client.get(url)

        # Then
        assert response.status_code == 400
        error_message = response.json
        assert error_message["email"] == [
            "Vous devez préciser l'email de l'utilisateur quand vous n'êtes pas connecté(e)"
        ]

    @pytest.mark.usefixtures("db_session")
    def when_user_doesnt_have_rights_and_token_exists(self, client):
        # Given
        user = users_factories.BeneficiaryGrant18Factory(email="user@example.com")
        users_factories.BeneficiaryGrant18Factory(email="querying@example.com")
        booking = IndividualBookingFactory(individualBooking__user=user)
        url = f"/bookings/token/{booking.token}"

        # When
        response = client.with_session_auth("querying@example.com").get(url)

        # Then
        assert response.status_code == 400
        assert response.json["global"] == ["Cette contremarque n'a pas été trouvée"]


class Returns403Test:
    @pytest.mark.usefixtures("db_session")
    def when_booking_not_confirmed(self, client):
        # Given
        cancellation_date = datetime.utcnow() + timedelta(days=7)
        unconfirmed_booking = IndividualBookingFactory(
            stock=offers_factories.EventStockFactory(), cancellationLimitDate=cancellation_date
        )
        url = (
            f"/bookings/token/{unconfirmed_booking.token}?email={unconfirmed_booking.individualBooking.user.email}"
            f"&offer_id={humanize(unconfirmed_booking.stock.offerId)}"
        )

        # When
        response = client.get(url)

        # Then
        assert response.status_code == 403
        assert "Cette réservation a été effectuée le " in response.json["booking"][0]

    @pytest.mark.usefixtures("db_session")
    def when_booking_is_refunded(self, client):
        # Given
        booking = finance_factories.PaymentFactory().booking
        url = (
            f"/bookings/token/{booking.token}?"
            f"email={booking.individualBooking.user.email}&offer_id={humanize(booking.stock.offerId)}"
        )

        # When
        response = client.get(url)

        # Then
        assert response.status_code == 403
        assert response.json["payment"] == ["Cette réservation a été remboursée"]


class Returns410Test:
    @pytest.mark.usefixtures("db_session")
    def when_booking_is_cancelled(self, client):
        # Given
        user = users_factories.BeneficiaryGrant18Factory(email="user@example.com")
        booking = CancelledIndividualBookingFactory(individualBooking__user=user)
        url = f"/bookings/token/{booking.token}?email={user.email}&offer_id={humanize(booking.stock.offerId)}"

        # When
        response = client.get(url)

        # Then
        assert response.status_code == 410
        assert response.json["booking_cancelled"] == ["Cette réservation a été annulée"]

    @pytest.mark.usefixtures("db_session")
    def when_booking_is_already_validated(self, client):
        # Given
        user = users_factories.BeneficiaryGrant18Factory(email="user@example.com")
        booking = UsedIndividualBookingFactory(individualBooking__user=user)
        url = f"/bookings/token/{booking.token}?email={user.email}&offer_id={humanize(booking.stock.offerId)}"

        # When
        response = client.get(url)

        # Then
        assert response.status_code == 410
        assert response.json["booking"] == ["Cette réservation a déjà été validée"]

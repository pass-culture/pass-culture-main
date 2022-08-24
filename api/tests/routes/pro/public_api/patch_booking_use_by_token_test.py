import pytest

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingStatus
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.users import factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


class Returns204Test:
    class WithApiKeyAuthTest:
        def test_when_api_key_is_provided_and_rights_and_regular_offer(self, client):
            booking = bookings_factories.BookingFactory(token="ABCDEF")
            offerers_factories.ApiKeyFactory(offerer=booking.offerer)

            url = f"/v2/bookings/use/token/{booking.token}"
            response = client.patch(
                url,
                headers={
                    "Authorization": f"Bearer {offerers_factories.DEFAULT_CLEAR_API_KEY}",
                },
            )

            assert response.status_code == 204
            booking = Booking.query.one()
            assert booking.status is BookingStatus.USED

    class WithBasicAuthTest:
        def test_when_user_is_logged_in_and_regular_offer(self, client):
            booking = bookings_factories.BookingFactory(token="ABCDEF")
            pro_user = users_factories.ProFactory(email="pro@example.com")
            offerers_factories.UserOffererFactory(user=pro_user, offerer=booking.offerer)

            url = f"/v2/bookings/use/token/{booking.token}"
            response = client.with_session_auth("pro@example.com").patch(url)

            assert response.status_code == 204
            booking = Booking.query.one()
            assert booking.status is BookingStatus.USED

        def test_when_user_is_logged_in_expect_booking_with_token_in_lower_case_to_be_used(self, client):
            booking = bookings_factories.BookingFactory(token="ABCDEF")
            pro_user = users_factories.ProFactory(email="pro@example.com")
            offerers_factories.UserOffererFactory(user=pro_user, offerer=booking.offerer)

            url = f"/v2/bookings/use/token/{booking.token.lower()}"
            response = client.with_session_auth("pro@example.com").patch(url)

            assert response.status_code == 204
            booking = Booking.query.one()
            assert booking.status is BookingStatus.USED


class Returns401Test:
    def test_when_user_not_logged_in_and_doesnt_give_api_key(self, client):
        response = client.patch("/v2/bookings/use/token/TOKEN")
        assert response.status_code == 401

    def test_when_user_not_logged_in_and_not_existing_api_key_given(self, client):
        url = "/v2/bookings/use/token/TOKEN"
        response = client.patch(url, headers={"Authorization": "Bearer WrongApiKey1234567"})
        assert response.status_code == 401


class Returns403Test:
    class WithApiKeyAuthTest:
        def test_when_api_key_given_not_related_to_booking_offerer(self, client):
            # Given
            booking = bookings_factories.BookingFactory()
            offerers_factories.ApiKeyFactory()  # another offerer's API key

            # When
            auth = "Bearer " + offerers_factories.DEFAULT_CLEAR_API_KEY
            url = f"/v2/bookings/use/token/{booking.token}"
            response = client.patch(url, headers={"Authorization": auth})

            # Then
            assert response.status_code == 403
            assert response.json["user"] == [
                "Vous n’avez pas les droits suffisants pour valider cette contremarque car cette réservation n'a pas été faite sur une de vos offres, ou que votre rattachement à la structure est encore en cours de validation"
            ]

    class WithBasicAuthTest:
        def test_when_user_is_not_attached_to_linked_offerer(self, client):
            # Given
            booking = bookings_factories.BookingFactory()
            another_pro_user = offerers_factories.UserOffererFactory().user

            # When
            url = f"/v2/bookings/use/token/{booking.token}"
            response = client.with_session_auth(another_pro_user.email).patch(url)

            # Then
            assert response.status_code == 403
            assert response.json["user"] == [
                "Vous n’avez pas les droits suffisants pour valider cette contremarque car cette réservation n'a pas été faite sur une de vos offres, ou que votre rattachement à la structure est encore en cours de validation"
            ]
            booking = Booking.query.get(booking.id)
            assert booking.status is not BookingStatus.USED


class Returns404Test:
    def test_missing_token(self, client):
        response = client.patch("/v2/bookings/use/token/")
        assert response.status_code == 404

    def test_unknown_token(self, client):
        pro_user = users_factories.ProFactory()
        response = client.with_basic_auth(pro_user.email).patch("/v2/bookings/use/token/UNKNOWN")
        assert response.status_code == 404
        assert response.json["global"] == ["Cette contremarque n'a pas été trouvée"]


class Returns410Test:
    def test_when_api_key_is_provided_and_booking_has_been_cancelled_already(self, client):
        # Given
        booking = bookings_factories.CancelledBookingFactory()
        offerers_factories.ApiKeyFactory(offerer=booking.offerer)

        # When
        url = f"/v2/bookings/use/token/{booking.token}"
        auth = "Bearer development_prefix_clearSecret"
        response = client.patch(url, headers={"Authorization": auth})

        # Then
        assert response.status_code == 410
        assert response.json["booking_cancelled"] == ["Cette réservation a été annulée"]
        booking = Booking.query.get(booking.id)
        assert booking.status is not BookingStatus.USED

    def test_when_user_is_logged_in_and_booking_has_been_cancelled_already(self, client):
        # Given
        admin = users_factories.AdminFactory()
        booking = bookings_factories.CancelledBookingFactory()
        url = f"/v2/bookings/use/token/{booking.token}"

        # When
        response = client.with_session_auth(admin.email).patch(url)

        # Then
        assert response.status_code == 410
        assert response.json["booking_cancelled"] == ["Cette réservation a été annulée"]
        booking = Booking.query.get(booking.id)
        assert booking.status is not BookingStatus.USED

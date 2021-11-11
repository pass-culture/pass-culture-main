import pytest

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.offerers.factories import ApiKeyFactory
from pcapi.core.offerers.factories import DEFAULT_CLEAR_API_KEY
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.models import Booking
import pcapi.notifications.push.testing as push_testing


class Returns204Test:
    @pytest.mark.usefixtures("db_session")
    def test_should_returns_204_with_cancellation_allowed(self, client):
        # Given
        stock = offers_factories.EventStockFactory(offer__name="Chouette concert")
        booking = bookings_factories.IndividualBookingFactory(stock=stock)
        ApiKeyFactory(offerer=booking.offerer)

        # When
        response = client.patch(
            f"/v2/bookings/cancel/token/{booking.token}",
            headers={"Authorization": "Bearer " + DEFAULT_CLEAR_API_KEY},
        )

        # Then
        # cancellation can trigger more than one request to Batch
        assert len(push_testing.requests) >= 1
        assert response.status_code == 204
        updated_booking = Booking.query.one()
        assert updated_booking.isCancelled
        assert updated_booking.status is BookingStatus.CANCELLED

        assert push_testing.requests[-1] == {
            "group_id": "Cancel_booking",
            "message": {
                "body": """Ta réservation "Chouette concert" a été annulée par l'offreur.""",
                "title": "Réservation annulée",
            },
            "user_ids": [booking.individualBooking.userId],
        }

    @pytest.mark.usefixtures("db_session")
    def test_should_returns_204_with_lowercase_token(self, client):
        # Given
        booking = bookings_factories.IndividualBookingFactory()
        ApiKeyFactory(offerer=booking.offerer)

        # When
        response = client.patch(
            f"/v2/bookings/cancel/token/{booking.token.lower()}",
            headers={"Authorization": "Bearer " + DEFAULT_CLEAR_API_KEY},
        )

        assert response.status_code == 204
        booking = Booking.query.one()
        assert booking.isCancelled
        assert booking.status is BookingStatus.CANCELLED


class Returns401Test:
    @pytest.mark.usefixtures("db_session")
    def when_not_authenticated_used_api_key_or_login(self, client):
        response = client.patch("/v2/bookings/cancel/token/TOKEN")
        assert response.status_code == 401

    @pytest.mark.usefixtures("db_session")
    def when_giving_an_api_key_that_does_not_exists(self, client):
        headers = {"Authorization": "Bearer WrongApiKey1234567"}
        response = client.patch("/v2/bookings/cancel/token/TOKEN", headers=headers)
        assert response.status_code == 401


class Returns403Test:
    @pytest.mark.usefixtures("db_session")
    def when_the_api_key_is_not_linked_to_the_right_offerer(self, client):
        # Given
        booking = bookings_factories.BookingFactory()
        ApiKeyFactory()  # another offerer's API key

        # When
        response = client.patch(
            f"/v2/bookings/cancel/token/{booking.token}",
            headers={"Authorization": "Bearer " + DEFAULT_CLEAR_API_KEY},
        )

        # Then
        assert response.status_code == 403
        assert response.json["user"] == ["Vous n'avez pas les droits suffisants pour annuler cette réservation."]

    @pytest.mark.usefixtures("db_session")
    def when_the_logged_user_has_not_rights_on_offerer(self, client):
        # Given
        booking = bookings_factories.BookingFactory()
        another_pro_user = offers_factories.UserOffererFactory().user

        # When
        url = f"/v2/bookings/cancel/token/{booking.token}"
        response = client.with_session_auth(another_pro_user.email).patch(url)

        # Then
        assert response.status_code == 403
        assert response.json["global"] == [
            "Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."
        ]

    @pytest.mark.usefixtures("db_session")
    def test_should_prevent_a_used_booking_from_being_cancelled(self, client):
        # Given
        booking = bookings_factories.UsedBookingFactory()
        pro_user = offers_factories.UserOffererFactory(offerer=booking.offerer).user

        # When
        url = f"/v2/bookings/cancel/token/{booking.token}"
        response = client.with_basic_auth(pro_user.email).patch(url)

        # Then
        assert response.status_code == 403
        assert response.json["global"] == ["Impossible d'annuler une réservation consommée"]
        booking = Booking.query.first()
        assert booking.isUsed
        assert not booking.isCancelled
        assert booking.status is BookingStatus.USED
        assert push_testing.requests == []


class Returns404Test:
    @pytest.mark.usefixtures("db_session")
    def when_the_booking_does_not_exists(self, client):
        user = users_factories.ProFactory()
        url = "/v2/bookings/cancel/token/FAKETOKEN"
        response = client.with_basic_auth(user.email).patch(url)
        assert response.status_code == 404
        assert response.json["global"] == ["Cette contremarque n'a pas été trouvée"]


class Returns410Test:
    @pytest.mark.usefixtures("db_session")
    def test_cancel_a_booking_already_cancelled(self, client):
        # Given
        booking = bookings_factories.CancelledBookingFactory()
        pro_user = offers_factories.UserOffererFactory(offerer=booking.offerer).user

        # When
        url = f"/v2/bookings/cancel/token/{booking.token}"
        response = client.with_basic_auth(pro_user.email).patch(url)

        # Then
        assert response.status_code == 410
        assert response.json["global"] == ["Cette contremarque a déjà été annulée"]

import pytest

from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.offerers.factories import ApiKeyFactory
from pcapi.core.offerers.factories import DEFAULT_CLEAR_API_KEY
import pcapi.core.offers.factories as offers_factories
from pcapi.core.payments import factories as payments_factories
from pcapi.core.users import factories as users_factories
from pcapi.models import Booking


@pytest.mark.usefixtures("db_session")
class Returns204Test:
    class WithApiKeyAuthTest:
        def test_when_api_key_provided_is_related_to_regular_offer_with_rights(self, client):
            booking = bookings_factories.UsedIndividualBookingFactory()
            ApiKeyFactory(offerer=booking.offerer)

            url = f"/v2/bookings/keep/token/{booking.token}"
            response = client.patch(
                url,
                headers={
                    "Authorization": f"Bearer {DEFAULT_CLEAR_API_KEY}",
                },
            )

            assert response.status_code == 204
            booking = Booking.query.one()
            assert not booking.isUsed
            assert booking.status is not BookingStatus.USED
            assert booking.dateUsed is None

    class WithBasicAuthTest:
        def test_when_user_is_logged_in_and_regular_offer(self, client):
            booking = bookings_factories.UsedIndividualBookingFactory()
            pro_user = offers_factories.UserOffererFactory(offerer=booking.offerer).user

            url = f"/v2/bookings/keep/token/{booking.token}"
            response = client.with_session_auth(pro_user.email).patch(url)

            assert response.status_code == 204
            booking = Booking.query.one()
            assert not booking.isUsed
            assert booking.status is not BookingStatus.USED
            assert booking.dateUsed is None

        def test_when_user_is_logged_in_expect_booking_with_token_in_lower_case_to_be_used(self, client):
            booking = bookings_factories.UsedIndividualBookingFactory()
            pro_user = offers_factories.UserOffererFactory(offerer=booking.offerer).user

            url = f"/v2/bookings/keep/token/{booking.token.lower()}"
            response = client.with_session_auth(pro_user.email).patch(url)

            assert response.status_code == 204
            booking = Booking.query.one()
            assert not booking.isUsed
            assert booking.status is not BookingStatus.USED
            assert booking.dateUsed is None

        # FIXME: I don't understand what we're trying to test, here.
        def test_when_there_is_no_remaining_quantity_after_validating(self, client):
            booking = bookings_factories.UsedIndividualBookingFactory(stock__quantity=1)
            pro_user = offers_factories.UserOffererFactory(offerer=booking.offerer).user

            url = f"/v2/bookings/keep/token/{booking.token.lower()}"
            response = client.with_session_auth(pro_user.email).patch(url)

            assert response.status_code == 204
            booking = Booking.query.one()
            assert not booking.isUsed
            assert booking.status is not BookingStatus.USED
            assert booking.dateUsed is None


class Returns401Test:
    @pytest.mark.usefixtures("db_session")
    def test_when_user_not_logged_in_and_doesnt_give_api_key(self, client):
        booking = bookings_factories.BookingFactory()
        response = client.patch(f"/v2/bookings/keep/token/{booking.token}")
        assert response.status_code == 401

    @pytest.mark.usefixtures("db_session")
    def test_when_user_not_logged_in_and_given_api_key_that_does_not_exists(self, client):
        # Given
        booking = bookings_factories.BookingFactory()

        # When
        unknown_auth = "Bearer WrongApiKey1234567"
        url = "/v2/bookings/keep/token/{}".format(booking.token)
        response = client.patch(url, headers={"Authorization": unknown_auth})

        # Then
        assert response.status_code == 401


class Returns403Test:
    class WithApiKeyAuthTest:
        @pytest.mark.usefixtures("db_session")
        def test_when_the_api_key_is_not_linked_to_the_right_offerer(self, client):
            # Given
            booking = bookings_factories.BookingFactory()
            ApiKeyFactory()  # another offerer's API key

            # When
            wrong_auth = f"Bearer {DEFAULT_CLEAR_API_KEY}"
            url = f"/v2/bookings/keep/token/{booking.token}"
            response = client.patch(url, headers={"Authorization": wrong_auth})

            # Then
            assert response.status_code == 403
            assert response.json["user"] == [
                "Vous n’avez pas les droits suffisants pour valider cette contremarque car cette réservation n'a pas été faite sur une de vos offres, ou que votre rattachement à la structure est encore en cours de validation"
            ]

        @pytest.mark.usefixtures("db_session")
        def test_when_api_key_is_provided_and_booking_has_been_cancelled_already(self, client):
            # Given
            booking = bookings_factories.CancelledBookingFactory()
            ApiKeyFactory(offerer=booking.offerer)

            # When
            url = f"/v2/bookings/keep/token/{booking.token}"
            auth = f"Bearer {DEFAULT_CLEAR_API_KEY}"
            response = client.patch(url, headers={"Authorization": auth})

            # Then
            booking = Booking.query.get(booking.id)
            assert response.status_code == 403
            assert response.json["booking"] == ["Cette réservation a été annulée"]
            assert not booking.isUsed
            assert booking.status is BookingStatus.CANCELLED

    class WithBasicAuthTest:
        @pytest.mark.usefixtures("db_session")
        def test_when_user_is_not_attached_to_linked_offerer(self, client):
            # Given
            booking = bookings_factories.BookingFactory()
            another_pro_user = offers_factories.UserOffererFactory().user

            # When
            url = f"/v2/bookings/keep/token/{booking.token}?email={booking.user.email}"
            response = client.with_session_auth(another_pro_user.email).patch(url)

            # Then
            assert response.status_code == 403
            assert response.json["user"] == [
                "Vous n’avez pas les droits suffisants pour valider cette contremarque car cette réservation n'a pas été faite sur une de vos offres, ou que votre rattachement à la structure est encore en cours de validation"
            ]
            assert not booking.isUsed

        @pytest.mark.usefixtures("db_session")
        def test_when_user_is_logged_in_and_booking_has_been_cancelled_already(self, client):
            # Given
            admin = users_factories.UserFactory(isAdmin=True)
            booking = bookings_factories.CancelledBookingFactory()
            url = f"/v2/bookings/keep/token/{booking.token}"

            # When
            response = client.with_session_auth(admin.email).patch(url)

            # Then
            booking = Booking.query.get(booking.id)
            assert response.status_code == 403
            assert response.json["booking"] == ["Cette réservation a été annulée"]
            assert not booking.isUsed
            assert booking.status is BookingStatus.CANCELLED


class Returns404Test:
    @pytest.mark.usefixtures("db_session")
    def test_missing_token(self, client):
        user = users_factories.ProFactory()
        response = client.with_basic_auth(user.email).patch("/v2/bookings/keep/token/")
        assert response.status_code == 404

    @pytest.mark.usefixtures("db_session")
    def test_unknown_token(self, client):
        user = users_factories.ProFactory()
        response = client.with_basic_auth(user.email).patch("/v2/bookings/keep/token/UNKNOWN")
        assert response.status_code == 404
        assert response.json["global"] == ["Cette contremarque n'a pas été trouvée"]


class Returns410Test:
    @pytest.mark.usefixtures("db_session")
    def test_when_booking_has_not_been_used_yet(self, client):
        # Given
        booking = bookings_factories.BookingFactory()
        pro_user = offers_factories.UserOffererFactory(offerer=booking.offerer).user

        # When
        url = f"/v2/bookings/keep/token/{booking.token}"
        response = client.with_session_auth(pro_user.email).patch(url)

        # Then
        assert response.status_code == 410
        assert response.json["booking"] == ["Cette réservation n'a pas encore été validée"]
        assert not booking.isUsed

    @pytest.mark.usefixtures("db_session")
    def test_when_user_is_logged_in_and_booking_payment_exists(self, client):
        # Given
        booking = payments_factories.PaymentFactory().booking
        pro_user = offers_factories.UserOffererFactory(offerer=booking.offerer).user

        # When
        url = f"/v2/bookings/keep/token/{booking.token}"
        response = client.with_session_auth(pro_user.email).patch(url)

        # Then
        assert response.status_code == 410
        assert response.json["payment"] == ["Le remboursement est en cours de traitement"]
        assert booking.isUsed

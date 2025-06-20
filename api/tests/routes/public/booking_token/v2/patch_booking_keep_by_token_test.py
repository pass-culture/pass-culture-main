import pytest

import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.users import factories as users_factories
from pcapi.models import db


@pytest.mark.usefixtures("db_session")
class Returns204Test:
    class WithApiKeyAuthTest:
        def test_when_api_key_provided_is_related_to_regular_offer_with_rights(self, client):
            booking = bookings_factories.UsedBookingFactory()
            offerers_factories.ApiKeyFactory(offerer=booking.offerer)

            url = f"/v2/bookings/keep/token/{booking.token}"
            response = client.patch(
                url,
                headers={
                    "Authorization": "Bearer " + offerers_factories.DEFAULT_CLEAR_API_KEY,
                },
            )

            assert response.status_code == 204
            booking = db.session.query(Booking).one()
            assert booking.status == BookingStatus.CONFIRMED
            assert booking.dateUsed is None

    class WithBasicAuthTest:
        def test_when_user_is_logged_in_and_regular_offer(self, client):
            booking = bookings_factories.UsedBookingFactory()
            pro_user = offerers_factories.UserOffererFactory(offerer=booking.offerer).user

            url = f"/v2/bookings/keep/token/{booking.token}"
            response = client.with_session_auth(pro_user.email).patch(url)

            assert response.status_code == 204
            booking = db.session.query(Booking).one()
            assert booking.status == BookingStatus.CONFIRMED
            assert booking.dateUsed is None

        def test_when_user_is_logged_in_expect_booking_with_token_in_lower_case_to_be_used(self, client):
            booking = bookings_factories.UsedBookingFactory()
            pro_user = offerers_factories.UserOffererFactory(offerer=booking.offerer).user

            url = f"/v2/bookings/keep/token/{booking.token.lower()}"
            response = client.with_session_auth(pro_user.email).patch(url)

            assert response.status_code == 204
            booking = db.session.query(Booking).one()
            assert booking.status == BookingStatus.CONFIRMED
            assert booking.dateUsed is None


class Returns401Test:
    @pytest.mark.usefixtures("db_session")
    def test_when_user_not_logged_in_and_doesnt_give_api_key(self, client):
        booking = bookings_factories.BookingFactory()
        response = client.patch(f"/v2/bookings/keep/token/{booking.token}")
        assert response.status_code == 401

    @pytest.mark.usefixtures("db_session")
    def test_when_user_not_logged_in_and_given_api_key_that_does_not_exists(self, client):
        booking = bookings_factories.BookingFactory()

        unknown_auth = "Bearer WrongApiKey1234567"
        url = "/v2/bookings/keep/token/{}".format(booking.token)
        response = client.patch(url, headers={"Authorization": unknown_auth})

        # Then
        assert response.status_code == 401


class Returns403Test:
    class WithApiKeyAuthTest:
        @pytest.mark.usefixtures("db_session")
        def test_when_the_api_key_is_not_linked_to_the_right_offerer(self, client):
            booking = bookings_factories.BookingFactory()
            offerers_factories.ApiKeyFactory()  # another offerer's API key

            wrong_auth = "Bearer " + offerers_factories.DEFAULT_CLEAR_API_KEY
            url = f"/v2/bookings/keep/token/{booking.token}"
            response = client.patch(url, headers={"Authorization": wrong_auth})

            # Then
            assert response.status_code == 403
            assert response.json["user"] == [
                "Vous n’avez pas les droits suffisants pour valider cette contremarque car cette réservation n'a pas été faite sur une de vos offres, ou que votre rattachement à la structure est encore en cours de validation"
            ]

    class WithBasicAuthTest:
        @pytest.mark.usefixtures("db_session")
        def test_when_user_is_not_attached_to_linked_offerer(self, client):
            booking = bookings_factories.UsedBookingFactory()
            another_pro_user = offerers_factories.UserOffererFactory().user

            url = f"/v2/bookings/keep/token/{booking.token}?email={booking.email}"
            response = client.with_session_auth(another_pro_user.email).patch(url)

            # Then
            assert response.status_code == 403
            assert response.json["user"] == [
                "Vous n’avez pas les droits suffisants pour valider cette contremarque car cette réservation n'a pas été faite sur une de vos offres, ou que votre rattachement à la structure est encore en cours de validation"
            ]
            assert booking.status == BookingStatus.USED


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
        booking = bookings_factories.BookingFactory()
        pro_user = offerers_factories.UserOffererFactory(offerer=booking.offerer).user

        url = f"/v2/bookings/keep/token/{booking.token}"
        response = client.with_session_auth(pro_user.email).patch(url)

        # Then
        assert response.status_code == 410
        assert response.json["booking"] == ["Cette réservation n'a pas encore été validée"]
        assert booking.status == BookingStatus.CONFIRMED

    @pytest.mark.usefixtures("db_session")
    def test_when_user_is_logged_in_and_booking_payment_exists(self, client):
        booking = bookings_factories.ReimbursedBookingFactory()
        pro_user = offerers_factories.UserOffererFactory(offerer=booking.offerer).user

        url = f"/v2/bookings/keep/token/{booking.token}"
        response = client.with_session_auth(pro_user.email).patch(url)

        # Then
        assert response.status_code == 410
        assert response.json["payment"] == ["Le remboursement est en cours de traitement"]
        assert booking.status is BookingStatus.REIMBURSED

    @pytest.mark.usefixtures("db_session")
    def test_when_user_is_logged_in_and_booking_has_been_cancelled_already(self, client):
        booking = bookings_factories.CancelledBookingFactory()
        user = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=booking.offerer)
        url = f"/v2/bookings/keep/token/{booking.token}"

        response = client.with_session_auth(user.email).patch(url)

        # Then
        booking = db.session.get(Booking, booking.id)
        assert response.status_code == 410
        assert response.json["booking"] == ["Cette réservation a été annulée"]
        assert booking.status is BookingStatus.CANCELLED

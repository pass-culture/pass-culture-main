import pytest

import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.users import factories as users_factories
from pcapi.models import db


@pytest.mark.usefixtures("db_session")
class Returns204Test:
    def test_when_user_is_logged_in_and_regular_offer(self, client):
        booking = bookings_factories.UsedBookingFactory()
        pro_user = offerers_factories.UserOffererFactory(offerer=booking.offerer).user

        response = client.with_session_auth(pro_user.email).patch(f"/bookings/keep/token/{booking.token}")

        assert response.status_code == 204
        booking = db.session.query(Booking).one()
        assert booking.status == BookingStatus.CONFIRMED
        assert booking.dateUsed is None

    def test_when_user_is_logged_in_expect_booking_with_token_in_lower_case_to_be_used(self, client):
        booking = bookings_factories.UsedBookingFactory()
        pro_user = offerers_factories.UserOffererFactory(offerer=booking.offerer).user

        response = client.with_session_auth(pro_user.email).patch(f"/bookings/keep/token/{booking.token.lower()}")

        assert response.status_code == 204
        booking = db.session.query(Booking).one()
        assert booking.status == BookingStatus.CONFIRMED
        assert booking.dateUsed is None


class Returns401Test:
    @pytest.mark.usefixtures("db_session")
    def test_when_user_not_logged_in(self, client):
        booking = bookings_factories.BookingFactory()
        response = client.patch(f"/bookings/keep/token/{booking.token}")
        assert response.status_code == 401


class Returns403Test:
    @pytest.mark.usefixtures("db_session")
    def test_when_user_is_not_attached_to_linked_offerer(self, client):
        booking = bookings_factories.UsedBookingFactory()
        another_pro_user = offerers_factories.UserOffererFactory().user

        response = client.with_session_auth(another_pro_user.email).patch(
            f"/bookings/keep/token/{booking.token}?email={booking.email}"
        )

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
        response = client.with_session_auth(user.email).patch("/bookings/keep/token/")
        assert response.status_code == 404

    @pytest.mark.usefixtures("db_session")
    def test_unknown_token(self, client):
        user = users_factories.ProFactory()
        response = client.with_session_auth(user.email).patch("/bookings/keep/token/UNKNOWN")
        assert response.status_code == 404
        assert response.json["global"] == ["Cette contremarque n'a pas été trouvée"]


class Returns410Test:
    @pytest.mark.usefixtures("db_session")
    def test_when_booking_has_not_been_used_yet(self, client):
        booking = bookings_factories.BookingFactory()
        pro_user = offerers_factories.UserOffererFactory(offerer=booking.offerer).user

        response = client.with_session_auth(pro_user.email).patch(f"/bookings/keep/token/{booking.token}")

        assert response.status_code == 410
        assert response.json["booking"] == ["Cette réservation n'a pas encore été validée"]
        assert booking.status == BookingStatus.CONFIRMED

    @pytest.mark.usefixtures("db_session")
    def test_when_user_is_logged_in_and_booking_payment_exists(self, client):
        booking = bookings_factories.ReimbursedBookingFactory()
        pro_user = offerers_factories.UserOffererFactory(offerer=booking.offerer).user

        response = client.with_session_auth(pro_user.email).patch(f"/bookings/keep/token/{booking.token}")

        assert response.status_code == 410
        assert response.json["payment"] == ["Le remboursement est en cours de traitement"]
        assert booking.status is BookingStatus.REIMBURSED

    @pytest.mark.usefixtures("db_session")
    def test_when_user_is_logged_in_and_booking_has_been_cancelled_already(self, client):
        booking = bookings_factories.CancelledBookingFactory()
        user = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=booking.offerer)

        response = client.with_session_auth(user.email).patch(f"/bookings/keep/token/{booking.token}")

        booking = db.session.get(Booking, booking.id)
        assert response.status_code == 410
        assert response.json["booking"] == ["Cette réservation a été annulée"]
        assert booking.status is BookingStatus.CANCELLED

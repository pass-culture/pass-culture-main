import pytest

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.users import factories as users_factories
from pcapi.models import db


pytestmark = pytest.mark.usefixtures("db_session")


class Returns204Test:
    def test_when_user_is_logged_in_and_regular_offer(self, client):
        booking = bookings_factories.BookingFactory(token="ABCDEF")
        pro_user = users_factories.ProFactory(email="pro@example.com")
        offerers_factories.UserOffererFactory(user=pro_user, offerer=booking.offerer)

        response = client.with_session_auth("pro@example.com").patch(f"/bookings/use/token/{booking.token}")

        assert response.status_code == 204
        booking = db.session.query(Booking).one()
        assert booking.status is BookingStatus.USED

    def test_when_user_is_logged_in_expect_booking_with_token_in_lower_case_to_be_used(self, client):
        booking = bookings_factories.BookingFactory(token="ABCDEF")
        pro_user = users_factories.ProFactory(email="pro@example.com")
        offerers_factories.UserOffererFactory(user=pro_user, offerer=booking.offerer)

        response = client.with_session_auth("pro@example.com").patch(f"/bookings/use/token/{booking.token}")

        assert response.status_code == 204
        booking = db.session.query(Booking).one()
        assert booking.status is BookingStatus.USED


class Returns401Test:
    def test_when_user_not_logged_in(self, client):
        response = client.patch("/bookings/use/token/TOKEN")
        assert response.status_code == 401


class Returns403Test:
    def test_when_user_is_not_attached_to_linked_offerer(self, client):
        booking = bookings_factories.BookingFactory()
        another_pro_user = offerers_factories.UserOffererFactory().user

        response = client.with_session_auth(another_pro_user.email).patch(f"/bookings/use/token/{booking.token}")

        assert response.status_code == 403
        assert response.json["user"] == [
            "Vous n’avez pas les droits suffisants pour valider cette contremarque car cette réservation n'a pas été faite sur une de vos offres, ou que votre rattachement à la structure est encore en cours de validation"
        ]
        booking = db.session.get(Booking, booking.id)
        assert booking.status == BookingStatus.CONFIRMED

    def test_when_offerer_is_closed(self, client):
        offerer = offerers_factories.ClosedOffererFactory()
        booking = bookings_factories.BookingFactory(stock__offer__venue__managingOfferer=offerer)
        pro_user = offerers_factories.UserOffererFactory(offerer=offerer).user

        response = client.with_session_auth(pro_user.email).patch(f"/bookings/use/token/{booking.token}")

        assert response.status_code == 403
        assert response.json["booking"] == ["Vous ne pouvez plus valider de contremarque sur une structure fermée"]
        booking = db.session.get(Booking, booking.id)
        assert booking.status == BookingStatus.CONFIRMED


class Returns404Test:
    def test_missing_token(self, client):
        response = client.patch("/bookings/use/token/")
        assert response.status_code == 404

    def test_unknown_token(self, client):
        pro_user = users_factories.ProFactory()
        response = client.with_session_auth(pro_user.email).patch("/bookings/use/token/UNKNOWN")
        assert response.status_code == 404
        assert response.json["global"] == ["Cette contremarque n'a pas été trouvée"]


class Returns410Test:
    def test_when_user_is_logged_in_and_booking_has_been_cancelled_already(self, client):
        booking = bookings_factories.CancelledBookingFactory()
        user = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=booking.offerer)

        response = client.with_session_auth(user.email).patch(f"/bookings/use/token/{booking.token}")

        assert response.status_code == 410
        assert response.json["booking_cancelled"] == ["Cette réservation a été annulée"]
        booking = db.session.get(Booking, booking.id)
        assert booking.status == BookingStatus.CANCELLED

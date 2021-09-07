from datetime import datetime
from datetime import timedelta

import pytest

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.bookings.models import BookingStatus
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.models import Booking
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


class Returns200Test:
    @pytest.mark.usefixtures("db_session")
    def expect_the_booking_to_be_cancelled_by_current_user(self, app):
        # Given
        in_four_days = datetime.utcnow() + timedelta(days=4)
        stock = offers_factories.EventStockFactory(beginningDatetime=in_four_days)
        booking = bookings_factories.BookingFactory(stock=stock)

        # When
        client = TestClient(app.test_client()).with_session_auth(booking.user.email)
        response = client.put(f"/bookings/{humanize(booking.id)}/cancel")
        booking = Booking.query.get(booking.id)

        # Then
        assert response.status_code == 200
        assert booking.isCancelled
        assert booking.status is BookingStatus.CANCELLED
        assert response.json == {
            "amount": 10.0,
            "completedUrl": None,
            "id": humanize(booking.id),
            "isCancelled": True,
            "quantity": booking.quantity,
            "stock": {"price": 10.0},
            "stockId": humanize(stock.id),
            "token": booking.token,
            "activationCode": None,
            "qrCode": None,
        }


class Returns400Test:
    @pytest.mark.usefixtures("db_session")
    def when_the_booking_cannot_be_cancelled(self, app):
        # Given
        booking = bookings_factories.UsedBookingFactory()

        # When
        client = TestClient(app.test_client()).with_session_auth(booking.user.email)
        response = client.put(f"/bookings/{humanize(booking.id)}/cancel")
        booking = Booking.query.get(booking.id)

        # Then
        assert response.status_code == 400
        assert response.json["booking"] == ["Impossible d'annuler une réservation consommée"]
        assert not booking.isCancelled
        assert booking.status is BookingStatus.USED


class Returns404Test:
    @pytest.mark.usefixtures("db_session")
    def when_cancelling_a_booking_of_someone_else(self, app):
        # Given
        booking = bookings_factories.UsedBookingFactory()
        user2 = users_factories.BeneficiaryGrant18Factory()

        # When
        client = TestClient(app.test_client()).with_session_auth(user2.email)
        response = client.put(f"/bookings/{humanize(booking.id)}/cancel")
        booking = Booking.query.get(booking.id)

        # Then
        assert response.status_code == 404
        assert not booking.isCancelled
        assert booking.status is not BookingStatus.CANCELLED

    @pytest.mark.usefixtures("db_session")
    def when_the_booking_does_not_exist(self, app):
        # Given
        user = users_factories.BeneficiaryGrant18Factory()

        # When
        client = TestClient(app.test_client()).with_session_auth(user.email)
        response = client.put("/bookings/AX/cancel")

        # Then
        assert response.status_code == 404

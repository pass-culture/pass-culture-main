from unittest import mock

import pytest

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingStatus
import pcapi.core.users.factories as users_factories

from tests.conftest import TestClient


@pytest.mark.usefixtures("db_session")
@mock.patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token", lambda *args, **kwargs: True)
class BookingViewTest:
    def test_search_booking(self, app):
        users_factories.UserFactory(email="admin@example.com", isAdmin=True)
        booking = bookings_factories.BookingFactory()

        client = TestClient(app.test_client()).with_auth("admin@example.com")
        response = client.post("/pc/back-office/bookings/", form={"token": booking.token})

        assert response.status_code == 200
        content = response.data.decode(response.charset)
        assert booking.user.email in content
        assert "Marquer comme utilisée" not in content

    def test_show_mark_as_used_button(self, app):
        users_factories.UserFactory(email="admin@example.com", isAdmin=True)
        bookings_factories.BookingFactory(isCancelled=True, status=BookingStatus.CANCELLED, token="ABCDEF")

        client = TestClient(app.test_client()).with_auth("admin@example.com")
        response = client.post("/pc/back-office/bookings/", form={"token": "abcdeF"})

        assert response.status_code == 200
        content = response.data.decode(response.charset)
        assert "Marquer comme utilisée" in content

    def test_uncancel_and_mark_as_used(self, app):
        users_factories.UserFactory(email="admin@example.com", isAdmin=True)
        booking = bookings_factories.BookingFactory(isCancelled=True, status=BookingStatus.CANCELLED)

        client = TestClient(app.test_client()).with_auth("admin@example.com")
        response = client.post("/pc/back-office/bookings/mark-as-used", form={"booking_id": booking.id})

        assert response.status_code == 302
        assert response.location == f"http://localhost/pc/back-office/bookings/?id={booking.id}"
        response = client.get(response.location)
        content = response.data.decode(response.charset)
        assert "La réservation a été dés-annulée et marquée comme utilisée." in content
        booking = Booking.query.get(booking.id)
        assert not booking.isCancelled
        assert booking.status is not BookingStatus.CANCELLED
        assert booking.isUsed
        assert booking.status is BookingStatus.USED

    def test_fail_to_uncancel_and_mark_as_used(self, app):
        users_factories.UserFactory(email="admin@example.com", isAdmin=True)
        booking = bookings_factories.BookingFactory()

        client = TestClient(app.test_client()).with_auth("admin@example.com")
        response = client.post("/pc/back-office/bookings/mark-as-used", form={"booking_id": booking.id})

        assert response.status_code == 302
        assert response.location == f"http://localhost/pc/back-office/bookings/?id={booking.id}"
        response = client.get(response.location)
        content = response.data.decode(response.charset)
        assert "ne peut pas être validée via ce formulaire." in content
        booking = Booking.query.get(booking.id)
        assert not booking.isUsed

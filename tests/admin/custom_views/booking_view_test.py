from unittest import mock

import pytest

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingStatus
import pcapi.core.payments.factories as payments_factories
import pcapi.core.users.factories as users_factories

from tests.conftest import TestClient


@pytest.mark.usefixtures("db_session")
@mock.patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token", lambda *args, **kwargs: True)
class BookingViewTest:
    def test_search_booking(self, app):
        users_factories.AdminFactory(email="admin@example.com")
        booking = bookings_factories.BookingFactory()

        client = TestClient(app.test_client()).with_auth("admin@example.com")
        response = client.post("/pc/back-office/bookings/", form={"token": booking.token})

        assert response.status_code == 200
        content = response.data.decode(response.charset)
        assert booking.user.email in content
        assert "Marquer comme utilisée" not in content

    def test_show_mark_as_used_button(self, app):
        users_factories.AdminFactory(email="admin@example.com")
        bookings_factories.CancelledBookingFactory(token="ABCDEF")

        client = TestClient(app.test_client()).with_auth("admin@example.com")
        response = client.post("/pc/back-office/bookings/", form={"token": "abcdeF"})

        assert response.status_code == 200
        content = response.data.decode(response.charset)
        assert "Marquer comme utilisée" in content

    def test_uncancel_and_mark_as_used(self, app):
        users_factories.AdminFactory(email="admin@example.com")
        booking = bookings_factories.CancelledBookingFactory()

        client = TestClient(app.test_client()).with_auth("admin@example.com")
        route = f"/pc/back-office/bookings/mark-as-used/{booking.id}"
        response = client.post(route, form={})

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
        users_factories.AdminFactory(email="admin@example.com")
        booking = bookings_factories.BookingFactory()

        client = TestClient(app.test_client()).with_auth("admin@example.com")
        route = f"/pc/back-office/bookings/mark-as-used/{booking.id}"
        response = client.post(route, form={})

        assert response.status_code == 302
        assert response.location == f"http://localhost/pc/back-office/bookings/?id={booking.id}"
        response = client.get(response.location)
        content = response.data.decode(response.charset)
        assert "ne peut pas être validée via ce formulaire." in content
        booking = Booking.query.get(booking.id)
        assert not booking.isUsed

    def test_cancel_booking(self, app, client):
        admin = users_factories.AdminFactory()
        booking = bookings_factories.BookingFactory(isCancelled=False)

        route = f"/pc/back-office/bookings/cancel/{booking.id}"
        response = client.with_auth(admin.email).post(route, form={})

        assert response.status_code == 302
        assert response.location == f"http://localhost/pc/back-office/bookings/?id={booking.id}"

        response = client.get(response.location)
        content = response.data.decode(response.charset)
        assert "La réservation a été marquée comme annulée" in content

        booking = Booking.query.get(booking.id)
        assert booking.isCancelled

    def test_can_not_cancel_refunded_booking(self, app):
        users_factories.UserFactory(email="admin@example.com", isAdmin=True)
        booking = payments_factories.PaymentFactory().booking

        client = TestClient(app.test_client()).with_auth("admin@example.com")
        route = f"/pc/back-office/bookings/cancel/{booking.id}"
        response = client.post(route, form={})

        assert response.status_code == 302
        assert response.location == f"http://localhost/pc/back-office/bookings/?id={booking.id}"

        response = client.get(response.location)
        content = response.data.decode(response.charset)
        assert "L&#39;opération a échoué : la réservation a déjà été remboursée" in content

        booking = Booking.query.get(booking.id)
        assert not booking.isCancelled

    def test_cant_cancel_cancelled_booking(self, app):
        users_factories.UserFactory(email="admin@example.com", isAdmin=True)
        booking = bookings_factories.CancelledBookingFactory()

        client = TestClient(app.test_client()).with_auth("admin@example.com")
        route = f"/pc/back-office/bookings/cancel/{booking.id}"
        response = client.post(route, form={})

        assert response.status_code == 302
        assert response.location == f"http://localhost/pc/back-office/bookings/?id={booking.id}"

        response = client.get(response.location)
        content = response.data.decode(response.charset)
        assert "L&#39;opération a échoué : la réservation a déjà été annulée" in content

        booking = Booking.query.get(booking.id)
        assert booking.isCancelled

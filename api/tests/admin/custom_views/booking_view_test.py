# import datetime
# from unittest import mock

# from dateutil.relativedelta import relativedelta
# from freezegun import freeze_time
# import pytest

# import pcapi.core.bookings.factories as bookings_factories
# from pcapi.core.bookings.models import Booking
# from pcapi.core.bookings.models import BookingStatus
# import pcapi.core.educational.factories as educational_factories
# from pcapi.core.educational.models import CollectiveBooking
# from pcapi.core.educational.models import CollectiveBookingCancellationReasons
# from pcapi.core.educational.models import CollectiveBookingStatus
# import pcapi.core.finance.factories as finance_factories
# import pcapi.core.users.factories as users_factories

# from tests.conftest import TestClient


# @pytest.mark.usefixtures("db_session")
# @mock.patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token", lambda *args, **kwargs: True)
# class BookingViewTest:
#     def test_search_booking(self, app):
#         users_factories.AdminFactory(email="admin@example.com")
#         booking = bookings_factories.BookingFactory()

#         client = TestClient(app.test_client()).with_session_auth("admin@example.com")
#         response = client.post("/pc/back-office/bookings/", form={"token": booking.token})

#         assert response.status_code == 200
#         content = response.data.decode(response.charset)
#         assert booking.email in content
#         assert "Désannuler" not in content

#     def test_show_mark_as_used_button(self, app):
#         users_factories.AdminFactory(email="admin@example.com")
#         bookings_factories.CancelledBookingFactory(token="ABCDEF")

#         client = TestClient(app.test_client()).with_session_auth("admin@example.com")
#         response = client.post("/pc/back-office/bookings/", form={"token": "abcdeF"})

#         assert response.status_code == 200
#         content = response.data.decode(response.charset)
#         assert "Désannuler" in content

#     def test_uncancel_and_mark_as_used(self, app):
#         users_factories.AdminFactory(email="admin@example.com")
#         booking = bookings_factories.CancelledBookingFactory()

#         client = TestClient(app.test_client()).with_session_auth("admin@example.com")
#         route = f"/pc/back-office/bookings/mark-as-used/{booking.id}"
#         response = client.post(route, form={})

#         assert response.status_code == 302
#         assert response.location == f"http://localhost/pc/back-office/bookings/?id={booking.id}"
#         response = client.get(response.location)
#         content = response.data.decode(response.charset)
#         assert "La réservation a été dés-annulée et marquée comme utilisée." in content
#         booking = Booking.query.get(booking.id)
#         assert booking.status is not BookingStatus.CANCELLED
#         assert booking.status is BookingStatus.USED

#     def test_fail_to_uncancel_and_mark_as_used(self, app):
#         users_factories.AdminFactory(email="admin@example.com")
#         booking = bookings_factories.BookingFactory(status=BookingStatus.CONFIRMED)

#         client = TestClient(app.test_client()).with_session_auth("admin@example.com")
#         route = f"/pc/back-office/bookings/mark-as-used/{booking.id}"
#         response = client.post(route, form={})

#         assert response.status_code == 302
#         assert response.location == f"http://localhost/pc/back-office/bookings/?id={booking.id}"
#         response = client.get(response.location)
#         content = response.data.decode(response.charset)
#         assert "ne peut pas être validée via ce formulaire." in content
#         booking = Booking.query.get(booking.id)
#         assert booking.status is BookingStatus.CONFIRMED

#     def test_cancel_booking(self, app, client):
#         admin = users_factories.AdminFactory()
#         booking = bookings_factories.BookingFactory()

#         route = f"/pc/back-office/bookings/cancel/{booking.id}"
#         response = client.with_session_auth(admin.email).post(route, form={})

#         assert response.status_code == 302
#         assert response.location == f"http://localhost/pc/back-office/bookings/?id={booking.id}"

#         response = client.get(response.location)
#         content = response.data.decode(response.charset)
#         assert "La réservation a été marquée comme annulée" in content

#         booking = Booking.query.get(booking.id)
#         assert booking.status == BookingStatus.CANCELLED

#     def test_can_not_cancel_refunded_booking(self, app):
#         users_factories.AdminFactory(email="admin@example.com")
#         booking = bookings_factories.UsedBookingFactory()
#         finance_factories.PaymentFactory(booking=booking)

#         client = TestClient(app.test_client()).with_session_auth("admin@example.com")
#         route = f"/pc/back-office/bookings/cancel/{booking.id}"
#         response = client.post(route, form={})

#         assert response.status_code == 302
#         assert response.location == f"http://localhost/pc/back-office/bookings/?id={booking.id}"

#         response = client.get(response.location)
#         content = response.data.decode(response.charset)
#         assert "L&#39;opération a échoué : la réservation a déjà été remboursée" in content

#         booking = Booking.query.get(booking.id)
#         assert not booking.status == BookingStatus.CANCELLED

#     def test_cant_cancel_cancelled_booking(self, app):
#         users_factories.AdminFactory(email="admin@example.com")
#         booking = bookings_factories.CancelledBookingFactory()

#         client = TestClient(app.test_client()).with_session_auth("admin@example.com")
#         route = f"/pc/back-office/bookings/cancel/{booking.id}"
#         response = client.post(route, form={})

#         assert response.status_code == 302
#         assert response.location == f"http://localhost/pc/back-office/bookings/?id={booking.id}"

#         response = client.get(response.location)
#         content = response.data.decode(response.charset)
#         assert "L&#39;opération a échoué : la réservation a déjà été annulée" in content

#         booking = Booking.query.get(booking.id)
#         assert booking.status == BookingStatus.CANCELLED

#     def test_cancel_used_booking_without_payment(self, app):
#         users_factories.AdminFactory(email="admin@example.com")
#         booking = bookings_factories.UsedBookingFactory()

#         client = TestClient(app.test_client()).with_session_auth("admin@example.com")
#         route = f"/pc/back-office/bookings/cancel/{booking.id}"
#         response = client.post(route, form={})

#         assert response.status_code == 302
#         assert response.location == f"http://localhost/pc/back-office/bookings/?id={booking.id}"

#         response = client.get(response.location)
#         content = response.data.decode(response.charset)
#         assert "La réservation a été marquée comme annulée" in content

#         booking = Booking.query.get(booking.id)
#         assert booking.status == BookingStatus.CANCELLED


# @pytest.mark.usefixtures("db_session")
# @mock.patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token", lambda *args, **kwargs: True)
# class CollectiveBookingViewTest:
#     def test_search_booking(self, client):
#         users_factories.AdminFactory(email="admin@example.com")
#         booking = educational_factories.CollectiveBookingFactory()

#         response = client.with_session_auth("admin@example.com").post(
#             "/pc/back-office/collective-bookings/", form={"booking_id": booking.id}
#         )

#         assert response.status_code == 200
#         content = response.data.decode(response.charset)
#         assert booking.collectiveStock.collectiveOffer.name in content
#         assert "Désannuler" not in content

#     def test_show_mark_as_used_button(self, client):
#         users_factories.AdminFactory(email="admin@example.com")
#         booking = educational_factories.CollectiveBookingFactory(
#             cancellationDate=datetime.datetime.utcnow(),
#             cancellationReason=CollectiveBookingCancellationReasons.OFFERER,
#             status=CollectiveBookingStatus.CANCELLED,
#         )

#         response = client.with_session_auth("admin@example.com").post(
#             "/pc/back-office/collective-bookings/", form={"booking_id": booking.id}
#         )

#         assert response.status_code == 200
#         content = response.data.decode(response.charset)
#         assert "Désannuler" in content

#     def test_uncancel_and_mark_as_confirmed(self, client):
#         users_factories.AdminFactory(email="admin@example.com")
#         booking = educational_factories.CollectiveBookingFactory(
#             cancellationDate=datetime.datetime.utcnow(),
#             cancellationReason=CollectiveBookingCancellationReasons.OFFERER,
#             status=CollectiveBookingStatus.CANCELLED,
#         )

#         route = f"/pc/back-office/collective-bookings/mark-as-used/{booking.id}"
#         response = client.with_session_auth("admin@example.com").post(route, form={})

#         assert response.status_code == 302
#         assert response.location == f"http://localhost/pc/back-office/collective-bookings/?id={booking.id}"
#         response = client.with_session_auth("admin@example.com").get(response.location)
#         content = response.data.decode(response.charset)
#         assert "La réservation a été dés-annulée et marquée comme confirmé ou préreservé." in content
#         booking = CollectiveBooking.query.get(booking.id)
#         assert booking.status is not CollectiveBookingStatus.CANCELLED
#         assert booking.status is CollectiveBookingStatus.CONFIRMED

#     def test_fail_to_uncancel_and_mark_as_used(self, client):
#         users_factories.AdminFactory(email="admin@example.com")
#         booking = educational_factories.CollectiveBookingFactory(status=CollectiveBookingStatus.CONFIRMED)

#         route = f"/pc/back-office/collective-bookings/mark-as-used/{booking.id}"
#         response = client.with_session_auth("admin@example.com").post(route, form={})

#         assert response.status_code == 302
#         assert response.location == f"http://localhost/pc/back-office/collective-bookings/?id={booking.id}"
#         response = client.with_session_auth("admin@example.com").get(response.location)
#         content = response.data.decode(response.charset)
#         assert "ne peut pas être validée via ce formulaire." in content
#         booking = CollectiveBooking.query.get(booking.id)
#         assert booking.status is CollectiveBookingStatus.CONFIRMED

#     def test_cancel_booking(self, app, client):
#         users_factories.AdminFactory(email="admin@example.com")
#         booking = educational_factories.CollectiveBookingFactory()

#         route = f"/pc/back-office/collective-bookings/cancel/{booking.id}"
#         response = client.with_session_auth("admin@example.com").post(route, form={})

#         assert response.status_code == 302
#         assert response.location == f"http://localhost/pc/back-office/collective-bookings/?id={booking.id}"

#         response = client.with_session_auth("admin@example.com").get(response.location)
#         content = response.data.decode(response.charset)
#         assert "La réservation a été marquée comme annulée" in content

#         booking = CollectiveBooking.query.get(booking.id)
#         assert booking.status == CollectiveBookingStatus.CANCELLED

#     def test_can_not_cancel_refunded_booking(self, client):
#         users_factories.AdminFactory(email="admin@example.com")
#         booking = educational_factories.CollectiveBookingFactory(status=CollectiveBookingStatus.USED)
#         finance_factories.PaymentFactory(collectiveBooking=booking)

#         route = f"/pc/back-office/collective-bookings/cancel/{booking.id}"
#         response = client.with_session_auth("admin@example.com").post(route, form={})

#         assert response.status_code == 302
#         assert response.location == f"http://localhost/pc/back-office/collective-bookings/?id={booking.id}"

#         response = client.with_session_auth("admin@example.com").get(response.location)
#         content = response.data.decode(response.charset)
#         assert "L&#39;opération a échoué : la réservation a déjà été remboursée" in content

#         booking = CollectiveBooking.query.get(booking.id)
#         assert not booking.status == BookingStatus.CANCELLED

#     def test_cant_cancel_cancelled_booking(self, client):
#         users_factories.AdminFactory(email="admin@example.com")
#         booking = educational_factories.CollectiveBookingFactory(
#             cancellationDate=datetime.datetime.utcnow(),
#             cancellationReason=CollectiveBookingCancellationReasons.OFFERER,
#             status=CollectiveBookingStatus.CANCELLED,
#         )

#         route = f"/pc/back-office/collective-bookings/cancel/{booking.id}"
#         response = client.with_session_auth("admin@example.com").post(route, form={})

#         assert response.status_code == 302
#         assert response.location == f"http://localhost/pc/back-office/collective-bookings/?id={booking.id}"

#         response = client.with_session_auth("admin@example.com").get(response.location)
#         content = response.data.decode(response.charset)
#         assert "L&#39;opération a échoué : la réservation a déjà été annulée" in content

#         booking = CollectiveBooking.query.get(booking.id)
#         assert booking.status == CollectiveBookingStatus.CANCELLED

#     def test_cancel_used_booking_without_payment(self, client):
#         users_factories.AdminFactory(email="admin@example.com")
#         booking = educational_factories.CollectiveBookingFactory(status=CollectiveBookingStatus.USED)

#         route = f"/pc/back-office/collective-bookings/cancel/{booking.id}"
#         response = client.with_session_auth("admin@example.com").post(route, form={})

#         assert response.status_code == 302
#         assert response.location == f"http://localhost/pc/back-office/collective-bookings/?id={booking.id}"

#         response = client.get(response.location)
#         content = response.data.decode(response.charset)
#         assert "La réservation a été marquée comme annulée" in content

#         booking = CollectiveBooking.query.get(booking.id)
#         assert booking.status == CollectiveBookingStatus.CANCELLED

#     @freeze_time("2023-02-02 15:00:00")
#     def test_uncancel_with_datetime_before_now(self, client):
#         users_factories.AdminFactory(email="admin@example.com")

#         stock = educational_factories.CollectiveStockFactory(
#             beginningDatetime=datetime.datetime.utcnow() - relativedelta(days=1)
#         )
#         booking = educational_factories.CollectiveBookingFactory(
#             collectiveStock=stock,
#             cancellationDate=datetime.datetime.utcnow(),
#             cancellationReason=CollectiveBookingCancellationReasons.OFFERER,
#             status=CollectiveBookingStatus.CANCELLED,
#         )

#         route = f"/pc/back-office/collective-bookings/mark-as-used/{booking.id}"
#         response = client.with_session_auth("admin@example.com").post(route, form={})

#         assert response.status_code == 302
#         assert booking.status is CollectiveBookingStatus.USED
#         assert booking.dateUsed == datetime.datetime.utcnow()

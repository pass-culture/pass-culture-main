from datetime import datetime
from datetime import timedelta

from flask_jwt_extended.utils import create_access_token
from freezegun import freeze_time
import pytest

from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.bookings.factories import CancelledBookingFactory
from pcapi.core.bookings.factories import UsedBookingFactory
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingCancellationReasons
from pcapi.core.categories import subcategories
from pcapi.core.offers.factories import EventStockFactory
from pcapi.core.offers.factories import MediationFactory
from pcapi.core.offers.factories import StockFactory
from pcapi.core.offers.factories import StockWithActivationCodesFactory
from pcapi.core.testing import assert_num_queries
from pcapi.core.testing import override_features
from pcapi.core.users import factories as users_factories
from pcapi.models.db import db
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


pytestmark = pytest.mark.usefixtures("db_session")


class PostBookingTest:
    identifier = "pascal.ture@example.com"

    def test_post_bookings(self, app):
        stock = StockFactory()
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)

        access_token = create_access_token(identity=self.identifier)
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}

        response = test_client.post("/native/v1/bookings", json={"stockId": stock.id, "quantity": 1})

        assert response.status_code == 200

        booking = Booking.query.filter(Booking.stockId == stock.id).first()
        assert booking.userId == user.id
        assert response.json["bookingId"] == booking.id

    def test_no_stock_found(self, app):
        users_factories.BeneficiaryGrant18Factory(email=self.identifier)

        access_token = create_access_token(identity=self.identifier)
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}

        response = test_client.post("/native/v1/bookings", json={"stockId": 400, "quantity": 1})

        assert response.status_code == 400

    def test_insufficient_credit(self, app):
        users_factories.BeneficiaryGrant18Factory(email=self.identifier)
        stock = StockFactory(price=501)

        access_token = create_access_token(identity=self.identifier)
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}

        response = test_client.post("/native/v1/bookings", json={"stockId": stock.id, "quantity": 1})

        assert response.status_code == 400
        assert response.json["code"] == "INSUFFICIENT_CREDIT"

    def test_already_booked(self, app):
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)
        booking = BookingFactory(user=user)

        access_token = create_access_token(identity=self.identifier)
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}

        response = test_client.post("/native/v1/bookings", json={"stockId": booking.stock.id, "quantity": 1})

        assert response.status_code == 400
        assert response.json["code"] == "ALREADY_BOOKED"


class GetBookingsTest:
    identifier = "pascal.ture@example.com"

    @freeze_time("2021-03-12")
    @override_features(AUTO_ACTIVATE_DIGITAL_BOOKINGS=True)
    def test_get_bookings(self, app):
        OFFER_URL = "https://demo.pass/some/path?token={token}&email={email}&offerId={offerId}"
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)

        permanent_booking = UsedBookingFactory(
            user=user,
            stock__offer__subcategoryId=subcategories.TELECHARGEMENT_LIVRE_AUDIO.id,
            dateUsed=datetime(2021, 2, 3),
        )

        event_booking = BookingFactory(user=user, stock=EventStockFactory(beginningDatetime=datetime(2021, 3, 14)))

        digital_stock = StockWithActivationCodesFactory()
        first_activation_code = digital_stock.activationCodes[0]
        second_activation_code = digital_stock.activationCodes[1]
        digital_booking = UsedBookingFactory(
            user=user,
            stock=digital_stock,
            activationCode=first_activation_code,
        )
        ended_digital_booking = UsedBookingFactory(
            user=user,
            displayAsEnded=True,
            stock=digital_stock,
            activationCode=second_activation_code,
        )
        expire_tomorrow = BookingFactory(user=user, dateCreated=datetime.now() - timedelta(days=29))
        used_but_in_future = UsedBookingFactory(
            user=user,
            dateUsed=datetime(2021, 3, 11),
            stock=StockFactory(beginningDatetime=datetime(2021, 3, 15)),
        )

        cancelled_permanent_booking = CancelledBookingFactory(
            user=user,
            stock__offer__subcategoryId=subcategories.TELECHARGEMENT_LIVRE_AUDIO.id,
            cancellation_date=datetime(2021, 3, 10),
        )
        cancelled = CancelledBookingFactory(user=user, cancellation_date=datetime(2021, 3, 8))
        used1 = UsedBookingFactory(user=user, dateUsed=datetime(2021, 3, 1))
        used2 = UsedBookingFactory(
            user=user,
            displayAsEnded=True,
            dateUsed=datetime(2021, 3, 2),
            stock__offer__url=OFFER_URL,
            cancellation_limit_date=datetime(2021, 3, 2),
        )

        mediation = MediationFactory(id=111, offer=used2.stock.offer, thumbCount=1, credit="street credit")

        access_token = create_access_token(identity=self.identifier)
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}

        # 1: get the user
        # 1: get the bookings
        # 1: get AUTO_ACTIVATE_DIGITAL_BOOKINGS feature
        # 1: rollback
        with assert_num_queries(4):
            response = test_client.get("/native/v1/bookings")

        assert response.status_code == 200
        assert [b["id"] for b in response.json["ongoing_bookings"]] == [
            expire_tomorrow.id,
            event_booking.id,
            used_but_in_future.id,
            digital_booking.id,
            permanent_booking.id,
        ]

        assert response.json["ongoing_bookings"][3]["activationCode"]

        assert [b["id"] for b in response.json["ended_bookings"]] == [
            ended_digital_booking.id,
            cancelled_permanent_booking.id,
            cancelled.id,
            used2.id,
            used1.id,
        ]

        assert response.json["ended_bookings"][3] == {
            "activationCode": None,
            "cancellationDate": None,
            "cancellationReason": None,
            "confirmationDate": "2021-03-02T00:00:00Z",
            "completedUrl": f"https://demo.pass/some/path?token={used2.token}&email=pascal.ture@example.com&offerId={humanize(used2.stock.offer.id)}",
            "dateUsed": "2021-03-02T00:00:00Z",
            "expirationDate": None,
            "quantity": 1,
            "qrCodeData": None,
            "id": used2.id,
            "stock": {
                "beginningDatetime": None,
                "id": used2.stock.id,
                "offer": {
                    "category": {
                        "categoryType": "Thing",
                        "label": "Support physique (DVD, Blu-ray...)",
                        "name": "FILM",
                    },
                    "subcategoryId": subcategories.SUPPORT_PHYSIQUE_FILM.id,
                    "extraData": None,
                    "id": used2.stock.offer.id,
                    "image": {"credit": "street credit", "url": mediation.thumbUrl},
                    "isDigital": True,
                    "isPermanent": False,
                    "name": used2.stock.offer.name,
                    "url": f"https://demo.pass/some/path?token={used2.token}&email=pascal.ture@example.com&offerId={humanize(used2.stock.offer.id)}",
                    "venue": {
                        "city": "Paris",
                        "coordinates": {"latitude": 48.87004, "longitude": 2.3785},
                        "id": used2.venue.id,
                        "name": used2.venue.name,
                        "publicName": used2.venue.publicName,
                    },
                    "withdrawalDetails": None,
                },
            },
            "token": used2.token,
            "totalAmount": 1000,
        }

        for booking in response.json["ongoing_bookings"]:
            assert booking["qrCodeData"] is not None


class CancelBookingTest:
    identifier = "pascal.ture@example.com"

    def test_cancel_booking(self, app):
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)
        booking = BookingFactory(user=user)

        access_token = create_access_token(identity=self.identifier)
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}

        response = test_client.post(f"/native/v1/bookings/{booking.id}/cancel")

        assert response.status_code == 204

        booking = Booking.query.get(booking.id)
        assert booking.isCancelled
        assert booking.cancellationReason == BookingCancellationReasons.BENEFICIARY

    def test_cancel_others_booking(self, app):
        users_factories.BeneficiaryGrant18Factory(email=self.identifier)
        booking = BookingFactory()

        access_token = create_access_token(identity=self.identifier)
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}

        response = test_client.post(f"/native/v1/bookings/{booking.id}/cancel")

        assert response.status_code == 404

    def test_cancel_confirmed_booking(self, app):
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)
        booking = BookingFactory(user=user, cancellation_limit_date=datetime.now() - timedelta(days=1))

        access_token = create_access_token(identity=self.identifier)
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}

        response = test_client.post(f"/native/v1/bookings/{booking.id}/cancel")

        assert response.status_code == 400
        assert response.json == {
            "code": "CONFIRMED_BOOKING",
            "message": "La date limite d'annulation est dépassée.",
        }


class ToggleBookingVisibilityTest:
    identifier = "pascal.ture@example.com"

    def test_toggle_visibility(self, app):
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)
        access_token = create_access_token(identity=self.identifier)

        booking = BookingFactory(user=user, displayAsEnded=None)
        booking_id = booking.id

        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}

        response = test_client.post(f"/native/v1/bookings/{booking_id}/toggle_display", json={"ended": True})

        assert response.status_code == 204
        db.session.refresh(booking)
        assert booking.displayAsEnded

        response = test_client.post(f"/native/v1/bookings/{booking_id}/toggle_display", json={"ended": False})

        assert response.status_code == 204
        db.session.refresh(booking)
        assert not booking.displayAsEnded

    @override_features(AUTO_ACTIVATE_DIGITAL_BOOKINGS=True)
    def test_integration_toggle_visibility(self, app):
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)
        access_token = create_access_token(identity=self.identifier)

        stock = StockWithActivationCodesFactory()
        activation_code = stock.activationCodes[0]
        booking = UsedBookingFactory(
            user=user,
            displayAsEnded=None,
            dateUsed=datetime.now(),
            stock=stock,
            activationCode=activation_code,
        )

        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}

        response = test_client.get("/native/v1/bookings")
        assert response.status_code == 200

        assert [b["id"] for b in response.json["ongoing_bookings"]] == [booking.id]
        assert [b["id"] for b in response.json["ended_bookings"]] == []

        response = test_client.post(f"/native/v1/bookings/{booking.id}/toggle_display", json={"ended": True})

        assert response.status_code == 204

        response = test_client.get("/native/v1/bookings")
        assert response.status_code == 200

        assert [b["id"] for b in response.json["ongoing_bookings"]] == []
        assert [b["id"] for b in response.json["ended_bookings"]] == [booking.id]

        response = test_client.post(f"/native/v1/bookings/{booking.id}/toggle_display", json={"ended": False})

        assert response.status_code == 204

        response = test_client.get("/native/v1/bookings")
        assert response.status_code == 200

        assert [b["id"] for b in response.json["ongoing_bookings"]] == [booking.id]
        assert [b["id"] for b in response.json["ended_bookings"]] == []

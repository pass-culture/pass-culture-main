from datetime import datetime
from datetime import timedelta

from flask_jwt_extended.utils import create_access_token
from freezegun import freeze_time
import pytest

from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingCancellationReasons
from pcapi.core.offers.factories import EventStockFactory
from pcapi.core.offers.factories import MediationFactory
from pcapi.core.offers.factories import StockFactory
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories
from pcapi.models.offer_type import ThingType

from tests.conftest import TestClient


pytestmark = pytest.mark.usefixtures("db_session")


class PostBookingTest:
    identifier = "pascal.ture@example.com"

    def test_post_bookings(self, app):
        stock = StockFactory()
        user = users_factories.UserFactory(email=self.identifier)

        access_token = create_access_token(identity=self.identifier)
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}

        response = test_client.post("/native/v1/bookings", json={"stockId": stock.id, "quantity": 1})

        assert response.status_code == 200

        booking = Booking.query.filter(Booking.stockId == stock.id).first()
        assert booking.userId == user.id
        assert response.json["bookingId"] == booking.id

    def test_no_stock_found(self, app):
        users_factories.UserFactory(email=self.identifier)

        access_token = create_access_token(identity=self.identifier)
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}

        response = test_client.post("/native/v1/bookings", json={"stockId": 400, "quantity": 1})

        assert response.status_code == 400

    def test_insufficient_credit(self, app):
        users_factories.UserFactory(email=self.identifier)
        stock = StockFactory(price=501)

        access_token = create_access_token(identity=self.identifier)
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}

        response = test_client.post("/native/v1/bookings", json={"stockId": stock.id, "quantity": 1})

        assert response.status_code == 400
        assert response.json["code"] == "INSUFFICIENT_CREDIT"

    def test_already_booked(self, app):
        user = users_factories.UserFactory(email=self.identifier)
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
    def test_get_bookings(self, app):
        OFFER_URL = "https://demo.pass/some/path"
        user = users_factories.UserFactory(email=self.identifier)

        permanent_booking = BookingFactory(
            user=user, stock__offer__type=str(ThingType.LIVRE_AUDIO), isUsed=True, dateUsed=datetime(2021, 2, 3)
        )
        cancelled_permanent_booking = BookingFactory(
            user=user,
            stock__offer__type=str(ThingType.LIVRE_AUDIO),
            isCancelled=True,
            cancellationDate=datetime(2021, 2, 3),
        )
        event_booking = BookingFactory(user=user, stock=EventStockFactory(beginningDatetime=datetime(2021, 3, 14)))
        expire_tomorrow = BookingFactory(user=user, dateCreated=datetime.now() - timedelta(days=29))
        used_but_in_future = BookingFactory(
            user=user,
            isUsed=True,
            dateUsed=datetime(2021, 3, 11),
            stock=StockFactory(beginningDatetime=datetime(2021, 3, 15)),
        )

        cancelled = BookingFactory(user=user, isCancelled=True)
        used1 = BookingFactory(user=user, isUsed=True, dateUsed=datetime(2021, 3, 1))
        used2 = BookingFactory(
            user=user,
            isUsed=True,
            dateUsed=datetime(2021, 3, 2),
            stock__offer__url=OFFER_URL,
        )

        mediation = MediationFactory(id=111, offer=used2.stock.offer, thumbCount=1, credit="street credit")

        access_token = create_access_token(identity=self.identifier)
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}

        with assert_num_queries(2):
            response = test_client.get("/native/v1/bookings")

        assert [b["id"] for b in response.json["ongoing_bookings"]] == [
            expire_tomorrow.id,
            event_booking.id,
            used_but_in_future.id,
            permanent_booking.id,
        ]

        assert [b["id"] for b in response.json["ended_bookings"]] == [
            cancelled_permanent_booking.id,
            cancelled.id,
            used2.id,
            used1.id,
        ]

        assert response.json["ended_bookings"][2] == {
            "cancellationDate": None,
            "cancellationReason": None,
            "confirmationDate": None,
            "dateUsed": "2021-03-02T00:00:00Z",
            "expirationDate": None,
            "quantity": 1,
            "qrCodeData": None,
            "id": used2.id,
            "stock": {
                "beginningDatetime": None,
                "id": used2.stock.id,
                "offer": {
                    "category": {"categoryType": "Thing", "label": "Film", "name": "FILM"},
                    "extraData": None,
                    "id": used2.stock.offer.id,
                    "image": {"credit": "street credit", "url": mediation.thumbUrl},
                    "isDigital": True,
                    "isPermanent": False,
                    "name": used2.stock.offer.name,
                    "url": OFFER_URL,
                    "venue": {
                        "city": "Paris",
                        "coordinates": {"latitude": 48.87004, "longitude": 2.3785},
                        "id": used2.stock.offer.venue.id,
                        "name": used2.stock.offer.venue.name,
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
        user = users_factories.UserFactory(email=self.identifier)
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
        users_factories.UserFactory(email=self.identifier)
        booking = BookingFactory()

        access_token = create_access_token(identity=self.identifier)
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}

        response = test_client.post(f"/native/v1/bookings/{booking.id}/cancel")

        assert response.status_code == 404

    def test_cancel_confirmed_booking(self, app):
        user = users_factories.UserFactory(email=self.identifier)
        booking = BookingFactory(user=user, confirmation_date=datetime.now() - timedelta(days=1))

        access_token = create_access_token(identity=self.identifier)
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}

        response = test_client.post(f"/native/v1/bookings/{booking.id}/cancel")

        assert response.status_code == 400
        assert response.json == {
            "code": "CONFIRMED_BOOKING",
            "message": "La date limite d'annulation est dépassée.",
        }

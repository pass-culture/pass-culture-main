from flask_jwt_extended.utils import create_access_token
import pytest

from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.bookings.models import Booking
from pcapi.core.offers.factories import StockFactory
from pcapi.core.users import factories as users_factories

from tests.conftest import TestClient


pytestmark = pytest.mark.usefixtures("db_session")


class BookOfferTest:
    identifier = "pascal.ture@example.com"

    def test_book_offer(self, app):
        stock = StockFactory()
        user = users_factories.UserFactory(email=self.identifier)

        access_token = create_access_token(identity=self.identifier)
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}

        response = test_client.post("/native/v1/book_offer", json={"stockId": stock.id, "quantity": 1})

        assert response.status_code == 204

        booking = Booking.query.filter(Booking.stockId == stock.id).first()
        assert booking.userId == user.id

    def test_no_stock_found(self, app):
        users_factories.UserFactory(email=self.identifier)

        access_token = create_access_token(identity=self.identifier)
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}

        response = test_client.post("/native/v1/book_offer", json={"stockId": 404, "quantity": 1})

        assert response.status_code == 404

    def test_insufficient_credit(self, app):
        users_factories.UserFactory(email=self.identifier)
        stock = StockFactory(price=501)

        access_token = create_access_token(identity=self.identifier)
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}

        response = test_client.post("/native/v1/book_offer", json={"stockId": stock.id, "quantity": 1})

        assert response.status_code == 400
        assert response.json["code"] == "INSUFFICIENT_CREDIT"

    def test_already_booked(self, app):
        user = users_factories.UserFactory(email=self.identifier)
        booking = BookingFactory(user=user)

        access_token = create_access_token(identity=self.identifier)
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}

        response = test_client.post("/native/v1/book_offer", json={"stockId": booking.stock.id, "quantity": 1})

        assert response.status_code == 400
        assert response.json["code"] == "ALREADY_BOOKED"

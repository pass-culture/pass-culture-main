import pytest

import pcapi.core.bookings.models as bookings_models
import pcapi.core.offers.factories as offers_factories
import pcapi.core.recommendations.factories as recommendations_factories
import pcapi.core.users.factories as users_factories
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


@pytest.mark.usefixtures("db_session")
class Returns201:
    def test_booking_creation(self, app):
        user = users_factories.UserFactory()
        stock = offers_factories.StockFactory()
        recommendation = recommendations_factories.RecommendationFactory(user=user)

        data = {"stockId": humanize(stock.id), "recommendationId": humanize(recommendation.id), "quantity": 1}
        client = TestClient(app.test_client()).with_auth(user.email)
        response = client.post("/bookings", json=data)

        booking = bookings_models.Booking.query.one()
        assert response.status_code == 201
        assert response.json == {
            "amount": 10.0,
            "completedUrl": None,
            "id": humanize(booking.id),
            "isCancelled": False,
            "quantity": 1,
            "stock": {"price": 10.0},
            "stockId": humanize(stock.id),
            "token": booking.token,
            "user": {
                "id": humanize(user.id),
                "wallet_balance": 490.0,
            },
        }


@pytest.mark.usefixtures("db_session")
class Returns400:
    def when_use_case_raise_stock_is_not_bookable_exception(self, app):
        user = users_factories.UserFactory()
        stock = offers_factories.StockFactory(quantity=0)

        data = {"stockId": humanize(stock.id), "recommendationId": None, "quantity": 1}
        client = TestClient(app.test_client()).with_auth(user.email)
        response = client.post("/bookings", json=data)

        assert response.status_code == 400
        assert response.json["stock"] == ["Ce stock n'est pas réservable"]

        assert bookings_models.Booking.query.first() is None

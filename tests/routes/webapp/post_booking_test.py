import pytest

import pcapi.core.bookings.models as bookings_models
import pcapi.core.offers.factories as offers_factories
from pcapi.core.testing import override_features
import pcapi.core.users.factories as users_factories
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


@pytest.mark.usefixtures("db_session")
class Returns201Test:
    def test_booking_creation(self, app):
        user = users_factories.BeneficiaryGrant18Factory()
        stock = offers_factories.StockFactory()

        data = {"stockId": humanize(stock.id), "quantity": 1}
        client = TestClient(app.test_client()).with_session_auth(user.email)
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
            "activationCode": None,
            "qrCode": booking.qrCode,
        }

    @override_features(ENABLE_ACTIVATION_CODES=True)
    def test_booking_creation_with_activation_code(self, app):
        # Given
        user = users_factories.BeneficiaryGrant18Factory()
        stock = offers_factories.StockWithActivationCodesFactory(
            activationCodes=["code-vgya451afvyux"], offer__url="https://new.example.com?token={token}"
        )

        # When
        data = {"stockId": humanize(stock.id), "quantity": 1}
        client = TestClient(app.test_client()).with_session_auth(user.email)
        response = client.post("/bookings", json=data)

        # Then
        assert response.status_code == 201
        booking = bookings_models.Booking.query.one()
        assert response.json == {
            "amount": 10.0,
            "completedUrl": "https://new.example.com?token=code-vgya451afvyux",
            "id": humanize(booking.id),
            "isCancelled": False,
            "quantity": 1,
            "stock": {"price": 10.0},
            "stockId": humanize(stock.id),
            "token": booking.token,
            "activationCode": {"code": "code-vgya451afvyux", "expirationDate": None},
            "qrCode": booking.qrCode,
        }


@pytest.mark.usefixtures("db_session")
class Returns400Test:
    def when_use_case_raise_stock_is_not_bookable_exception(self, app):
        user = users_factories.BeneficiaryGrant18Factory()
        stock = offers_factories.StockFactory(quantity=0)

        data = {"stockId": humanize(stock.id), "quantity": 1}
        client = TestClient(app.test_client()).with_session_auth(user.email)
        response = client.post("/bookings", json=data)

        assert response.status_code == 400
        assert response.json["stock"] == ["Ce stock n'est pas réservable"]

        assert bookings_models.Booking.query.first() is None

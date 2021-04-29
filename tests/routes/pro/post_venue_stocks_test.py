from decimal import Decimal
from unittest.mock import patch

import pytest

import pcapi.core.offers.factories as offers_factories

from tests.conftest import TestClient


pytestmark = pytest.mark.usefixtures("db_session")


class Post:
    @patch("pcapi.core.providers.api.synchronize_stocks")
    def test_accepts_request(self, mock_synchronize_stocks, app):
        offerer = offers_factories.OffererFactory(siren=123456789)
        venue = offers_factories.VenueFactory(managingOfferer=offerer, id=3)
        api_key = offers_factories.ApiKeyFactory(offerer=offerer)

        mock_synchronize_stocks.return_value = {}

        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {api_key.value}"}

        response = test_client.post("/v2/venue/3/stocks", json={"stocks": [{"ref": "123456789", "available": 4}]})

        assert response.status_code == 204
        mock_synchronize_stocks.assert_called_once_with(
            [
                {
                    "products_provider_reference": "123456789",
                    "offers_provider_reference": "123456789@3",
                    "stocks_provider_reference": "123456789@3",
                    "available_quantity": 4,
                    "price": None,
                }
            ],
            venue,
        )

    @pytest.mark.parametrize(
        "price,expected_price",
        [(None, None), ("", None), ("0", None), (0, None), (1.23, Decimal("1.23")), ("1.23", Decimal("1.23"))],
    )
    @patch("pcapi.core.providers.api.synchronize_stocks")
    def test_accepts_request_with_price(self, mock_synchronize_stocks, price, expected_price, app):
        offerer = offers_factories.OffererFactory(siren=123456789)
        venue = offers_factories.VenueFactory(managingOfferer=offerer, id=3)
        api_key = offers_factories.ApiKeyFactory(offerer=offerer)

        mock_synchronize_stocks.return_value = {}

        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {api_key.value}"}

        response = test_client.post(
            "/v2/venue/3/stocks", json={"stocks": [{"ref": "123456789", "available": 4, "price": price}]}
        )

        assert response.status_code == 204
        mock_synchronize_stocks.assert_called_once_with(
            [
                {
                    "products_provider_reference": "123456789",
                    "offers_provider_reference": "123456789@3",
                    "stocks_provider_reference": "123456789@3",
                    "available_quantity": 4,
                    "price": expected_price,
                }
            ],
            venue,
        )

    @patch("pcapi.core.providers.api.synchronize_stocks")
    def test_requires_an_api_key(self, mock_synchronize_stocks, app):
        offerer = offers_factories.OffererFactory(siren=123456789)
        offers_factories.VenueFactory(managingOfferer=offerer, id=3)

        mock_synchronize_stocks.return_value = {}

        test_client = TestClient(app.test_client())

        response = test_client.post("/v2/venue/3/stocks", json={"stocks": [{"ref": "123456789", "available": 4}]})

        assert response.status_code == 401
        mock_synchronize_stocks.assert_not_called()

    @patch("pcapi.core.providers.api.synchronize_stocks")
    def test_returns_404_if_api_key_cant_access_venue(self, mock_synchronize_stocks, app):
        offerer = offers_factories.OffererFactory(siren=123456789)
        offers_factories.VenueFactory(managingOfferer=offerer, id=3)

        offerer2 = offers_factories.OffererFactory(siren=123456780)
        api_key = offers_factories.ApiKeyFactory(offerer=offerer2)

        mock_synchronize_stocks.return_value = {}

        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {api_key.value}"}

        response1 = test_client.post("/v2/venue/3/stocks", json={"stocks": [{"ref": "123456789", "available": 4}]})
        response2 = test_client.post("/v2/venue/123/stocks", json={"stocks": [{"ref": "123456789", "available": 4}]})

        assert response1.status_code == 404
        assert response2.status_code == 404
        mock_synchronize_stocks.assert_not_called()

    @patch("pcapi.core.providers.api.synchronize_stocks")
    def test_returns_comprehensive_errors(self, mock_synchronize_stocks, app):
        api_key = offers_factories.ApiKeyFactory()

        mock_synchronize_stocks.return_value = {}

        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {api_key.value}"}

        response1 = test_client.post("/v2/venue/3/stocks", json={})
        response2 = test_client.post(
            "/v2/venue/3/stocks", json={"stocks": [{"ref": "123456789"}, {"wrong_key": "123456789"}]}
        )

        assert response1.status_code == 400
        assert response1.json["stocks"] == ["Ce champ est obligatoire"]
        assert response2.status_code == 400
        assert response2.json["stocks.0.available"] == ["Ce champ est obligatoire"]
        assert response2.json["stocks.1.available"] == ["Ce champ est obligatoire"]
        assert response2.json["stocks.1.ref"] == ["Ce champ est obligatoire"]
        mock_synchronize_stocks.assert_not_called()

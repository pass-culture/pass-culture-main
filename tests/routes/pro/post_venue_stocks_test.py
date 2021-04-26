from unittest.mock import patch

import pcapi.core.offers.factories as offers_factories

from tests.conftest import TestClient
from tests.conftest import clean_database


class Post:
    @clean_database
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
                }
            ],
            venue,
        )

    @clean_database
    @patch("pcapi.core.providers.api.synchronize_stocks")
    def test_requires_an_api_key(self, mock_synchronize_stocks, app):
        offerer = offers_factories.OffererFactory(siren=123456789)
        offers_factories.VenueFactory(managingOfferer=offerer, id=3)

        mock_synchronize_stocks.return_value = {}

        test_client = TestClient(app.test_client())

        response = test_client.post("/v2/venue/3/stocks", json={"stocks": [{"ref": "123456789", "available": 4}]})

        assert response.status_code == 401
        mock_synchronize_stocks.assert_not_called()

    @clean_database
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

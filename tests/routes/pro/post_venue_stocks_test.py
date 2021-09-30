from decimal import Decimal
from unittest.mock import patch

import pytest

from pcapi.core.offerers.factories import ApiKeyFactory
from pcapi.core.offerers.factories import DEFAULT_CLEAR_API_KEY
from pcapi.core.offerers.factories import ProviderFactory
import pcapi.core.offers.factories as offers_factories

from tests.conftest import TestClient


pytestmark = pytest.mark.usefixtures("db_session")


@patch("pcapi.core.providers.api.synchronize_stocks")
def test_accepts_request(mock_synchronize_stocks, app):
    api_stocks_provider = ProviderFactory(name="Pass Culture API Stocks", localClass="PCAPIStocks")
    offerer = offers_factories.OffererFactory(siren=123456789)
    venue = offers_factories.VenueFactory(managingOfferer=offerer, id=3)
    ApiKeyFactory(offerer=offerer)

    mock_synchronize_stocks.return_value = {}

    test_client = TestClient(app.test_client())
    test_client.auth_header = {"Authorization": f"Bearer {DEFAULT_CLEAR_API_KEY}"}

    response = test_client.post(
        "/v2/venue/3/stocks",
        json={"stocks": [{"ref": "123456789", "available": 4}, {"ref": "1234567890", "available": 0}]},
    )

    assert response.status_code == 204
    mock_synchronize_stocks.assert_called_once_with(
        [
            {
                "products_provider_reference": "123456789",
                "offers_provider_reference": "123456789@3",
                "stocks_provider_reference": "123456789@3",
                "available_quantity": 4,
                "price": None,
            },
            {
                "products_provider_reference": "1234567890",
                "offers_provider_reference": "1234567890@3",
                "stocks_provider_reference": "1234567890@3",
                "available_quantity": 0,
                "price": None,
            },
        ],
        venue,
        provider_id=api_stocks_provider.id,
    )


@pytest.mark.parametrize(
    "price,expected_price",
    [(None, None), ("", None), ("0", None), (0, None), (1.23, Decimal("1.23")), ("1.23", Decimal("1.23"))],
)
@patch("pcapi.core.providers.api.synchronize_stocks")
def test_accepts_request_with_price(mock_synchronize_stocks, price, expected_price, app):
    api_stocks_provider = ProviderFactory(name="Pass Culture API Stocks", localClass="PCAPIStocks")
    offerer = offers_factories.OffererFactory(siren=123456789)
    venue = offers_factories.VenueFactory(managingOfferer=offerer, id=3)
    ApiKeyFactory(offerer=offerer)

    mock_synchronize_stocks.return_value = {}

    test_client = TestClient(app.test_client())
    test_client.auth_header = {"Authorization": f"Bearer {DEFAULT_CLEAR_API_KEY}"}

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
        provider_id=api_stocks_provider.id,
    )


@patch("pcapi.core.providers.api.synchronize_stocks")
def test_requires_an_api_key(mock_synchronize_stocks, app):
    offerer = offers_factories.OffererFactory(siren=123456789)
    offers_factories.VenueFactory(managingOfferer=offerer, id=3)

    mock_synchronize_stocks.return_value = {}

    test_client = TestClient(app.test_client())

    response = test_client.post("/v2/venue/3/stocks", json={"stocks": [{"ref": "123456789", "available": 4}]})

    assert response.status_code == 401
    mock_synchronize_stocks.assert_not_called()


@patch("pcapi.core.providers.api.synchronize_stocks")
def test_returns_404_if_api_key_cant_access_venue(mock_synchronize_stocks, app):
    offerer = offers_factories.OffererFactory(siren=123456789)
    offers_factories.VenueFactory(managingOfferer=offerer, id=3)

    offerer2 = offers_factories.OffererFactory(siren=123456780)
    ApiKeyFactory(offerer=offerer2)

    mock_synchronize_stocks.return_value = {}

    test_client = TestClient(app.test_client())
    test_client.auth_header = {"Authorization": f"Bearer {DEFAULT_CLEAR_API_KEY}"}

    response1 = test_client.post("/v2/venue/3/stocks", json={"stocks": [{"ref": "123456789", "available": 4}]})
    response2 = test_client.post("/v2/venue/123/stocks", json={"stocks": [{"ref": "123456789", "available": 4}]})

    assert response1.status_code == 404
    assert response2.status_code == 404
    mock_synchronize_stocks.assert_not_called()


@patch("pcapi.core.providers.api.synchronize_stocks")
def test_returns_comprehensive_errors(mock_synchronize_stocks, app):
    ApiKeyFactory()

    mock_synchronize_stocks.return_value = {}

    test_client = TestClient(app.test_client())
    test_client.auth_header = {"Authorization": f"Bearer {DEFAULT_CLEAR_API_KEY}"}

    response1 = test_client.post("/v2/venue/3/stocks", json={})
    response2 = test_client.post(
        "/v2/venue/3/stocks",
        json={
            "stocks": [
                {"ref": "123456789"},
                {"wrong_key": "123456789"},
                {"ref": "1234567890", "available": "abc"},
                {"ref": "12345678901", "available": -3},
            ]
        },
    )

    assert response1.status_code == 400
    assert response1.json["stocks"] == ["Ce champ est obligatoire"]
    assert response2.status_code == 400
    assert response2.json["stocks.0.available"] == ["Ce champ est obligatoire"]
    assert response2.json["stocks.1.available"] == ["Ce champ est obligatoire"]
    assert response2.json["stocks.1.ref"] == ["Ce champ est obligatoire"]
    assert response2.json["stocks.2.available"] == ["Saisissez un nombre valide"]
    assert response2.json["stocks.3.available"] == ["Saisissez un nombre supérieur ou égal à 0"]
    mock_synchronize_stocks.assert_not_called()

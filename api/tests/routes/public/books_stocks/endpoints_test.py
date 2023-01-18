import decimal
from unittest.mock import patch

import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.offers.models as offers_models
from pcapi.core.testing import override_features


pytestmark = pytest.mark.usefixtures("db_session")

NOT_SENT = object()


@pytest.mark.parametrize("require_price_flag", [False, True])
def test_basics(require_price_flag, client):
    venue = offerers_factories.VenueFactory()
    isbn = "123456789"
    offer = offers_factories.OfferFactory(
        product__idAtProviders=isbn,
        product__extraData={"prix_livre": 12.34},
        product__subcategoryId="LIVRE_PAPIER",
        idAtProvider=isbn,
        venue=venue,
    )
    offerers_factories.ApiKeyFactory(offerer=venue.managingOfferer)

    data = {
        "stocks": [
            {"ref": isbn, "available": 4, "price": 30},
            {"ref": "unknown", "available": 0, "price": 10},
        ]
    }
    client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)
    with override_features(WIP_REQUIRE_PRICE_IN_STOCK_API=require_price_flag):
        response = client.post(f"/v2/venue/{venue.id}/stocks", json=data)

    assert response.status_code == 204
    assert offers_models.Offer.query.count() == 1
    assert len(offer.stocks) == 1
    assert offer.stocks[0].quantity == 4
    assert offer.stocks[0].price == 30


@override_features(WIP_REQUIRE_PRICE_IN_STOCK_API=False)
@pytest.mark.parametrize("price", [None, "", 0, "0"])
def test_default_to_product_price_if_no_price_is_given(price, client):
    venue = offerers_factories.VenueFactory()
    isbn = "123456789"
    product_price = decimal.Decimal("12.34")
    offer = offers_factories.OfferFactory(
        product__idAtProviders=isbn,
        product__subcategoryId="LIVRE_PAPIER",
        idAtProvider=isbn,
        product__extraData={"prix_livre": product_price},
        venue=venue,
    )
    offerers_factories.ApiKeyFactory(offerer=venue.managingOfferer)

    data = {"stocks": [{"ref": isbn, "available": 4, "price": price}]}
    client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)
    response = client.post(f"/v2/venue/{venue.id}/stocks", json=data)

    assert response.status_code == 204
    assert offer.stocks[0].price == product_price
    assert offer.stocks[0].quantity == 4


@override_features(WIP_REQUIRE_PRICE_IN_STOCK_API=True)
@pytest.mark.parametrize("price", [NOT_SENT, None, "", 0, "0"])
def test_require_price(price, client):
    venue = offerers_factories.VenueFactory()
    isbn = "123456789"
    product_price = decimal.Decimal("12.34")
    offers_factories.OfferFactory(
        product__idAtProviders=isbn,
        product__subcategoryId="LIVRE_PAPIER",
        idAtProvider=isbn,
        product__extraData={"prix_livre": product_price},
        venue=venue,
    )
    offerers_factories.ApiKeyFactory(offerer=venue.managingOfferer)

    data = {"stocks": [{"ref": isbn, "available": 4, "price": price}]}
    if price == NOT_SENT:
        del data["stocks"][0]["price"]
    client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)
    response = client.post(f"/v2/venue/{venue.id}/stocks", json=data)

    assert response.status_code == 400
    error = "Le prix est obligatoire depuis le 10/12/2022"
    assert response.json["stocks.0.__root__"][0] == error


@patch("pcapi.core.providers.api.synchronize_stocks")
def test_require_an_api_key(mock_synchronize_stocks, client):
    venue = offerers_factories.VenueFactory()

    data = {"stocks": [{"ref": "x", "available": 4, "price": 12.34}]}
    response = client.post(f"/v2/venue/{venue.id}/stocks", json=data)

    assert response.status_code == 401
    mock_synchronize_stocks.assert_not_called()


@patch("pcapi.core.providers.api.synchronize_stocks")
def test_return_404_if_api_key_cant_access_venue(mock_synchronize_stocks, client):
    offerers_factories.ApiKeyFactory()
    other_venue = offerers_factories.VenueFactory()

    client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)

    data = {"stocks": [{"ref": "x", "available": 4, "price": 12.34}]}
    response = client.post(f"/v2/venue/{other_venue.id}/stocks", json=data)  # no access
    assert response.status_code == 404

    response = client.post("/v2/venue/0/stocks", json=data)  # unknown venue
    assert response.status_code == 404

    mock_synchronize_stocks.assert_not_called()


@override_features(WIP_REQUIRE_PRICE_IN_STOCK_API=False)
@patch("pcapi.core.providers.api.synchronize_stocks")
def test_return_comprehensive_errors_legacy(mock_synchronize_stocks, client):
    offerers_factories.ApiKeyFactory()

    client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)
    response1 = client.post("/v2/venue/3/stocks", json={})
    assert response1.status_code == 400
    assert response1.json["stocks"] == ["Ce champ est obligatoire"]

    response2 = client.post(
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
    assert response2.status_code == 400
    assert response2.json["stocks.0.available"] == ["Ce champ est obligatoire"]
    assert response2.json["stocks.1.available"] == ["Ce champ est obligatoire"]
    assert response2.json["stocks.1.ref"] == ["Ce champ est obligatoire"]
    assert response2.json["stocks.2.available"] == ["Saisissez un nombre valide"]
    assert response2.json["stocks.3.available"] == ["Saisissez un nombre supérieur ou égal à 0"]

    mock_synchronize_stocks.assert_not_called()


@override_features(WIP_REQUIRE_PRICE_IN_STOCK_API=True)
@patch("pcapi.core.providers.api.synchronize_stocks")
def test_return_comprehensive_errors(mock_synchronize_stocks, client):
    offerers_factories.ApiKeyFactory()

    client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)
    response1 = client.post("/v2/venue/3/stocks", json={})
    assert response1.status_code == 400
    assert response1.json == {"stocks": ["Ce champ est obligatoire"]}

    response2 = client.post(
        "/v2/venue/3/stocks",
        json={
            "stocks": [
                {"ref": "123456789", "price": "12.34", "available": 1},  # no error
                {},
                {"ref": "1234567890", "price": "12.34", "available": "abc"},
                {"ref": "12345678901", "price": "12.34", "available": -3},
            ]
        },
    )
    assert response2.status_code == 400
    assert response2.json == {
        "stocks.1.available": ["Ce champ est obligatoire"],
        "stocks.1.__root__": ["Le prix est obligatoire depuis le 10/12/2022"],
        "stocks.1.ref": ["Ce champ est obligatoire"],
        "stocks.2.available": ["Saisissez un nombre valide"],
        "stocks.3.available": ["Saisissez un nombre supérieur ou égal à 0"],
    }

    mock_synchronize_stocks.assert_not_called()

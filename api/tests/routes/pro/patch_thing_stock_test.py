import datetime
from unittest.mock import patch

import pytest

import pcapi.core.mails.testing as mails_testing
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.providers.factories as providers_factories
from pcapi.core import search
from pcapi.core.offers import models as offers_models
from pcapi.models import db
from pcapi.utils.date import format_into_utc_date


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    @patch("pcapi.core.search.async_index_offer_ids")
    @pytest.mark.parametrize(
        "input_json,expected_log_extra_changes",
        [
            (
                {
                    "price": 20,
                    "bookingLimitDatetime": format_into_utc_date(
                        datetime.datetime.utcnow() + datetime.timedelta(days=1)
                    ),
                    "quantity": 10,
                },
                {"price", "quantity", "bookingLimitDatetime"},
            ),
            ({"price": 0, "quantity": None}, {"price", "quantity"}),
        ],
    )
    def test_update_one_product_stock(
        self, mocked_async_index_offer_ids, input_json: dict, expected_log_extra_changes: dict, client
    ):
        email = "user@example.com"
        stock = offers_factories.ThingStockFactory()
        offerers_factories.UserOffererFactory(user__email=email, offerer=stock.offer.venue.managingOfferer)

        response = client.with_session_auth(email).patch(f"/stocks/{stock.id}", json=input_json)

        assert response.status_code == 200
        assert response.json["id"] == stock.id

        assert stock.price == input_json.get("price")
        if input_json.get("bookingLimitDatetime"):
            assert format_into_utc_date(stock.bookingLimitDatetime) == input_json.get("bookingLimitDatetime")
        assert stock.quantity == input_json.get("quantity")
        assert db.session.query(offers_models.PriceCategory).count() == 0
        assert db.session.query(offers_models.PriceCategoryLabel).count() == 0
        assert len(mails_testing.outbox) == 0  # Mail sent during fraud validation
        mocked_async_index_offer_ids.assert_called_once_with(
            [stock.offer.id],
            reason=search.IndexationReason.STOCK_UPDATE,
            log_extra={"changes": expected_log_extra_changes},
        )

    def test_should_be_able_to_update_synchronized_stock_quantity(self, client):
        public_api_provider = providers_factories.PublicApiProviderFactory()
        stock = offers_factories.ThingStockFactory(offer__lastProvider=public_api_provider)
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=stock.offer.venue.managingOfferer)
        response = client.with_session_auth("user@example.com").patch(f"/stocks/{stock.id}", json={"quantity": 3456})

        assert response.status_code == 200
        assert stock.quantity == 3456


@pytest.mark.usefixtures("db_session")
class Returns400Test:
    @pytest.mark.parametrize(
        "input_json,error_json",
        [
            ({"price": "coucou"}, {"price": ["Saisissez un nombre valide"]}),
            ({"price": 12, "bookingLimitDatetime": ""}, {"bookingLimitDatetime": ["Format de date invalide"]}),
            ({"price": float("NaN")}, {"price": ["La valeur n'est pas un nombre décimal valide"]}),
            ({"price": 20, "quantity": 10**10}, {"quantity": ["ensure this value is less than or equal to 1000000"]}),
        ],
    )
    def test_should_raise_because_of_invalid_data(self, input_json, error_json, client):
        offerers_factories.UserOffererFactory(user__email="user@example.com")
        response = client.with_session_auth("user@example.com").patch("/stocks/43", json=input_json)

        assert response.status_code == 400
        assert response.json == error_json

    @pytest.mark.parametrize(
        "input_json",
        [
            {"price": 20},
            {"bookingLimitDatetime": format_into_utc_date(datetime.datetime.utcnow() + datetime.timedelta(days=1))},
        ],
    )
    def test_should_raise_because_you_cannot_update_stock_attribute_except_quantity_for_synchronized_offers(
        self, input_json, client
    ):
        public_api_provider = providers_factories.PublicApiProviderFactory()
        stock = offers_factories.ThingStockFactory(offer__lastProvider=public_api_provider)
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=stock.offer.venue.managingOfferer)
        response = client.with_session_auth("user@example.com").patch(f"/stocks/{stock.id}", json=input_json)

        assert response.status_code == 400
        assert response.json == {"global": ["Les offres importées ne sont pas modifiables"]}


@pytest.mark.usefixtures("db_session")
class Returns403Test:
    def test_should_raise(self, client):
        stock = offers_factories.ThingStockFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com")
        response = client.with_session_auth("user@example.com").patch(f"/stocks/{stock.id}", json={"price": 12})

        assert response.status_code == 403
        assert response.json == {
            "global": ["Vous n'avez pas les droits d'accès suffisants pour accéder à cette information."]
        }


@pytest.mark.usefixtures("db_session")
class Returns404Test:
    def test_should_raise(self, client):
        offerers_factories.UserOffererFactory(user__email="user@example.com")
        response = client.with_session_auth("user@example.com").patch("/stocks/42", json={"price": 12})

        assert response.status_code == 404
        assert response.json == {}

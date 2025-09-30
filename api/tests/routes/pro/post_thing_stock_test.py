import datetime
from unittest.mock import patch

import pytest

import pcapi.core.mails.testing as mails_testing
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core import search
from pcapi.core.offers import models as offers_models
from pcapi.models import db
from pcapi.utils.date import format_into_utc_date


@pytest.mark.usefixtures("db_session")
class Returns201Test:
    @patch("pcapi.core.search.async_index_offer_ids")
    @pytest.mark.parametrize(
        "input_json",
        [
            {
                "price": 20,
                "bookingLimitDatetime": format_into_utc_date(datetime.datetime.utcnow() + datetime.timedelta(days=1)),
                "quantity": 10,
            },
            {"price": 0},
        ],
    )
    def test_create_one_thing_stock(self, mocked_async_index_offer_ids, input_json: dict, client):
        email = "user@example.com"
        offer = offers_factories.ThingOfferFactory(isActive=False, validation=offers_models.OfferValidationStatus.DRAFT)
        offerers_factories.UserOffererFactory(user__email=email, offerer=offer.venue.managingOfferer)
        input_json["offerId"] = offer.id

        response = client.with_session_auth(email).post("/stocks", json=input_json)
        created_stock = db.session.query(offers_models.Stock).first()
        assert response.status_code == 201
        assert response.json["id"] == created_stock.id

        assert offer.id == created_stock.offerId
        assert created_stock.price == input_json.get("price")
        if created_stock.bookingLimitDatetime:
            assert format_into_utc_date(created_stock.bookingLimitDatetime) == input_json.get("bookingLimitDatetime")
        assert created_stock.quantity == input_json.get("quantity")
        assert offer.isActive is False
        assert db.session.query(offers_models.PriceCategory).count() == 0
        assert db.session.query(offers_models.PriceCategoryLabel).count() == 0
        assert offer.validation == offers_models.OfferValidationStatus.DRAFT
        assert len(mails_testing.outbox) == 0  # Mail sent during fraud validation
        mocked_async_index_offer_ids.assert_called_once_with([offer.id], reason=search.IndexationReason.STOCK_CREATION)

    def test_create_one_stock_with_activation_codes(self, client):
        offer = offers_factories.DigitalOfferFactory(url="https://chartreu.se")
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        activation_codes = ["AZ3", "3ZE"]
        limit_datetime = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        expiration_datetime = datetime.datetime.utcnow() + datetime.timedelta(days=14)
        stock_data = {
            "offerId": offer.id,
            "price": 20,
            "quantity": 30,
            "activationCodes": activation_codes,
            "bookingLimitDatetime": format_into_utc_date(limit_datetime),
            "activationCodesExpirationDatetime": format_into_utc_date(expiration_datetime),
        }

        response = client.with_session_auth("user@example.com").post("/stocks", json=stock_data)

        created_stock: offers_models.Stock = db.session.query(offers_models.Stock).first()
        assert response.status_code == 201
        assert response.json["id"] == created_stock.id

        assert offer.id == created_stock.offerId
        assert created_stock.price == 20
        assert created_stock.bookingLimitDatetime == limit_datetime
        assert created_stock.quantity == len(activation_codes)
        assert [activation_code.code for activation_code in created_stock.activationCodes] == activation_codes
        for activation_code in created_stock.activationCodes:
            assert activation_code.expirationDate == expiration_datetime


@pytest.mark.usefixtures("db_session")
class Returns400Test:
    @pytest.mark.parametrize(
        "is_caledonian,input_json,error_json",
        [
            (False, {}, {"offerId": ["Ce champ est obligatoire"], "price": ["Ce champ est obligatoire"]}),
            (False, {"offerId": 43, "price": "coucou"}, {"price": ["Saisissez un nombre valide"]}),
            (
                False,
                {"offerId": 43, "price": 12, "bookingLimitDatetime": "", "activationCodesExpirationDatetime": ""},
                {
                    "activationCodesExpirationDatetime": ["Format de date invalide"],
                    "bookingLimitDatetime": ["Format de date invalide"],
                },
            ),
            (
                False,
                {"offerId": 43, "price": float("NaN")},
                {"price": ["La valeur n'est pas un nombre décimal valide"]},
            ),
            (
                False,
                {"offerId": 43, "price": 20, "quantity": 1234567890987654},
                {"quantity": ["ensure this value is less than or equal to 1000000"]},
            ),
            (True, {"price": 23866}, {"price23865": ["Le prix d’une offre ne peut excéder 23865 francs Pacifique."]}),
        ],
    )
    def test_should_raise_because_of_invalid_data(self, is_caledonian, input_json, error_json, client):
        if is_caledonian:
            venue = offerers_factories.CaledonianVenueFactory()
            offer = offers_factories.ThingOfferFactory.create(
                isActive=False,
                name="Offre calédonienne THING",
                venue=venue,
                validation=offers_models.OfferValidationStatus.DRAFT,
            )
            offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)
            input_json["offerId"] = offer.id
        else:
            offerers_factories.UserOffererFactory(user__email="user@example.com")

        response = client.with_session_auth("user@example.com").post("/stocks", json=input_json)

        assert response.status_code == 400
        assert response.json == error_json


@pytest.mark.usefixtures("db_session")
class Returns403Test:
    def test_should_raise(self, client):
        offer = offers_factories.ThingOfferFactory(isActive=False, validation=offers_models.OfferValidationStatus.DRAFT)
        offerers_factories.UserOffererFactory(user__email="user@example.com")
        response = client.with_session_auth("user@example.com").post("/stocks", json={"offerId": offer.id, "price": 12})

        assert response.status_code == 403
        assert response.json == {
            "global": ["Vous n'avez pas les droits d'accès suffisants pour accéder à cette information."]
        }


@pytest.mark.usefixtures("db_session")
class Returns404Test:
    def test_should_raise(self, client):
        offerers_factories.UserOffererFactory(user__email="user@example.com")
        response = client.with_session_auth("user@example.com").post("/stocks", json={"offerId": 12, "price": 12})

        assert response.status_code == 404
        assert response.json == {}

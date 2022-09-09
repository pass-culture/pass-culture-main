from datetime import datetime
from unittest.mock import patch

import pytest

import pcapi.core.mails.testing as mails_testing
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.models import OfferValidationStatus
from pcapi.core.offers.models import Stock
import pcapi.core.users.factories as users_factories
from pcapi.routes.serialization import serialize
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


@pytest.mark.usefixtures("db_session")
class Returns201Test:
    @patch("pcapi.core.search.async_index_offer_ids")
    def test_create_one_stock(self, mocked_async_index_offer_ids, app):
        # Given
        offer = offers_factories.ThingOfferFactory(isActive=False, validation=OfferValidationStatus.DRAFT)
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        stock_data = {
            "offerId": humanize(offer.id),
            "stocks": [{"price": 20}],
        }

        response = (
            TestClient(app.test_client()).with_session_auth("user@example.com").post("/stocks/bulk/", json=stock_data)
        )
        assert response.status_code == 201

        response_dict = response.json
        assert len(response_dict["stockIds"]) == len(stock_data["stocks"])

        created_stock = Stock.query.get(dehumanize(response_dict["stockIds"][0]["id"]))
        assert offer.id == created_stock.offerId
        assert created_stock.price == 20
        assert offer.isActive == False
        assert offer.validation == OfferValidationStatus.DRAFT
        assert len(mails_testing.outbox) == 0  # Mail sent during fraud validation
        mocked_async_index_offer_ids.assert_not_called()

    @patch("pcapi.core.search.async_index_offer_ids")
    def test_edit_one_stock(self, mocked_async_index_offer_ids, client):
        offer = offers_factories.ThingOfferFactory(isActive=False, validation=OfferValidationStatus.DRAFT)
        existing_stock = offers_factories.StockFactory(offer=offer, price=10)
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        stock_data = {
            "offerId": humanize(offer.id),
            "stocks": [{"id": humanize(existing_stock.id), "price": 20}],
        }
        response = client.with_session_auth("user@example.com").post("/stocks/bulk/", json=stock_data)
        created_stock = Stock.query.get(dehumanize(response.json["stockIds"][0]["id"]))
        assert offer.id == created_stock.offerId
        assert created_stock.price == 20
        assert len(Stock.query.all()) == 1
        mocked_async_index_offer_ids.assert_called_once_with([offer.id])

    def test_create_one_stock_with_activation_codes(self, app):
        # Given
        offer = offers_factories.ThingOfferFactory(url="https://chartreu.se")
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )
        activation_codes = ["AZ3", "3ZE"]

        # When
        stock_data = {
            "offerId": humanize(offer.id),
            "stocks": [
                {
                    "price": 20,
                    "quantity": 30,
                    "activationCodes": activation_codes,
                    "bookingLimitDatetime": "2021-06-15T23:59:59Z",
                    "activationCodesExpirationDatetime": "2021-06-22T23:59:59Z",
                }
            ],
        }

        response = (
            TestClient(app.test_client()).with_session_auth("user@example.com").post("/stocks/bulk/", json=stock_data)
        )

        # Then
        assert response.status_code == 201

        response_dict = response.json
        assert len(response_dict["stockIds"]) == len(stock_data["stocks"])

        created_stock: Stock = Stock.query.get(dehumanize(response_dict["stockIds"][0]["id"]))
        assert offer.id == created_stock.offerId
        assert created_stock.price == 20
        assert created_stock.quantity == 2  # Same as the activation codes length
        assert [activation_code.code for activation_code in created_stock.activationCodes] == activation_codes
        for activation_code in created_stock.activationCodes:
            assert activation_code.expirationDate == datetime(2021, 6, 22, 23, 59, 59)

    def test_upsert_multiple_stocks(self, app):
        # Given
        offer = offers_factories.ThingOfferFactory()
        existing_stock = offers_factories.StockFactory(offer=offer, price=10)
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )
        booking_limit_datetime = datetime(2019, 2, 14)

        # When
        stock_data = {
            "offerId": humanize(offer.id),
            "stocks": [
                {
                    "id": humanize(existing_stock.id),
                    "price": 20,
                    "quantity": None,
                    "bookingLimitDatetime": serialize(booking_limit_datetime),
                },
                {
                    "price": 30,
                    "quantity": None,
                    "bookingLimitDatetime": serialize(booking_limit_datetime),
                },
                {
                    "price": 40,
                    "quantity": None,
                    "bookingLimitDatetime": serialize(booking_limit_datetime),
                },
            ],
        }
        response = (
            TestClient(app.test_client()).with_session_auth("user@example.com").post("/stocks/bulk/", json=stock_data)
        )

        # Then
        assert response.status_code == 201

        response_dict = response.json
        assert len(response_dict["stockIds"]) == len(stock_data["stocks"])

        for idx, result_stock_id in enumerate(response_dict["stockIds"]):
            expected_stock = stock_data["stocks"][idx]
            result_stock = Stock.query.get(dehumanize(result_stock_id["id"]))
            assert result_stock.price == expected_stock["price"]
            assert result_stock.quantity == expected_stock["quantity"]
            assert result_stock.bookingLimitDatetime == booking_limit_datetime


@pytest.mark.usefixtures("db_session")
class Returns400Test:
    def when_missing_offer_id(self, app):
        # Given
        offer = offers_factories.ThingOfferFactory()
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )
        booking_limit_datetime = datetime(2019, 2, 14)

        # When
        stock_data = {
            "stocks": [
                {
                    "quantity": -2,
                    "price": 0,
                    "bookingLimitDatetime": serialize(booking_limit_datetime),
                },
            ],
        }

        response = (
            TestClient(app.test_client()).with_session_auth("user@example.com").post("/stocks/bulk/", json=stock_data)
        )

        # Then
        assert response.status_code == 400
        assert response.json == {"offerId": ["Ce champ est obligatoire"]}

    def when_invalid_quantity_or_price_for_edition_and_creation(self, app):
        # Given
        offer = offers_factories.ThingOfferFactory()
        existing_stock = offers_factories.StockFactory(offer=offer, price=10)
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )
        booking_limit_datetime = datetime(2019, 2, 14)

        # When
        stock_data = {
            "offerId": humanize(offer.id),
            "stocks": [
                {
                    "id": humanize(existing_stock.id),
                    "price": -3,
                    "bookingLimitDatetime": serialize(booking_limit_datetime),
                },
                {
                    "quantity": -2,
                    "price": 0,
                    "bookingLimitDatetime": serialize(booking_limit_datetime),
                },
            ],
        }

        response = (
            TestClient(app.test_client()).with_session_auth("user@example.com").post("/stocks/bulk/", json=stock_data)
        )

        # Then
        assert response.status_code == 400
        assert response.json == {"price": ["Le prix doit être positif"]}

        persisted_stock = Stock.query.filter_by(offerId=offer.id)
        assert persisted_stock.count() == 1
        assert persisted_stock[0].price == 10

    def test_patch_non_approved_offer_fails(self, app):
        pending_validation_offer = offers_factories.OfferFactory(validation=OfferValidationStatus.PENDING)
        stock = offers_factories.StockFactory(offer=pending_validation_offer)
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=pending_validation_offer.venue.managingOfferer,
        )
        stock_data = {
            "offerId": humanize(pending_validation_offer.id),
            "stocks": [{"id": humanize(stock.id), "price": 20}],
        }

        response = (
            TestClient(app.test_client()).with_session_auth("user@example.com").post("/stocks/bulk/", json=stock_data)
        )

        assert response.status_code == 400
        assert response.json["global"] == ["Les offres refusées ou en attente de validation ne sont pas modifiables"]

    def test_invalid_activation_codes_expiration_datetime(self, app):
        # Given
        offer = offers_factories.ThingOfferFactory(url="https://chartreu.se")
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        stock_data = {
            "offerId": humanize(offer.id),
            "stocks": [
                {
                    "price": 20,
                    "activationCodes": ["AZ3"],
                    "bookingLimitDatetime": "2021-06-15T02:59:59Z",
                    "activationCodesExpirationDatetime": "2021-06-16T02:59:59Z",
                }
            ],
        }

        response = (
            TestClient(app.test_client()).with_session_auth("user@example.com").post("/stocks/bulk/", json=stock_data)
        )

        # Then
        assert response.status_code == 400
        assert response.json["activationCodesExpirationDatetime"] == [
            (
                "La date limite de validité des codes d'activation doit être ultérieure"
                " d'au moins 7 jours à la date limite de réservation"
            )
        ]

    def test_invalid_booking_limit_datetime(self, app):
        # Given
        offer = offers_factories.ThingOfferFactory(url="https://chartreu.se")
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )
        existing_stock = offers_factories.StockFactory(offer=offer)
        offers_factories.ActivationCodeFactory(expirationDate=datetime(2020, 5, 2, 23, 59, 59), stock=existing_stock)
        offers_factories.ActivationCodeFactory(expirationDate=datetime(2020, 5, 2, 23, 59, 59), stock=existing_stock)

        # When
        stock_data = {
            "offerId": humanize(offer.id),
            "stocks": [
                {
                    "id": humanize(existing_stock.id),
                    "bookingLimitDatetime": "2020-05-2T23:59:59Z",
                    "price": 20.0,
                }
            ],
        }

        response = (
            TestClient(app.test_client()).with_session_auth("user@example.com").post("/stocks/bulk/", json=stock_data)
        )

        # Then
        assert response.status_code == 400
        assert response.json["activationCodesExpirationDatetime"] == [
            (
                "La date limite de validité des codes d'activation doit être ultérieure"
                " d'au moins 7 jours à la date limite de réservation"
            )
        ]

    def test_when_offer_is_not_digital(self, app):
        # Given
        offer = offers_factories.ThingOfferFactory(url=None)
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        stock_data = {
            "offerId": humanize(offer.id),
            "stocks": [
                {
                    "price": 20,
                    "activationCodes": ["AZ3"],
                    "bookingLimitDatetime": "2021-06-15T02:59:59Z",
                    "activationCodesExpirationDatetime": "2021-07-15T02:59:59Z",
                }
            ],
        }

        response = (
            TestClient(app.test_client()).with_session_auth("user@example.com").post("/stocks/bulk/", json=stock_data)
        )

        # Then
        assert response.status_code == 400
        assert response.json["global"] == ["Impossible de créer des codes d'activation sur une offre non-numérique"]

    @pytest.mark.parametrize("price_str", [float("NaN"), float("inf"), float("-inf")])
    def test_create_one_stock_with_invalid_prices(self, price_str, app):
        # Given
        offer = offers_factories.ThingOfferFactory()
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        stock_data = {
            "offerId": humanize(offer.id),
            "stocks": [{"price": float(price_str)}],
        }

        response = (
            TestClient(app.test_client()).with_session_auth("user@example.com").post("/stocks/bulk/", json=stock_data)
        )

        # Then
        assert response.status_code == 400

        response_dict = response.json
        assert response_dict == {
            "stocks.0.id": ["Ce champ est obligatoire"],
            "stocks.0.price": [
                "La valeur n'est pas un nombre décimal valide",
                "La valeur n'est pas un nombre décimal valide",
            ],
        }

    @pytest.mark.parametrize("is_update", [False, True])
    def test_beginning_datetime_after_booking_limit_datetime(self, is_update, client):
        # Given
        offer = offers_factories.EventOfferFactory()
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        stock_data = {
            "offerId": humanize(offer.id),
            "stocks": [
                {
                    "beginningDatetime": "2022-06-11T08:00:00Z",
                    "bookingLimitDatetime": "2022-06-12T21:59:59Z",
                    "price": 15,
                    "quantity": 1000,
                },
            ],
        }

        if is_update:
            stock = offers_factories.StockFactory(offer=offer)
            stock_data["stocks"][0]["id"] = humanize(stock.id)

        # When
        response = client.with_session_auth("user@example.com").post("/stocks/bulk/", json=stock_data)

        # Then
        assert response.status_code == 400

        response_dict = response.json
        assert response_dict == {
            "stocks": ["La date limite de réservation ne peut être postérieure à la date de début de l'événement"],
        }


@pytest.mark.usefixtures("db_session")
class Returns403Test:
    def when_user_has_no_rights_and_creating_stock_from_offer_id(self, app, db_session):
        # Given
        user = users_factories.ProFactory(email="wrong@example.com")
        offer = offers_factories.ThingOfferFactory()
        offerers_factories.UserOffererFactory(user__email="right@example.com", offerer=offer.venue.managingOfferer)
        booking_datetime = datetime.utcnow()

        # When
        stock_data = {
            "offerId": humanize(offer.id),
            "stocks": [
                {
                    "quantity": 10,
                    "price": 0,
                    "bookingLimitDatetime": serialize(booking_datetime),
                },
            ],
        }
        response = TestClient(app.test_client()).with_session_auth(user.email).post("/stocks/bulk/", json=stock_data)

        # Then
        assert response.status_code == 403
        assert response.json == {
            "global": ["Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."]
        }

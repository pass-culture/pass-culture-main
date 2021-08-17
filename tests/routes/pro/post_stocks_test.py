from datetime import datetime

import pytest

import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.models import OfferValidationStatus
import pcapi.core.users.factories as users_factories
from pcapi.models import Stock
from pcapi.routes.serialization import serialize
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


@pytest.mark.usefixtures("db_session")
class Returns201Test:
    def test_create_one_stock(self, app):
        # Given
        offer = offers_factories.ThingOfferFactory()
        offers_factories.UserOffererFactory(
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

        # Then
        assert response.status_code == 201

        response_dict = response.json
        assert len(response_dict["stockIds"]) == len(stock_data["stocks"])

        created_stock = Stock.query.get(dehumanize(response_dict["stockIds"][0]["id"]))
        assert offer.id == created_stock.offerId
        assert created_stock.price == 20

    def test_create_one_stock_with_activation_codes(self, app):
        # Given
        offer = offers_factories.ThingOfferFactory(url="https://chartreu.se")
        offers_factories.UserOffererFactory(
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

    def test_edit_one_stock(self, app):
        # Given
        offer = offers_factories.ThingOfferFactory()
        existing_stock = offers_factories.StockFactory(offer=offer, price=10)
        offers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        stock_data = {
            "offerId": humanize(offer.id),
            "stocks": [{"id": humanize(existing_stock.id), "price": 20}],
        }
        response = (
            TestClient(app.test_client()).with_session_auth("user@example.com").post("/stocks/bulk/", json=stock_data)
        )

        # Then
        assert response.status_code == 201

        response_dict = response.json
        assert len(response_dict["stockIds"]) == len(stock_data["stocks"])

        edited_stock = Stock.query.get(dehumanize(response_dict["stockIds"][0]["id"]))
        assert edited_stock.price == 20

    def test_upsert_multiple_stocks(self, app):
        # Given
        offer = offers_factories.ThingOfferFactory()
        existing_stock = offers_factories.StockFactory(offer=offer, price=10)
        offers_factories.UserOffererFactory(
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
        offers_factories.UserOffererFactory(
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
        offers_factories.UserOffererFactory(
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
        offers_factories.UserOffererFactory(
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
        offers_factories.UserOffererFactory(
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
        offers_factories.UserOffererFactory(
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
        offers_factories.UserOffererFactory(
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


@pytest.mark.usefixtures("db_session")
class Returns403Test:
    def when_user_has_no_rights_and_creating_stock_from_offer_id(self, app, db_session):
        # Given
        user = users_factories.ProFactory(email="wrong@example.com")
        offer = offers_factories.ThingOfferFactory()
        offers_factories.UserOffererFactory(user__email="right@example.com", offerer=offer.venue.managingOfferer)
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

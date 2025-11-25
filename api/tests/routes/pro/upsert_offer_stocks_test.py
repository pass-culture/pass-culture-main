import datetime
import decimal

import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.offers.models as offers_models
import pcapi.core.users.factories as users_factories
from pcapi.models import db
from pcapi.utils import date as date_utils
from pcapi.utils.date import format_into_utc_date


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    def test_create_single_stock(self, client):
        offer = offers_factories.ThingOfferFactory()
        user = users_factories.UserFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offer.venue.managingOfferer)

        payload = {
            "stocks": [
                {
                    "id": None,
                    "offerId": offer.id,
                    "activationCodes": None,
                    "activationCodesExpirationDatetime": None,
                    "bookingLimitDatetime": None,
                    "price": 12.5,
                    "quantity": 5,
                }
            ]
        }
        response = client.with_session_auth(user.email).patch(f"/offers/{offer.id}/stocks/", json=payload)
        db.session.refresh(offer)

        assert response.status_code == 200
        assert len(offer.activeStocks) == 1
        created_stock = offer.activeStocks[0]
        assert created_stock.price == decimal.Decimal("12.5")
        assert created_stock.quantity == 5

    def test_update_and_delete_and_create(self, client):
        offer = offers_factories.ThingOfferFactory()
        user = users_factories.UserFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offer.venue.managingOfferer)
        stock_to_update = offers_factories.ThingStockFactory(offer=offer, price=decimal.Decimal("5"), quantity=10)
        stock_to_delete = offers_factories.ThingStockFactory(offer=offer, price=decimal.Decimal("7"), quantity=3)

        updated_stock_booking_limit_datetime = date_utils.get_naive_utc_now() + datetime.timedelta(days=2)
        payload = {
            "stocks": [
                {
                    "id": stock_to_update.id,
                    "offerId": offer.id,
                    "activationCodes": None,
                    "activationCodesExpirationDatetime": None,
                    "bookingLimitDatetime": format_into_utc_date(updated_stock_booking_limit_datetime),
                    "price": 9.99,
                    "quantity": 15,
                },
                {
                    "id": None,
                    "offerId": offer.id,
                    "activationCodes": None,
                    "activationCodesExpirationDatetime": None,
                    "bookingLimitDatetime": None,
                    "price": 3,
                    "quantity": None,
                },
            ]
        }
        response = client.with_session_auth(user.email).patch(f"/offers/{offer.id}/stocks/", json=payload)
        db.session.refresh(offer)

        assert response.status_code == 200
        updated_stock = db.session.get(offers_models.Stock, stock_to_update.id)
        deleted_stock = db.session.get(offers_models.Stock, stock_to_delete.id)
        assert deleted_stock.isSoftDeleted is True
        assert updated_stock.price == decimal.Decimal("9.99") and updated_stock.quantity == 15
        assert updated_stock.bookingLimitDatetime == updated_stock_booking_limit_datetime.replace(tzinfo=None)
        created_stocks = [s for s in offer.activeStocks if s.id not in (stock_to_update.id, stock_to_delete.id)]
        assert len(created_stocks) == 1
        assert created_stocks[0].quantity is None  # unlimited because quantity=None and no activation codes

    def test_create_with_activation_codes_sets_quantity(self, client):
        offer = offers_factories.DigitalOfferFactory()
        user = users_factories.UserFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offer.venue.managingOfferer)

        activation_codes = ["CODE1", "CODE2", "CODE3"]
        booking_limit_datetime = datetime.datetime.now() + datetime.timedelta(days=2)
        activation_codes_expiration_datetime = booking_limit_datetime + datetime.timedelta(days=7)
        payload = {
            "stocks": [
                {
                    "id": None,
                    "offerId": offer.id,
                    "activationCodes": activation_codes,
                    "activationCodesExpirationDatetime": activation_codes_expiration_datetime.isoformat(),
                    "bookingLimitDatetime": booking_limit_datetime.isoformat(),
                    "price": 0,
                    "quantity": None,  # server should set to len(activation_codes)
                }
            ]
        }
        response = client.with_session_auth(user.email).patch(f"/offers/{offer.id}/stocks/", json=payload)

        assert response.status_code == 200
        db.session.refresh(offer)
        assert len(offer.activeStocks) == 1
        created_stock = offer.activeStocks[0]
        assert created_stock.quantity == len(activation_codes)
        assert {ac.code for ac in created_stock.activationCodes} == set(activation_codes)


@pytest.mark.usefixtures("db_session")
class Returns400Test:
    def test_error_on_event_offer(self, client):
        offer = offers_factories.EventOfferFactory()
        user = users_factories.UserFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offer.venue.managingOfferer)

        payload = {"stocks": []}
        response = client.with_session_auth(user.email).patch(f"/offers/{offer.id}/stocks/", json=payload)

        assert response.status_code == 400
        assert response.json == {"global": "Offer is an event."}

    def test_error_trying_to_update_non_existing_stock(self, client):
        offer = offers_factories.ThingOfferFactory()
        user = users_factories.UserFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offer.venue.managingOfferer)

        payload = {
            "stocks": [
                {
                    "id": 999999,
                    "offerId": offer.id,
                    "activationCodes": None,
                    "activationCodesExpirationDatetime": None,
                    "bookingLimitDatetime": None,
                    "price": 1,
                    "quantity": 1,
                }
            ]
        }
        response = client.with_session_auth(user.email).patch(f"/offers/{offer.id}/stocks/", json=payload)

        assert response.status_code == 400
        assert response.json == {"global": "Trying to update a non-existing stock."}


@pytest.mark.usefixtures("db_session")
class Returns401Test:
    def test_not_authenticated(self, client):
        offer = offers_factories.ThingOfferFactory()

        payload = {"stocks": []}
        response = client.patch(f"/offers/{offer.id}/stocks/", json=payload)

        assert response.status_code == 401


@pytest.mark.usefixtures("db_session")
class Returns403Test:
    def test_user_without_rights(self, client):
        offer = offers_factories.ThingOfferFactory()
        unauthorized_pro = users_factories.ProFactory()
        offerers_factories.UserOffererFactory()

        payload = {"stocks": []}
        response = client.with_session_auth(unauthorized_pro.email).patch(f"/offers/{offer.id}/stocks/", json=payload)

        assert response.status_code == 403
        assert response.json == {
            "global": ["Vous n'avez pas les droits d'accès suffisants pour accéder à cette information."]
        }


@pytest.mark.usefixtures("db_session")
class Returns404Test:
    def test_offer_not_found(self, client):
        user = users_factories.UserFactory()
        offerers_factories.UserOffererFactory(user=user)

        payload = {"stocks": []}
        response = client.with_session_auth(user.email).patch("/offers/999999/stocks/", json=payload)

        assert response.status_code == 404
        assert response.json == {"global": "No offer found for this id"}

from datetime import datetime
from datetime import timedelta

import pytest

from pcapi.core import testing
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories


@pytest.mark.usefixtures("db_session")
class Returns403Test:
    def test_access_by_beneficiary(self, client):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        offer = offers_factories.OfferFactory()

        # When
        response = client.with_session_auth(beneficiary.email).get(f"/offers/{offer.id}/stocks")

        # Then
        assert response.status_code == 403

    def test_access_by_unauthorized_pro_user(self, client):
        # Given
        pro_user = users_factories.ProFactory()
        offer = offers_factories.ThingOfferFactory(
            venue__latitude=None, venue__longitude=None, venue__offererAddress=None
        )

        # When
        response = client.with_session_auth(pro_user.email).get(f"/offers/{offer.id}/stocks")

        # Then
        assert response.status_code == 403


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    def test_basic(self, client):
        # Given
        user_offerer = offerers_factories.UserOffererFactory()
        offer = offers_factories.ThingOfferFactory(venue__managingOfferer=user_offerer.offerer)

        # When
        response = client.with_session_auth(email=user_offerer.user.email).get(f"/offers/{offer.id}/stocks/")

        # Then
        assert response.status_code == 200

    def test_returns_an_event_stock(self, client):
        # Given
        now = datetime.utcnow()
        booking_datetime = now + timedelta(hours=1)
        booking_datetime_as_isoformat = booking_datetime.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        user_offerer = offerers_factories.UserOffererFactory()
        event_offer = offers_factories.EventOfferFactory(venue__managingOfferer=user_offerer.offerer)
        stock = offers_factories.EventStockFactory(
            dateCreated=now,
            dateModified=now,
            dateModifiedAtLastProvider=now,
            beginningDatetime=booking_datetime,
            bookingLimitDatetime=booking_datetime,
            offer=event_offer,
        )

        # When
        response = client.with_session_auth(email=user_offerer.user.email).get(f"/offers/{event_offer.id}/stocks")

        # Then
        assert response.status_code == 200
        assert response.json == {
            "stockCount": 1,
            "hasStocks": True,
            "stocks": [
                {
                    "activationCodesExpirationDatetime": None,
                    "beginningDatetime": booking_datetime_as_isoformat,
                    "bookingLimitDatetime": booking_datetime_as_isoformat,
                    "bookingsQuantity": 0,
                    "hasActivationCode": False,
                    "priceCategoryId": stock.priceCategoryId,
                    "id": stock.id,
                    "isEventDeletable": True,
                    "price": 10.1,
                    "quantity": 1000,
                    "remainingQuantity": 1000,
                }
            ],
        }

    def test_returns_a_thing_stock(self, client):
        # Given
        now = datetime.utcnow()
        user_offerer = offerers_factories.UserOffererFactory()
        thing_offer = offers_factories.ThingOfferFactory(venue__managingOfferer=user_offerer.offerer)
        stock = offers_factories.ThingStockFactory(
            dateCreated=now,
            dateModified=now,
            offer=thing_offer,
        )

        # When
        response = client.with_session_auth(email=user_offerer.user.email).get(f"/offers/{thing_offer.id}/stocks")

        # Then
        assert response.status_code == 200
        assert response.json == {
            "stockCount": 1,
            "hasStocks": True,
            "stocks": [
                {
                    "activationCodesExpirationDatetime": None,
                    "beginningDatetime": None,
                    "bookingLimitDatetime": None,
                    "bookingsQuantity": 0,
                    "hasActivationCode": False,
                    "id": stock.id,
                    "isEventDeletable": True,
                    "price": 10.1,
                    "priceCategoryId": None,
                    "quantity": 1000,
                    "remainingQuantity": 1000,
                },
            ],
        }

    def test_should_not_return_soft_deleted_stock(self, client):
        # Given
        user_offerer = offerers_factories.UserOffererFactory()
        offer = offers_factories.EventOfferFactory(venue__managingOfferer=user_offerer.offerer)
        deleted_stock = offers_factories.EventStockFactory(offer=offer, isSoftDeleted=True)

        # When
        response = client.with_session_auth(email=user_offerer.user.email).get(
            f"/offers/{deleted_stock.offer.id}/stocks"
        )

        # Then
        assert response.status_code == 200
        assert len(response.json["stocks"]) == 0

    def test_returns_false_if_no_stocks(self, client):
        # Given
        user_offerer = offerers_factories.UserOffererFactory()
        offer = offers_factories.EventOfferFactory(venue__managingOfferer=user_offerer.offerer)

        # When
        response = client.with_session_auth(email=user_offerer.user.email).get(f"/offers/{offer.id}/stocks")

        # Then
        assert response.status_code == 200
        assert response.json["hasStocks"] == False

    def test_returns_false_if_all_stocks_are_soft_deleted(self, client):
        # Given
        user_offerer = offerers_factories.UserOffererFactory()
        offer = offers_factories.EventOfferFactory(venue__managingOfferer=user_offerer.offerer)
        offers_factories.StockFactory.create_batch(3, offer=offer, isSoftDeleted=True)
        # When
        response = client.with_session_auth(email=user_offerer.user.email).get(f"/offers/{offer.id}/stocks")

        # Then
        assert response.status_code == 200
        assert response.json["hasStocks"] == False

    def test_returns_true_if_stock_exists_outside_filter(self, client):
        # Given
        date_1 = datetime.utcnow()
        date_2 = datetime.utcnow() + timedelta(days=1)
        user_offerer = offerers_factories.UserOffererFactory()
        offer = offers_factories.OfferFactory(venue__managingOfferer=user_offerer.offerer)
        offers_factories.StockFactory.create_batch(
            3, beginningDatetime=date_1, dateCreated=date_1, dateModified=date_1, offer=offer
        )
        # When
        response = client.with_session_auth(email=user_offerer.user.email).get(
            f"/offers/{offer.id}/stocks?date={date_2.date()}"
        )
        assert response.status_code == 200
        assert len(response.json["stocks"]) == 0
        assert response.json["hasStocks"] == True

    def test_should_return_total_stock_count_when_unfiltered(self, client):
        # Given
        date_1 = datetime.utcnow()
        date_2 = datetime.utcnow() + timedelta(days=1)
        user_offerer = offerers_factories.UserOffererFactory()
        offer = offers_factories.OfferFactory(venue__managingOfferer=user_offerer.offerer)
        offers_factories.StockFactory.create_batch(3, beginningDatetime=date_1, offer=offer)
        offers_factories.StockFactory.create_batch(2, beginningDatetime=date_2, offer=offer)

        # When
        response = client.with_session_auth(email=user_offerer.user.email).get(f"/offers/{offer.id}/stocks")
        assert response.status_code == 200
        assert response.json["stockCount"] == 5
        assert len(response.json["stocks"]) == 5

    def test_should_return_filtered_stock_count(self, client):
        # Given
        now = datetime.utcnow()
        beginning_datetime = now + timedelta(seconds=1)
        booking_limit_datetime = beginning_datetime.replace(hour=23, minute=59) - timedelta(days=3)
        user_offerer = offerers_factories.UserOffererFactory()
        offer = offers_factories.OfferFactory(venue__managingOfferer=user_offerer.offerer)
        offers_factories.ThingStockFactory.create_batch(
            4, dateCreated=now, dateModified=now, beginningDatetime=now, offer=offer
        )
        last_stock = offers_factories.ThingStockFactory(
            dateCreated=now, dateModified=now, beginningDatetime=beginning_datetime, offer=offer
        )

        # When
        response = client.with_session_auth(email=user_offerer.user.email).get(
            f"/offers/{offer.id}/stocks?page=3&stocks_limit_per_page=2"
        )

        # Then
        assert response.status_code == 200
        assert response.json == {
            "stockCount": 5,
            "hasStocks": True,
            "stocks": [
                {
                    "activationCodesExpirationDatetime": None,
                    "beginningDatetime": beginning_datetime.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                    "bookingLimitDatetime": booking_limit_datetime.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                    "bookingsQuantity": 0,
                    "hasActivationCode": False,
                    "id": last_stock.id,
                    "isEventDeletable": True,
                    "price": 10.1,
                    "priceCategoryId": None,
                    "quantity": 1000,
                    "remainingQuantity": 1000,
                },
            ],
        }

    def test_should_return_filtered_stock_count_and_filtered_stock_list(self, client):
        # Given
        date_1 = datetime.utcnow()
        date_2 = datetime.utcnow() + timedelta(days=1)
        user_offerer = offerers_factories.UserOffererFactory()
        offer = offers_factories.OfferFactory(venue__managingOfferer=user_offerer.offerer)
        offers_factories.StockFactory.create_batch(
            3, beginningDatetime=date_1, dateCreated=date_1, dateModified=date_1, offer=offer
        )
        offers_factories.StockFactory.create_batch(
            2, beginningDatetime=date_2, dateCreated=date_2, dateModified=date_2, offer=offer
        )
        # stock_list = [stock for stock in offer.stocks]
        stock_limit_per_page = 2
        # When
        response = client.with_session_auth(email=user_offerer.user.email).get(
            f"/offers/{offer.id}/stocks?date={date_1.date()}&stocks_limit_per_page={stock_limit_per_page}"
        )
        assert response.status_code == 200
        assert response.json["stockCount"] == 3
        assert len(response.json["stocks"]) == 2

    def test_should_return_filtered_stock_count_and_filtered_stock_list_with_stocks_inferior_to_limit_per_page(
        self, client
    ):
        # Given
        date_1 = datetime.utcnow()
        date_2 = datetime.utcnow() + timedelta(days=1)
        user_offerer = offerers_factories.UserOffererFactory()
        offer = offers_factories.OfferFactory(venue__managingOfferer=user_offerer.offerer)
        offers_factories.StockFactory.create_batch(
            3, beginningDatetime=date_1, dateCreated=date_1, dateModified=date_1, offer=offer
        )
        offers_factories.StockFactory.create_batch(
            2, beginningDatetime=date_2, dateCreated=date_2, dateModified=date_2, offer=offer
        )
        # stock_list = [stock for stock in offer.stocks]
        stock_limit_per_page = 4
        # When
        response = client.with_session_auth(email=user_offerer.user.email).get(
            f"/offers/{offer.id}/stocks?date={date_1.date()}&stocks_limit_per_page={stock_limit_per_page}"
        )
        assert response.status_code == 200
        assert response.json["stockCount"] == 3
        assert len(response.json["stocks"]) == 3

    def test_performance(self, client):
        # Given
        date_1 = datetime.utcnow()
        date_2 = datetime.utcnow() + timedelta(days=1)
        user_offerer = offerers_factories.UserOffererFactory()
        offer = offers_factories.OfferFactory(venue__managingOfferer=user_offerer.offerer)
        offers_factories.StockFactory.create_batch(3, beginningDatetime=date_1, dateCreated=date_1, offer=offer)
        offers_factories.StockFactory.create_batch(2, beginningDatetime=date_2, dateCreated=date_2, offer=offer)

        # When
        client = client.with_session_auth(email=user_offerer.user.email)
        with testing.assert_no_duplicated_queries():
            client.get(f"/offers/{offer.id}/stocks?date={date_1.date()}&time={date_1.hour}:{date_1.minute}")

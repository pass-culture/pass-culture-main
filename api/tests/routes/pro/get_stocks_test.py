from datetime import datetime
from datetime import timedelta

import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.core import testing


@pytest.mark.usefixtures("db_session")
class Returns403Test:
    num_queries = testing.AUTHENTICATION_QUERIES
    num_queries += 1  # select offer
    num_queries += 1  # check user has rights on venue
    num_queries += 1  # rollback

    def test_access_by_beneficiary(self, client):
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        offer = offers_factories.OfferFactory()

        client = client.with_session_auth(beneficiary.email)
        offer_id = offer.id
        with testing.assert_num_queries(self.num_queries):
            response = client.get(f"/offers/{offer_id}/stocks")
            assert response.status_code == 403

    def test_access_by_unauthorized_pro_user(self, client):
        pro_user = users_factories.ProFactory()
        offer = offers_factories.ThingOfferFactory()

        client = client.with_session_auth(pro_user.email)
        offer_id = offer.id
        with testing.assert_num_queries(self.num_queries):
            response = client.get(f"/offers/{offer_id}/stocks")
            assert response.status_code == 403


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    num_queries = testing.AUTHENTICATION_QUERIES
    num_queries += 1  # select offer
    num_queries += 1  # check user has rights on venue
    num_queries += 1  # checks active stocks exists
    num_queries += 1  # select count(*) from active stocks
    num_queries += 1  # select stocks

    def test_returns_an_event_stock(self, client):
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
        another_stock = offers_factories.EventStockFactory(
            dateCreated=now,
            dateModified=now,
            dateModifiedAtLastProvider=now,
            beginningDatetime=booking_datetime + timedelta(hours=1),
            bookingLimitDatetime=booking_datetime + timedelta(hours=1),
            offer=event_offer,
        )

        client = client.with_session_auth(email=user_offerer.user.email)
        offer_id = event_offer.id
        with testing.assert_num_queries(self.num_queries):
            response = client.get(f"/offers/{offer_id}/stocks/")
            assert response.status_code == 200

        assert response.json == {
            "stockCount": 2,
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
                },
                {
                    "activationCodesExpirationDatetime": None,
                    "beginningDatetime": (booking_datetime + timedelta(hours=1)).isoformat() + "Z",
                    "bookingLimitDatetime": (booking_datetime + timedelta(hours=1)).isoformat() + "Z",
                    "bookingsQuantity": 0,
                    "hasActivationCode": False,
                    "priceCategoryId": another_stock.priceCategoryId,
                    "id": another_stock.id,
                    "isEventDeletable": True,
                    "price": 10.1,
                    "quantity": 1000,
                    "remainingQuantity": 1000,
                },
            ],
        }

    def test_returns_a_thing_stock(self, client):
        now = datetime.utcnow()
        user_offerer = offerers_factories.UserOffererFactory()
        thing_offer = offers_factories.ThingOfferFactory(venue__managingOfferer=user_offerer.offerer)
        stock = offers_factories.ThingStockFactory(
            dateCreated=now,
            dateModified=now,
            offer=thing_offer,
        )

        client = client.with_session_auth(email=user_offerer.user.email)
        offer_id = thing_offer.id
        with testing.assert_num_queries(self.num_queries):
            response = client.get(f"/offers/{offer_id}/stocks/")
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
        user_offerer = offerers_factories.UserOffererFactory()
        offer = offers_factories.EventOfferFactory(venue__managingOfferer=user_offerer.offerer)
        offers_factories.EventStockFactory.create_batch(2, offer=offer, isSoftDeleted=True)

        client = client.with_session_auth(email=user_offerer.user.email)
        offer_id = offer.id
        with testing.assert_num_queries(self.num_queries - 2):  # no active stock exists
            response = client.get(f"/offers/{offer_id}/stocks")
            assert response.status_code == 200

        assert len(response.json["stocks"]) == 0

    def test_returns_false_if_no_stocks(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        offer = offers_factories.EventOfferFactory(venue__managingOfferer=user_offerer.offerer)

        client = client.with_session_auth(email=user_offerer.user.email)
        offer_id = offer.id
        with testing.assert_num_queries(self.num_queries - 2):  # no stock exists
            response = client.get(f"/offers/{offer_id}/stocks/")
            assert response.status_code == 200

        assert response.json["hasStocks"] == False

    def test_returns_false_if_all_stocks_are_soft_deleted(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        offer = offers_factories.EventOfferFactory(venue__managingOfferer=user_offerer.offerer)
        offers_factories.StockFactory.create_batch(3, offer=offer, isSoftDeleted=True)

        client = client.with_session_auth(email=user_offerer.user.email)
        offer_id = offer.id
        with testing.assert_num_queries(self.num_queries - 2):  # no active stock exists
            response = client.get(f"/offers/{offer_id}/stocks")
            assert response.status_code == 200

        assert response.json["hasStocks"] == False

    def test_returns_true_if_stock_exists_outside_filter(self, client):
        date_1 = datetime.utcnow()
        date_2 = datetime.utcnow() + timedelta(days=1)
        user_offerer = offerers_factories.UserOffererFactory()
        offer = offers_factories.OfferFactory(venue__managingOfferer=user_offerer.offerer)
        offers_factories.StockFactory.create_batch(
            3, beginningDatetime=date_1, dateCreated=date_1, dateModified=date_1, offer=offer
        )

        client = client.with_session_auth(email=user_offerer.user.email)
        offer_id = offer.id
        with testing.assert_num_queries(self.num_queries):
            response = client.get(f"/offers/{offer_id}/stocks?date={date_2.date()}")
            assert response.status_code == 200

        assert len(response.json["stocks"]) == 0
        assert response.json["hasStocks"] == True

    def test_should_return_total_stock_count_when_unfiltered(self, client):
        date_1 = datetime.utcnow()
        date_2 = datetime.utcnow() + timedelta(days=1)
        user_offerer = offerers_factories.UserOffererFactory()
        offer = offers_factories.OfferFactory(venue__managingOfferer=user_offerer.offerer)
        offers_factories.StockFactory.create_batch(3, beginningDatetime=date_1, offer=offer)
        offers_factories.StockFactory.create_batch(2, beginningDatetime=date_2, offer=offer)

        client = client.with_session_auth(email=user_offerer.user.email)
        offer_id = offer.id
        with testing.assert_num_queries(self.num_queries):
            response = client.get(f"/offers/{offer_id}/stocks")
            assert response.status_code == 200

        assert response.json["stockCount"] == 5
        assert len(response.json["stocks"]) == 5

    def test_should_return_filtered_stock_count(self, client):
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

        client = client.with_session_auth(email=user_offerer.user.email)
        offer_id = offer.id
        with testing.assert_num_queries(self.num_queries):
            response = client.get(f"/offers/{offer_id}/stocks?page=3&stocks_limit_per_page=2")
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
        stock_limit_per_page = 2

        client = client.with_session_auth(email=user_offerer.user.email)
        offer_id = offer.id
        with testing.assert_num_queries(self.num_queries):
            response = client.get(
                f"/offers/{offer_id}/stocks?date={date_1.date()}&stocks_limit_per_page={stock_limit_per_page}"
            )
            assert response.status_code == 200

        assert response.json["stockCount"] == 3
        assert len(response.json["stocks"]) == 2

    def test_should_return_filtered_stock_count_and_filtered_stock_list_with_stocks_inferior_to_limit_per_page(
        self, client
    ):
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
        stock_limit_per_page = 4

        client = client.with_session_auth(email=user_offerer.user.email)
        offer_id = offer.id
        with testing.assert_num_queries(self.num_queries):
            response = client.get(
                f"/offers/{offer_id}/stocks?date={date_1.date()}&stocks_limit_per_page={stock_limit_per_page}"
            )
            assert response.status_code == 200

        assert response.json["stockCount"] == 3
        assert len(response.json["stocks"]) == 3

        assert response.json["stockCount"] == 3
        assert len(response.json["stocks"]) == 3

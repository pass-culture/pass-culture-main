from datetime import datetime

from freezegun import freeze_time
import pytest

from pcapi.core import testing
import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    @freeze_time("2020-10-15 00:00:00")
    def test_returns_an_event_stock(self, app, assert_num_queries):
        # Given
        now = datetime.utcnow()
        pro = users_factories.ProFactory()
        stock = offers_factories.EventStockFactory(
            dateCreated=now,
            dateModified=now,
            dateModifiedAtLastProvider=now,
            beginningDatetime=now,
            bookingLimitDatetime=now,
        )
        bookings_factories.BookingFactory.create_batch(3, stock=stock)
        offers_factories.UserOffererFactory(user=pro, offerer=stock.offer.venue.managingOfferer)
        client = TestClient(app.test_client()).with_session_auth(email=pro.email)

        # When
        offer_id = stock.offer.id
        n_query_select_offerer = 1
        n_query_exist_user_offerer = 1
        n_query_select_stock = 1

        with assert_num_queries(
            testing.AUTHENTICATION_QUERIES + n_query_select_offerer + n_query_exist_user_offerer + n_query_select_stock
        ):
            response = client.get(f"/offers/{humanize(offer_id)}/stocks")

        # Then
        assert response.status_code == 200
        assert response.json == {
            "stocks": [
                {
                    "hasActivationCodes": False,
                    "activationCodesExpirationDatetime": None,
                    "beginningDatetime": "2020-10-15T00:00:00Z",
                    "bookingLimitDatetime": "2020-10-15T00:00:00Z",
                    "bookingsQuantity": 3,
                    "dateCreated": "2020-10-15T00:00:00Z",
                    "dateModified": "2020-10-15T00:00:00Z",
                    "id": humanize(stock.id),
                    "isEventDeletable": True,
                    "isEventExpired": True,
                    "offerId": humanize(stock.offer.id),
                    "price": 10.0,
                    "quantity": 1000,
                }
            ],
        }

    @freeze_time("2019-10-15 00:00:00")
    def test_returns_a_thing_stock_without_activation_codes(self, app):
        # Given
        now = datetime.utcnow()
        pro = users_factories.ProFactory()
        stock = offers_factories.ThingStockFactory(
            dateCreated=now,
            dateModified=now,
            dateModifiedAtLastProvider=now,
            bookingLimitDatetime=now,
        )
        stock_on_other_offer = offers_factories.ThingStockFactory(offer__venue=stock.offer.venue)
        offers_factories.UserOffererFactory(user=pro, offerer=stock.offer.venue.managingOfferer)
        client = TestClient(app.test_client()).with_session_auth(email=pro.email)

        # When
        response = client.get(f"/offers/{humanize(stock.offer.id)}/stocks")

        # Then
        assert response.status_code == 200
        assert stock_on_other_offer.id not in [stock["id"] for stock in response.json["stocks"]]
        assert response.json == {
            "stocks": [
                {
                    "hasActivationCodes": False,
                    "activationCodesExpirationDatetime": None,
                    "beginningDatetime": None,
                    "bookingLimitDatetime": "2019-10-15T00:00:00Z",
                    "bookingsQuantity": 0,
                    "dateCreated": "2019-10-15T00:00:00Z",
                    "dateModified": "2019-10-15T00:00:00Z",
                    "id": humanize(stock.id),
                    "isEventDeletable": True,
                    "isEventExpired": False,
                    "offerId": humanize(stock.offer.id),
                    "price": 10.0,
                    "quantity": 1000,
                }
            ],
        }

    @freeze_time("2019-10-15 00:00:00")
    def test_returns_a_thing_stock_with_activation_codes(self, app, assert_num_queries):
        # Given
        now = datetime.utcnow()
        pro = users_factories.ProFactory()
        offer = offers_factories.OfferFactory(url="url.com")
        stock, _ = offers_factories.ThingStockFactory.create_batch(
            2,
            dateCreated=now,
            dateModified=now,
            dateModifiedAtLastProvider=now,
            bookingLimitDatetime=now,
            offer=offer,
        )
        offers_factories.ActivationCodeFactory(stock=stock, code="ABC", expirationDate=datetime(2022, 10, 15))
        offers_factories.ActivationCodeFactory(stock=stock, code="DEF", expirationDate=datetime(2022, 10, 15))
        stock_on_other_offer = offers_factories.ThingStockFactory(offer__venue=stock.offer.venue)
        offers_factories.UserOffererFactory(user=pro, offerer=stock.offer.venue.managingOfferer)
        client = TestClient(app.test_client()).with_session_auth(email=pro.email)

        # When
        stock_id = stock.offer.id
        n_query_select_offerer = 1
        n_query_exist_user_offerer = 1
        n_query_select_stock = 1
        n_query_select_activation_code = 2  # 1 query per stock

        with assert_num_queries(
            testing.AUTHENTICATION_QUERIES
            + n_query_select_offerer
            + n_query_exist_user_offerer
            + n_query_select_stock
            + n_query_select_activation_code
        ):
            response = client.get(f"/offers/{humanize(stock_id)}/stocks")

        # Then
        assert response.status_code == 200
        assert stock_on_other_offer.id not in [stock["id"] for stock in response.json["stocks"]]
        assert response.json["stocks"][0] == {
            "hasActivationCodes": True,
            "activationCodesExpirationDatetime": "2022-10-15T00:00:00Z",
            "beginningDatetime": None,
            "bookingLimitDatetime": "2019-10-15T00:00:00Z",
            "bookingsQuantity": 0,
            "dateCreated": "2019-10-15T00:00:00Z",
            "dateModified": "2019-10-15T00:00:00Z",
            "id": humanize(stock.id),
            "isEventDeletable": True,
            "isEventExpired": False,
            "offerId": humanize(stock.offer.id),
            "price": 10.0,
            "quantity": 1000,
        }

    def test_does_not_return_soft_deleted_stock(self, app):
        # Given
        pro = users_factories.ProFactory()
        stock = offers_factories.ThingStockFactory(isSoftDeleted=True)
        offers_factories.UserOffererFactory(user=pro, offerer=stock.offer.venue.managingOfferer)
        client = TestClient(app.test_client()).with_session_auth(email=pro.email)

        # When
        response = client.get(f"/offers/{humanize(stock.offer.id)}/stocks")

        # Then
        assert response.status_code == 200
        assert response.json == {
            "stocks": [],
        }

    def test_query_performance(self, app, db_session, assert_num_queries):
        # Given
        now = datetime.utcnow()
        pro = users_factories.ProFactory()
        stock_1 = offers_factories.ThingStockFactory(
            dateCreated=now,
            dateModified=now,
            dateModifiedAtLastProvider=now,
            bookingLimitDatetime=now,
        )
        offer = stock_1.offer
        stock_2 = offers_factories.ThingStockFactory(
            dateCreated=now, dateModified=now, dateModifiedAtLastProvider=now, bookingLimitDatetime=now, offer=offer
        )
        bookings_factories.BookingFactory(stock=stock_1)
        bookings_factories.BookingFactory(stock=stock_1)
        bookings_factories.BookingFactory(stock=stock_2)
        offers_factories.UserOffererFactory(user=pro, offerer=offer.venue.managingOfferer)
        client = TestClient(app.test_client()).with_session_auth(email=pro.email)
        check_user_has_rights_queries = 2
        get_stock_queries = 1
        offer_id = offer.id

        # When
        with assert_num_queries(testing.AUTHENTICATION_QUERIES + check_user_has_rights_queries + get_stock_queries):
            response = client.get(f"/offers/{humanize(offer_id)}/stocks")

        # Then
        assert response.status_code == 200


@pytest.mark.usefixtures("db_session")
class Returns403Test:
    def test_returns_an_event_stock(self, app):
        # Given
        now = datetime.utcnow()
        pro = users_factories.ProFactory()
        stock = offers_factories.EventStockFactory(
            dateCreated=now,
            dateModified=now,
            dateModifiedAtLastProvider=now,
            beginningDatetime=now,
            bookingLimitDatetime=now,
        )
        client = TestClient(app.test_client()).with_session_auth(email=pro.email)

        # When
        response = client.get(f"/offers/{humanize(stock.offer.id)}/stocks")

        # Then
        assert response.status_code == 403
        assert response.json == {
            "global": ["Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."]
        }

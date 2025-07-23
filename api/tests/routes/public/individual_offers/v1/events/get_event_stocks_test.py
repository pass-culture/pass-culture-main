import datetime

import pytest

from pcapi.core import testing
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.utils import date as date_utils

from tests.conftest import TestClient
from tests.routes.public.helpers import PublicAPIVenueEndpointHelper


@pytest.mark.usefixtures("db_session")
class GetEventStocksTest(PublicAPIVenueEndpointHelper):
    endpoint_url = "/public/offers/v1/events/{offer_id}/dates"
    endpoint_method = "get"
    default_path_params = {"offer_id": 1}

    num_queries_400 = 1  # select api_key, offerer and provider
    num_queries_400 += 1  # select offers
    num_queries_400 += 1  # rollback atomic

    num_queries = 1  # select api_key, offerer and provider
    num_queries += 1  # select offers
    num_queries_with_stocks = num_queries + 1  # Select stock ids
    num_queries_with_stocks += 1  # Select stocks

    def setup_base_resource(self, venue=None, provider=None) -> tuple[offers_models.Offer, offers_models.Stock]:
        event = offers_factories.EventOfferFactory(venue=venue or self.setup_venue(), lastProvider=provider)
        price_category = offers_factories.PriceCategoryFactory(
            offer=event, price=12.34, priceCategoryLabel__label="carre or"
        )
        two_weeks_from_now = datetime.datetime.utcnow().replace(second=0, microsecond=0) + datetime.timedelta(weeks=2)
        stock = offers_factories.EventStockFactory(
            offer=event,
            priceCategory=price_category,
            quantity=10,
            bookingLimitDatetime=two_weeks_from_now,
            beginningDatetime=two_weeks_from_now,
            idAtProviders="Il y a deux types d'id",
        )
        return event, stock

    def test_should_raise_404_because_has_no_access_to_venue(self):
        plain_api_key, _ = self.setup_provider()
        offer, _ = self.setup_base_resource()
        offer_id = offer.id

        with testing.assert_num_queries(self.num_queries_400):
            response = self.make_request(plain_api_key, path_params={"offer_id": offer_id})
            assert response.status_code == 404

    def test_should_raise_404_because_venue_provider_is_inactive(self):
        plain_api_key, venue_provider = self.setup_inactive_venue_provider()
        offer, _ = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        offer_id = offer.id

        with testing.assert_num_queries(self.num_queries_400):
            response = self.make_request(plain_api_key, path_params={"offer_id": offer_id})
            assert response.status_code == 404

    def test_should_raise_400_because_too_many_ids_at_provider(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        offer = offers_factories.EventOfferFactory(venue=venue_provider.venue, lastProvider=venue_provider.provider)
        with testing.assert_num_queries(self.num_queries_400):
            response = self.make_request(
                plain_api_key,
                path_params={"offer_id": offer.id},
                query_params={"idsAtProvider": ",".join(["1234567890123" for _ in range(101)])},
            )

            assert response.status_code == 400

        assert response.json == {"idsAtProvider": ["Too many ids"]}

    def test_event_with_dates(self, client: TestClient):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        offer = offers_factories.EventOfferFactory(venue=venue_provider.venue, lastProvider=venue_provider.provider)
        offer_id = offer.id
        offers_factories.StockFactory(offer=offer, isSoftDeleted=True)
        price_category = offers_factories.PriceCategoryFactory(
            offer=offer, price=12.34, priceCategoryLabel__label="carre or"
        )
        two_weeks_from_now = datetime.datetime.utcnow().replace(second=0, microsecond=0) + datetime.timedelta(weeks=2)
        stock1_id_at_provider = "5edd982915c2a74b9302e443"
        bookable_stock = offers_factories.EventStockFactory(
            offer=offer,
            priceCategory=price_category,
            quantity=10,
            bookingLimitDatetime=two_weeks_from_now,
            beginningDatetime=two_weeks_from_now,
            idAtProviders=stock1_id_at_provider,
        )
        not_booked_price_category = offers_factories.PriceCategoryFactory(
            offer=offer, price=299.99, priceCategoryLabel__label="ultra vip"
        )
        stock2_id_at_provider = "2ezz982915c2a74b9302e546"
        stock_without_booking = offers_factories.EventStockFactory(
            offer=offer,
            priceCategory=not_booked_price_category,
            quantity=2,
            bookingLimitDatetime=two_weeks_from_now,
            beginningDatetime=two_weeks_from_now,
            idAtProviders=stock2_id_at_provider,
        )
        offers_factories.EventStockFactory(offer=offer, isSoftDeleted=True)  # deleted stock, not returned
        bookings_factories.BookingFactory(stock=bookable_stock)
        expected_serialized_stock1 = {
            "beginningDatetime": date_utils.format_into_utc_date(two_weeks_from_now),
            "bookedQuantity": 1,
            "bookingLimitDatetime": date_utils.format_into_utc_date(two_weeks_from_now),
            "id": bookable_stock.id,
            "priceCategory": {
                "id": price_category.id,
                "label": "carre or",
                "price": 1234,
                "idAtProvider": None,
            },
            "quantity": 10,
            "idAtProvider": "5edd982915c2a74b9302e443",
        }
        expected_serialized_stock2 = {
            "beginningDatetime": date_utils.format_into_utc_date(two_weeks_from_now),
            "bookedQuantity": 0,
            "bookingLimitDatetime": date_utils.format_into_utc_date(two_weeks_from_now),
            "id": stock_without_booking.id,
            "priceCategory": {
                "id": not_booked_price_category.id,
                "label": not_booked_price_category.label,
                "price": not_booked_price_category.price * 100,
                "idAtProvider": None,
            },
            "quantity": 2,
            "idAtProvider": "2ezz982915c2a74b9302e546",
        }

        # Without filtering on `idsAtProvider`
        with testing.assert_num_queries(self.num_queries_with_stocks):
            response = self.make_request(plain_api_key, path_params={"offer_id": offer_id})
            assert response.status_code == 200

        assert response.json["dates"] == [expected_serialized_stock1, expected_serialized_stock2]

        # With filtering on `idsAtProvider`
        with testing.assert_num_queries(self.num_queries_with_stocks):
            response = self.make_request(
                plain_api_key,
                path_params={"offer_id": offer_id},
                query_params={"idsAtProvider": stock2_id_at_provider},
            )
            assert response.status_code == 200

        assert response.json["dates"] == [expected_serialized_stock2]

        with testing.assert_num_queries(self.num_queries_with_stocks):
            response = self.make_request(
                plain_api_key,
                path_params={"offer_id": offer_id},
                query_params={"idsAtProvider": f"{stock1_id_at_provider},{stock2_id_at_provider}"},
            )
            assert response.status_code == 200

        assert response.json["dates"] == [expected_serialized_stock1, expected_serialized_stock2]

    def test_event_without_dates(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        offer = offers_factories.EventOfferFactory(venue=venue_provider.venue, lastProvider=venue_provider.provider)
        offer_id = offer.id
        offers_factories.EventStockFactory(offer=offer, isSoftDeleted=True)  # deleted stock, not returned

        with testing.assert_num_queries(self.num_queries_with_stocks):
            response = self.make_request(plain_api_key, path_params={"offer_id": offer_id})
            assert response.status_code == 200

        assert response.json == {"dates": []}

    def test_should_return_no_result_when_first_index_is_too_high(self, client: TestClient):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        offer, stock = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        offer_id = offer.id
        out_of_range_index = stock.id + 1

        with testing.assert_num_queries(self.num_queries_with_stocks):
            response = self.make_request(
                plain_api_key, path_params={"offer_id": offer_id}, query_params={"firstIndex": out_of_range_index}
            )
            assert response.status_code == 200

        assert response.json == {"dates": []}

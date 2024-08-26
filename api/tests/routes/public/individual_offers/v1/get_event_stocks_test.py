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
    endpoint_url = "/public/offers/v1/events/{event_id}/dates"
    endpoint_method = "get"
    default_path_params = {"event_id": 1}

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

    def test_should_raise_404_because_has_no_access_to_venue(self, client: TestClient):
        plain_api_key, _ = self.setup_provider()
        event, _ = self.setup_base_resource()
        response = client.with_explicit_token(plain_api_key).get(self.endpoint_url.format(event_id=event.id))
        assert response.status_code == 404

    def test_should_raise_404_because_venue_provider_is_inactive(self, client: TestClient):
        plain_api_key, venue_provider = self.setup_inactive_venue_provider()
        event, _ = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        response = client.with_explicit_token(plain_api_key).get(self.endpoint_url.format(event_id=event.id))
        assert response.status_code == 404

    def test_event_with_dates(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event_offer = offers_factories.EventOfferFactory(
            venue=venue_provider.venue, lastProvider=venue_provider.provider
        )
        event_offer_id = event_offer.id
        offers_factories.StockFactory(offer=event_offer, isSoftDeleted=True)
        price_category = offers_factories.PriceCategoryFactory(
            offer=event_offer, price=12.34, priceCategoryLabel__label="carre or"
        )
        two_weeks_from_now = datetime.datetime.utcnow().replace(second=0, microsecond=0) + datetime.timedelta(weeks=2)
        bookable_stock = offers_factories.EventStockFactory(
            offer=event_offer,
            priceCategory=price_category,
            quantity=10,
            bookingLimitDatetime=two_weeks_from_now,
            beginningDatetime=two_weeks_from_now,
            idAtProviders="Il y a deux types d'id",
        )
        not_booked_price_category = offers_factories.PriceCategoryFactory(
            offer=event_offer, price=299.99, priceCategoryLabel__label="ultra vip"
        )
        stock_without_booking = offers_factories.EventStockFactory(
            offer=event_offer,
            priceCategory=not_booked_price_category,
            quantity=2,
            bookingLimitDatetime=two_weeks_from_now,
            beginningDatetime=two_weeks_from_now,
        )
        offers_factories.EventStockFactory(offer=event_offer, isSoftDeleted=True)  # deleted stock, not returned
        bookings_factories.BookingFactory(stock=bookable_stock)

        with testing.assert_no_duplicated_queries():
            response = client.with_explicit_token(plain_api_key).get(self.endpoint_url.format(event_id=event_offer_id))

        assert response.status_code == 200
        assert response.json["dates"] == [
            {
                "beginningDatetime": date_utils.format_into_utc_date(two_weeks_from_now),
                "bookedQuantity": 1,
                "bookingLimitDatetime": date_utils.format_into_utc_date(two_weeks_from_now),
                "id": bookable_stock.id,
                "priceCategory": {"id": price_category.id, "label": "carre or", "price": 1234},
                "quantity": 10,
                "idAtProvider": "Il y a deux types d'id",
            },
            {
                "beginningDatetime": date_utils.format_into_utc_date(two_weeks_from_now),
                "bookedQuantity": 0,
                "bookingLimitDatetime": date_utils.format_into_utc_date(two_weeks_from_now),
                "id": stock_without_booking.id,
                "priceCategory": {
                    "id": not_booked_price_category.id,
                    "label": not_booked_price_category.label,
                    "price": not_booked_price_category.price * 100,
                },
                "quantity": 2,
                "idAtProvider": None,
            },
        ]

    def test_event_without_dates(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event_offer = offers_factories.EventOfferFactory(
            venue=venue_provider.venue, lastProvider=venue_provider.provider
        )
        event_offer_id = event_offer.id
        offers_factories.EventStockFactory(offer=event_offer, isSoftDeleted=True)  # deleted stock, not returned

        with testing.assert_no_duplicated_queries():
            response = client.with_explicit_token(plain_api_key).get(self.endpoint_url.format(event_id=event_offer_id))

        assert response.status_code == 200
        assert response.json == {"dates": []}

    def test_should_return_no_result_when_first_index_is_too_high(self, client: TestClient):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event, stock = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        event_id = event.id
        out_of_range_index = stock.id + 1

        with testing.assert_no_duplicated_queries():
            response = client.with_explicit_token(plain_api_key).get(
                self.endpoint_url.format(event_id=event_id), params={"firstIndex": out_of_range_index}
            )

        assert response.status_code == 200
        assert response.json == {"dates": []}

import datetime

import pytest

from pcapi.core import testing
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.utils import date as date_utils

from . import utils


@pytest.mark.usefixtures("db_session")
class GetEventDatesTest:
    def test_event_with_dates(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(venue=venue)
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
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
                f"/public/offers/v1/events/{event_offer.id}/dates"
            )

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
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(venue=venue)
        offers_factories.EventStockFactory(offer=event_offer, isSoftDeleted=True)  # deleted stock, not returned

        with testing.assert_no_duplicated_queries():
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
                f"/public/offers/v1/events/{event_offer.id}/dates"
            )

        assert response.status_code == 200
        assert response.json == {
            "dates": [],
        }

    def test_404_when_page_is_too_high(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(venue=venue)
        event_stock = offers_factories.EventStockFactory(offer=event_offer)

        with testing.assert_no_duplicated_queries():
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
                f"/public/offers/v1/events/{event_offer.id}/dates?firstIndex={int(event_stock.id)+1}&limit=50"
            )

        assert response.status_code == 200
        assert response.json == {"dates": []}

    def test_404_inactive_venue_provider(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue(is_venue_provider_active=False)
        event_offer = offers_factories.EventOfferFactory(venue=venue)
        offers_factories.StockFactory(offer=event_offer, isSoftDeleted=True)
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            f"/public/offers/v1/events/{event_offer.id}/dates"
        )

        assert response.status_code == 404

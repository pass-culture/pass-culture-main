import datetime

import freezegun
import pytest

from pcapi.core import testing
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories

from . import utils


@pytest.mark.usefixtures("db_session")
class GetEventDatesTest:
    @freezegun.freeze_time("2023-01-01 12:00:00")
    def test_event_with_dates(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(venue=venue)
        offers_factories.StockFactory(offer=event_offer, isSoftDeleted=True)
        price_category = offers_factories.PriceCategoryFactory(
            offer=event_offer, price=12.34, priceCategoryLabel__label="carre or"
        )
        bookable_stock = offers_factories.EventStockFactory(
            offer=event_offer,
            priceCategory=price_category,
            quantity=10,
            bookingLimitDatetime=datetime.datetime(2023, 1, 15, 13, 0, 0),
            beginningDatetime=datetime.datetime(2023, 1, 15, 13, 0, 0),
        )
        stock_without_booking = offers_factories.EventStockFactory(
            offer=event_offer,
            # FIXME (cepehang, 2023-02-02): remove price and None price category after price category generation script
            price=12.34,
            priceCategory=None,
            quantity=2,
            bookingLimitDatetime=datetime.datetime(2023, 1, 15, 13, 0, 0),
            beginningDatetime=datetime.datetime(2023, 1, 15, 13, 0, 0),
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
                "beginningDatetime": "2023-01-15T13:00:00Z",
                "bookedQuantity": 1,
                "bookingLimitDatetime": "2023-01-15T13:00:00Z",
                "id": bookable_stock.id,
                "priceCategory": {"id": price_category.id, "label": "carre or", "price": 1234},
                "quantity": 10,
            },
            {
                "beginningDatetime": "2023-01-15T13:00:00Z",
                "bookedQuantity": 0,
                "bookingLimitDatetime": "2023-01-15T13:00:00Z",
                "id": stock_without_booking.id,
                "priceCategory": {"id": None, "label": None, "price": 1234},
                "quantity": 2,
            },
        ]
        assert (
            response.json["pagination"]["pagesLinks"]["current"]
            == f"http://localhost/public/offers/v1/events/{event_offer.id}/dates?page=1&limit=50"
        )

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
            "pagination": {
                "currentPage": 1,
                "itemsCount": 0,
                "itemsTotal": 0,
                "lastPage": 1,
                "limitPerPage": 50,
                "pagesLinks": {
                    "current": f"http://localhost/public/offers/v1/events/{event_offer.id}/dates?page=1&limit=50",
                    "first": f"http://localhost/public/offers/v1/events/{event_offer.id}/dates?page=1&limit=50",
                    "last": f"http://localhost/public/offers/v1/events/{event_offer.id}/dates?page=1&limit=50",
                    "next": None,
                    "previous": None,
                },
            },
        }

    def test_404_when_page_is_too_high(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(venue=venue)
        offers_factories.EventStockFactory(offer=event_offer)  # deleted stock, not returned

        with testing.assert_no_duplicated_queries():
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
                f"/public/offers/v1/events/{event_offer.id}/dates?page=2&limit=50"
            )

        assert response.status_code == 404
        assert response.json == {
            "page": "The page you requested does not exist. The maximum page for the specified limit is 1"
        }

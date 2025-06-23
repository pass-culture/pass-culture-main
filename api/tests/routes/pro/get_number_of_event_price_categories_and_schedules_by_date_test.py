from datetime import datetime

import pytest

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.bookings.models as bookings_models
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core import testing


@pytest.mark.usefixtures("db_session")
def test_return_price_categories_and_schedule_count_by_date(client):
    user_offerer = offerers_factories.UserOffererFactory()

    offer = offers_factories.OfferFactory(venue__managingOfferer=user_offerer.offerer)

    stocks_with_bookings = []
    # date with 1 schedule time and 1 price category
    stocks_with_bookings.append(
        offers_factories.EventStockFactory(offer=offer, beginningDatetime=datetime(2024, 9, 9, 12, 0, 0))
    )

    # date with 1 schedule time and 4 price categories
    date = datetime(2024, 10, 10, 12, 0, 0)
    stocks_with_bookings.append(offers_factories.EventStockFactory(offer=offer, beginningDatetime=date))
    stocks_with_bookings.append(offers_factories.EventStockFactory(offer=offer, beginningDatetime=date))
    stocks_with_bookings.append(offers_factories.EventStockFactory(offer=offer, beginningDatetime=date))
    stocks_with_bookings.append(offers_factories.EventStockFactory(offer=offer, beginningDatetime=date))

    # date with 2 schedule times and 1 price category
    price_category = offers_factories.PriceCategoryFactory(offer=offer)
    stocks_with_bookings.append(
        offers_factories.EventStockFactory(
            offer=offer, beginningDatetime=datetime(2024, 11, 11, 15, 0, 0), priceCategory=price_category
        )
    )
    stocks_with_bookings.append(
        offers_factories.EventStockFactory(
            offer=offer, beginningDatetime=datetime(2024, 11, 11, 12, 0, 0), priceCategory=price_category
        )
    )

    # date with 3 schedule times and 2 price categories
    price_category_1 = offers_factories.PriceCategoryFactory(offer=offer)
    price_category_2 = offers_factories.PriceCategoryFactory(offer=offer)
    stocks_with_bookings.append(
        offers_factories.EventStockFactory(
            offer=offer, beginningDatetime=datetime(2024, 12, 12, 15, 0, 0), priceCategory=price_category_1
        )
    )
    stocks_with_bookings.append(
        offers_factories.EventStockFactory(
            offer=offer, beginningDatetime=datetime(2024, 12, 12, 12, 0, 0), priceCategory=price_category_1
        )
    )
    stocks_with_bookings.append(
        offers_factories.EventStockFactory(
            offer=offer, beginningDatetime=datetime(2024, 12, 12, 18, 0, 0), priceCategory=price_category_2
        )
    )

    # stock with no bookings
    offers_factories.EventStockFactory(offer=offer, beginningDatetime=datetime(2024, 1, 1, 12, 0, 0))

    # stock with cancelled booking
    stock = offers_factories.EventStockFactory(offer=offer, beginningDatetime=datetime(2024, 2, 2, 12, 0, 0))
    bookings_factories.BookingFactory(
        stock=stock,
        status=bookings_models.BookingStatus.CANCELLED,
    )

    for stock in stocks_with_bookings:
        bookings_factories.BookingFactory(
            stock=stock,
        )

    client = client.with_session_auth(user_offerer.user.email)
    offer_id = offer.id
    queries = testing.AUTHENTICATION_QUERIES
    queries += 1  # select venue
    queries += 1  # check user_offerer exists
    queries += 1  # select stock
    with testing.assert_num_queries(queries):
        response = client.get(f"/bookings/dates/{offer_id}")
        assert response.status_code == 200

    assert response.json == [
        {"eventDate": "2024-02-02", "scheduleCount": 1, "priceCategoriesCount": 1},
        {"eventDate": "2024-09-09", "scheduleCount": 1, "priceCategoriesCount": 1},
        {"eventDate": "2024-10-10", "scheduleCount": 1, "priceCategoriesCount": 4},
        {"eventDate": "2024-11-11", "scheduleCount": 2, "priceCategoriesCount": 1},
        {"eventDate": "2024-12-12", "scheduleCount": 3, "priceCategoriesCount": 2},
    ]


@pytest.mark.usefixtures("db_session")
def test_return_empty_list_when_no_stock(client):
    user_offerer = offerers_factories.UserOffererFactory()

    offer = offers_factories.OfferFactory(venue__managingOfferer=user_offerer.offerer)

    client = client.with_session_auth(user_offerer.user.email)
    offer_id = offer.id
    queries = testing.AUTHENTICATION_QUERIES
    queries += 1  # select venue
    queries += 1  # check user_offerer exists
    queries += 1  # select stock
    with testing.assert_num_queries(queries):
        response = client.get(f"/bookings/dates/{offer_id}")
        assert response.status_code == 200

    assert response.json == []


@pytest.mark.usefixtures("db_session")
def test_user_is_forbidden(client):
    user_offerer = offerers_factories.UserOffererFactory()

    offer = offers_factories.OfferFactory()

    client = client.with_session_auth(user_offerer.user.email)
    offer_id = offer.id
    queries = testing.AUTHENTICATION_QUERIES
    queries += 1  # select venue
    queries += 1  # check user_offerer exists
    queries += 1  # rollback
    with testing.assert_num_queries(queries):
        response = client.get(f"/bookings/dates/{offer_id}")
        assert response.status_code == 403

from datetime import UTC
from datetime import datetime
from datetime import timedelta

import pytest
from dateutil.relativedelta import relativedelta

import pcapi.core.offers.factories as offers_factories
from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.categories import subcategories
from pcapi.core.geography.factories import AddressFactory
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.providers.repository import get_provider_by_local_class
from pcapi.core.subscription import factories as subscription_factories
from pcapi.core.subscription import models as subscription_models
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.utils import date as date_utils


pytestmark = pytest.mark.usefixtures("db_session")


class MovieCalendarTest:
    def test_get_movie_shows_with_allocine_id(self, client):
        product = offers_factories.ProductFactory(extraData={"allocineId": 12345})
        address = AddressFactory(latitude=48.85, longitude=2.35)
        tz_naive_beginning_datetime = date_utils.get_naive_utc_now() + timedelta(hours=1)
        tz_aware_beginning_datetime = date_utils.default_timezone_to_local_datetime(
            tz_naive_beginning_datetime, address.timezone
        )
        stock = offers_factories.EventStockFactory(
            offer__product=product,
            offer__venue__offererAddress__address=address,
            beginningDatetime=tz_naive_beginning_datetime,
        )

        start = date_utils.get_naive_utc_now()
        end = date_utils.get_naive_utc_now() + timedelta(days=1)
        params = {
            "allocineId": "12345",
            "latitude": 48.85,
            "longitude": 2.35,
            "from": start,
            "to": end,
        }
        expected_num_queries = 1  # product
        expected_num_queries += 1  # stocks
        expected_num_queries += 1  # screenings
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/movie/calendar", params=params)
            assert response.status_code == 200

        calendar = response.json["calendar"]
        today = date_utils.default_timezone_to_local_datetime(start, address.timezone).date()
        tomorrow = date_utils.default_timezone_to_local_datetime(end, address.timezone).date()
        assert calendar == [
            {
                "date": today.isoformat(),
                "screenings": [
                    {
                        "address": f"{address.street}, {address.postalCode} {address.city}",
                        "distance": 0.0,
                        "dayScreenings": [
                            {
                                "beginningDatetime": tz_aware_beginning_datetime.isoformat(),
                                "bookability": "AUTHENTICATION_REQUIRED",
                                "features": [],
                                "price": float(stock.price),
                                "stockId": stock.id,
                            }
                        ],
                        "label": stock.offer.venue.publicName,
                        "nextScreening": {
                            "beginningDatetime": tz_aware_beginning_datetime.isoformat(),
                            "bookability": "AUTHENTICATION_REQUIRED",
                            "features": [],
                            "price": float(stock.price),
                            "stockId": stock.id,
                        },
                        "offerId": stock.offer.id,
                        "thumbUrl": None,
                        "venueId": stock.offer.venue.id,
                    },
                ],
            },
            {
                "date": tomorrow.isoformat(),
                "screenings": [
                    {
                        "address": f"{address.street}, {address.postalCode} {address.city}",
                        "distance": 0.0,
                        "dayScreenings": [],
                        "label": stock.offer.venue.publicName,
                        "nextScreening": {
                            "beginningDatetime": tz_aware_beginning_datetime.isoformat(),
                            "bookability": "AUTHENTICATION_REQUIRED",
                            "features": [],
                            "price": 10.1,
                            "stockId": stock.id,
                        },
                        "offerId": stock.offer.id,
                        "thumbUrl": None,
                        "venueId": stock.offer.venue.id,
                    },
                ],
            },
        ]

    def test_get_movie_shows_with_visa(self, client):
        product = offers_factories.ProductFactory(extraData={"visa": "12345"})
        address = AddressFactory(latitude=48.85, longitude=2.35)
        offers_factories.EventStockFactory(
            offer__product=product,
            offer__venue__offererAddress__address=address,
            beginningDatetime=date_utils.get_naive_utc_now() + timedelta(hours=1),
        )

        start = date_utils.get_naive_utc_now()
        end = date_utils.get_naive_utc_now() + timedelta(days=1)
        params = {
            "visa": "12345",
            "latitude": 48.85,
            "longitude": 2.35,
            "from": start,
            "to": end,
        }
        expected_num_queries = 1  # product
        expected_num_queries += 1  # stocks
        expected_num_queries += 1  # screenings
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/movie/calendar", params=params)
            assert response.status_code == 200

        today = date_utils.default_timezone_to_local_datetime(start, address.timezone).date()
        tomorrow = date_utils.default_timezone_to_local_datetime(end, address.timezone).date()
        assert len(response.json["calendar"]) == 2
        assert [e["date"] for e in response.json["calendar"]] == [today.isoformat(), tomorrow.isoformat()]

    def test_requires_allocine_id_or_visa(self, client):
        params = {
            "latitude": 48.85,
            "longitude": 2.35,
        }
        expected_num_queries = 0  # should fail before fetching anything
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/movie/calendar", params=params)
            assert response.status_code == 400

    def test_cant_have_allocine_id_and_visa(self, client):
        params = {
            "allocineId": "12345",
            "visa": "12345",
            "latitude": 48.85,
            "longitude": 2.35,
        }
        expected_num_queries = 0  # should fail before fetching anything
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/movie/calendar", params=params)
            assert response.status_code == 400

    def test_requires_location(self, client):
        params = {
            "visa": "12345",
            "latitude": 48.85,
        }
        expected_num_queries = 0  # should fail before fetching anything
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/movie/calendar", params=params)
            assert response.status_code == 400

    def test_returns_404_if_product_not_found(self, client):
        params = {
            "allocineId": "12345",
            "latitude": 48.85,
            "longitude": 2.35,
        }
        expected_num_queries = 1  # product
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/movie/calendar", params=params)
            assert response.status_code == 404

    def test_on_no_screenings_found(self, client):
        offers_factories.ProductFactory(extraData={"allocineId": 12345})
        start = date_utils.get_naive_utc_now()
        end = date_utils.get_naive_utc_now() + timedelta(days=1)
        params = {
            "allocineId": "12345",
            "latitude": 48.85,
            "longitude": 2.35,
            "from": start,
            "to": end,
        }
        expected_num_queries = 1  # product
        expected_num_queries += 1  # stocks
        expected_num_queries += 1  # screenings
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/movie/calendar", params=params)
            assert response.status_code == 200

        today = date_utils.default_timezone_to_local_datetime(start, "UTC").date()
        tomorrow = date_utils.default_timezone_to_local_datetime(end, "UTC").date()
        today_screenings = [e["screenings"] for e in response.json["calendar"] if e["date"] == today.isoformat()][0]
        assert today_screenings == []
        tomorrow_screenings = [e["screenings"] for e in response.json["calendar"] if e["date"] == tomorrow.isoformat()][
            0
        ]
        assert tomorrow_screenings == []

    def test_screenings_are_sorted_by_distance_then_screening_day(self, client):
        product = offers_factories.ProductFactory(extraData={"allocineId": 12345})
        timezone = "Europe/Paris"
        closest_address_for_today = AddressFactory(latitude=48.85, longitude=2.35, timezone=timezone)
        closest_address_for_tomorrow = AddressFactory(latitude=48.85, longitude=2.35, timezone=timezone)
        furthest_address_for_today = AddressFactory(latitude=48.84, longitude=2.35, timezone=timezone)
        furthest_address_for_tomorrow = AddressFactory(latitude=48.84, longitude=2.35, timezone=timezone)
        today_closest_stock = offers_factories.EventStockFactory(
            offer__product=product,
            offer__venue__offererAddress__address=closest_address_for_today,
            beginningDatetime=date_utils.get_naive_utc_now() + timedelta(minutes=10),
        )
        today_furthest_stock = offers_factories.EventStockFactory(
            offer__product=product,
            offer__venue__offererAddress__address=furthest_address_for_today,
            beginningDatetime=date_utils.get_naive_utc_now() + timedelta(minutes=10),
        )
        tomorrow_closest_stock = offers_factories.EventStockFactory(
            offer__product=product,
            offer__venue__offererAddress__address=closest_address_for_tomorrow,
            beginningDatetime=(date_utils.get_naive_utc_now() + timedelta(days=1)).replace(hour=12),
        )
        tomorrow_furthest_stock = offers_factories.EventStockFactory(
            offer__product=product,
            offer__venue__offererAddress__address=furthest_address_for_tomorrow,
            beginningDatetime=(date_utils.get_naive_utc_now() + timedelta(days=1)).replace(hour=12),
        )

        start = date_utils.get_naive_utc_now().replace(hour=0, minute=0, second=0, microsecond=0)
        end = (date_utils.get_naive_utc_now() + timedelta(days=1)).replace(
            hour=23, minute=59, second=59, microsecond=999
        )
        params = {
            "allocineId": "12345",
            "latitude": 48.85,
            "longitude": 2.35,
            "from": start,
            "to": end,
        }
        expected_num_queries = 1  # product
        expected_num_queries += 1  # stocks
        expected_num_queries += 1  # screenings
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/movie/calendar", params=params)
            assert response.status_code == 200

        today = date_utils.default_timezone_to_local_datetime(start, timezone).date()
        tomorrow = date_utils.default_timezone_to_local_datetime(
            (date_utils.get_naive_utc_now() + timedelta(days=1)).replace(hour=12), timezone
        ).date()
        today_screenings = [e["screenings"] for e in response.json["calendar"] if e["date"] == today.isoformat()][0]
        tomorrow_screenings = [e["screenings"] for e in response.json["calendar"] if e["date"] == tomorrow.isoformat()][
            0
        ]
        assert today_screenings[0]["dayScreenings"][0]["stockId"] == today_closest_stock.id
        assert today_screenings[1]["dayScreenings"][0]["stockId"] == today_furthest_stock.id
        assert today_screenings[2]["nextScreening"]["stockId"] == tomorrow_closest_stock.id
        assert today_screenings[3]["nextScreening"]["stockId"] == tomorrow_furthest_stock.id
        assert tomorrow_screenings[0]["dayScreenings"][0]["stockId"] == tomorrow_closest_stock.id
        assert tomorrow_screenings[1]["dayScreenings"][0]["stockId"] == tomorrow_furthest_stock.id
        assert tomorrow_screenings[2]["nextScreening"]["stockId"] == today_closest_stock.id
        assert tomorrow_screenings[3]["nextScreening"]["stockId"] == today_furthest_stock.id

    def test_venue_screenings_are_sorted_by_beginning_datetime(self, client):
        product = offers_factories.ProductFactory(extraData={"allocineId": 12345})
        address = AddressFactory(latitude=48.85, longitude=2.35)
        venue = offerers_factories.VenueFactory(offererAddress__address=address)
        first_stock = offers_factories.EventStockFactory(
            offer__product=product,
            offer__venue=venue,
            beginningDatetime=date_utils.get_naive_utc_now() + timedelta(hours=1),
        )
        last_stock = offers_factories.EventStockFactory(
            offer__product=product,
            offer__venue=venue,
            beginningDatetime=date_utils.get_naive_utc_now() + timedelta(hours=2),
        )

        start = date_utils.get_naive_utc_now().replace(hour=0, minute=0, second=0, microsecond=0)
        end = (date_utils.get_naive_utc_now() + timedelta(days=1)).replace(
            hour=23, minute=59, second=59, microsecond=999
        )
        params = {
            "allocineId": "12345",
            "latitude": 48.85,
            "longitude": 2.35,
            "from": start,
            "to": end,
        }
        expected_num_queries = 1  # product
        expected_num_queries += 1  # stocks
        expected_num_queries += 1  # screenings
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/movie/calendar", params=params)
            assert response.status_code == 200

        today = date_utils.default_timezone_to_local_datetime(start, address.timezone).date()
        today_screenings = [e["screenings"] for e in response.json["calendar"] if e["date"] == today.isoformat()][0]
        assert today_screenings[0]["dayScreenings"][0]["stockId"] == first_stock.id
        assert today_screenings[0]["dayScreenings"][1]["stockId"] == last_stock.id

    def test_next_screening_is_closest_from_today(self, client):
        product = offers_factories.ProductFactory(extraData={"allocineId": 12345})
        address = AddressFactory(latitude=48.85, longitude=2.35)
        venue = offerers_factories.VenueFactory(offererAddress__address=address)
        closest_stock_from_tomorrow = offers_factories.EventStockFactory(
            offer__product=product,
            offer__venue=venue,
            beginningDatetime=date_utils.get_naive_utc_now() + timedelta(hours=2),
        )
        _furthest_stock_from_tomorrow = offers_factories.EventStockFactory(
            offer__product=product,
            offer__venue=venue,
            beginningDatetime=date_utils.get_naive_utc_now() + timedelta(days=3, hours=1),
        )

        start = date_utils.get_naive_utc_now().replace(hour=0, minute=0, second=0, microsecond=0)
        in_three_days = (date_utils.get_naive_utc_now() + timedelta(days=3)).replace(hour=12)
        params = {
            "allocineId": "12345",
            "latitude": 48.85,
            "longitude": 2.35,
            "from": start,
            "to": in_three_days,
        }
        expected_num_queries = 1  # product
        expected_num_queries += 1  # stocks
        expected_num_queries += 1  # screenings
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/movie/calendar", params=params)
            assert response.status_code == 200

        tomorrow = date_utils.default_timezone_to_local_datetime(
            start + timedelta(days=1, hours=12), address.timezone
        ).date()
        tomorrow_screenings = [e["screenings"] for e in response.json["calendar"] if e["date"] == tomorrow.isoformat()][
            0
        ]
        assert tomorrow_screenings[0]["nextScreening"]["stockId"] == closest_stock_from_tomorrow.id

    def test_screenings_are_within_around_radius(self, client):
        product = offers_factories.ProductFactory(extraData={"allocineId": 12345})
        timezone = "Europe/Paris"
        closest_address = AddressFactory(latitude=48.8, longitude=2.35, timezone=timezone)
        furthest_address = AddressFactory(latitude=48.0, longitude=2.35, timezone=timezone)
        _closest_stock = offers_factories.EventStockFactory(
            offer__product=product,
            offer__venue__offererAddress__address=closest_address,
            beginningDatetime=date_utils.get_naive_utc_now() + timedelta(minutes=10),
        )
        _furthest_stock = offers_factories.EventStockFactory(
            offer__product=product,
            offer__venue__offererAddress__address=furthest_address,
            beginningDatetime=date_utils.get_naive_utc_now() + timedelta(minutes=10),
        )

        start_of_day = date_utils.get_naive_utc_now().replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = date_utils.get_naive_utc_now().replace(hour=23, minute=59, second=59, microsecond=999)
        params = {
            "allocineId": "12345",
            "latitude": 48.8,
            "longitude": 2.35,
            "aroundRadius": 10_000,
            "from": start_of_day,
            "to": end_of_day,
        }
        expected_num_queries = 1  # product
        expected_num_queries += 1  # stocks
        expected_num_queries += 1  # screenings
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/movie/calendar", params=params)
            assert response.status_code == 200

        today = date_utils.default_timezone_to_local_datetime(
            date_utils.get_naive_utc_now().replace(hour=12), timezone
        ).date()
        today_screenings = [e["screenings"] for e in response.json["calendar"] if e["date"] == today.isoformat()][0]
        assert len(today_screenings) == 1
        assert len(today_screenings[0]["dayScreenings"]) == 1
        assert today_screenings[0]["distance"] < 10_000

    def test_sold_out_screening(self, client):
        product = offers_factories.ProductFactory(extraData={"allocineId": 12345})
        timezone = "Europe/Paris"
        address = AddressFactory(latitude=48.85, longitude=2.35, timezone=timezone)
        _sold_out_stock = offers_factories.EventStockFactory(
            quantity=1,
            dnBookedQuantity=1,
            offer__product=product,
            offer__venue__offererAddress__address=address,
            beginningDatetime=date_utils.get_naive_utc_now() + timedelta(minutes=10),
        )
        start = date_utils.get_naive_utc_now().replace(hour=0, minute=0, second=0, microsecond=0)
        end = (date_utils.get_naive_utc_now() + timedelta(days=1)).replace(hour=12)
        params = {
            "allocineId": "12345",
            "latitude": 48.85,
            "longitude": 2.35,
            "from": start,
            "to": end,
        }
        expected_num_queries = 1  # product
        expected_num_queries += 1  # stocks
        expected_num_queries += 1  # screenings
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/movie/calendar", params=params)
            assert response.status_code == 200

        calendar = response.json["calendar"]
        today = date_utils.default_timezone_to_local_datetime(
            date_utils.get_naive_utc_now().replace(hour=12), timezone
        ).date()
        today_screenings = [e["screenings"] for e in calendar if e["date"] == today.isoformat()][0]
        assert today_screenings[0]["dayScreenings"][0]["bookability"] == "STOCK_IS_SOLD_OUT"
        assert today_screenings[0]["nextScreening"]["bookability"] == "STOCK_IS_SOLD_OUT"

    @pytest.mark.features(DISABLE_BOOST_EXTERNAL_BOOKINGS=True)
    def test_disabled_booking(self, client):
        product = offers_factories.ProductFactory(extraData={"allocineId": 12345})
        disabled_provider = get_provider_by_local_class("BoostStocks")
        address = AddressFactory(latitude=48.85, longitude=2.35)
        _stock = offers_factories.EventStockFactory(
            offer__lastProvider=disabled_provider,
            offer__product=product,
            offer__venue__offererAddress__address=address,
            beginningDatetime=date_utils.get_naive_utc_now() + timedelta(minutes=10),
        )
        start = date_utils.get_naive_utc_now().replace(hour=0, minute=0, second=0, microsecond=0)
        end = (date_utils.get_naive_utc_now() + timedelta(days=1)).replace(hour=12)
        params = {
            "allocineId": "12345",
            "latitude": 48.85,
            "longitude": 2.35,
            "from": start,
            "to": end,
        }
        expected_num_queries = 1  # product
        expected_num_queries += 1  # stocks
        expected_num_queries += 1  # screenings
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/movie/calendar", params=params)
            assert response.status_code == 200

        calendar = response.json["calendar"]
        today = date_utils.default_timezone_to_local_datetime(
            date_utils.get_naive_utc_now().replace(hour=12), address.timezone
        ).date()
        today_screenings = [e["screenings"] for e in calendar if e["date"] == today.isoformat()][0]
        assert today_screenings[0]["dayScreenings"][0]["bookability"] == "STOCK_BOOKING_IS_DISABLED"
        assert today_screenings[0]["nextScreening"]["bookability"] == "STOCK_BOOKING_IS_DISABLED"

    @pytest.mark.parametrize(
        "field_name,value",
        [
            ("allocineId", "https://malware.0rg"),
            ("allocineId", "&'@09839"),
            ("visa", "https://malware.0rg"),
            ("visa", "&'@09839"),
        ],
    )
    def test_invalid_query_params(self, client, field_name, value):
        params = {
            "latitude": 48.85,
            "longitude": 2.35,
            "from": date_utils.get_naive_utc_now(),
            "to": date_utils.get_naive_utc_now() + timedelta(days=1),
            field_name: value,
        }
        response = client.get("/native/v1/movie/calendar", params=params)
        assert response.status_code == 400
        assert list(response.json) == [field_name]

    @pytest.mark.parametrize(
        "field_name,value",
        [
            ("allocineId", "09839"),
            ("visa", "abc1234def"),
            ("visa", "abc"),
            ("visa", "1234"),
        ],
    )
    def test_valid_query_params(self, client, field_name, value):
        params = {
            "latitude": 48.85,
            "longitude": 2.35,
            "from": date_utils.get_naive_utc_now(),
            "to": date_utils.get_naive_utc_now() + timedelta(days=1),
            field_name: value,
        }
        response = client.get("/native/v1/movie/calendar", params=params)
        assert response.status_code == 404

    def test_timezone_aware_query_params(self, client):
        product = offers_factories.ProductFactory(extraData={"allocineId": 12345}, durationMinutes=113)
        address = AddressFactory(latitude=48.85, longitude=2.35, timezone="Europe/Paris")
        start_date = datetime.now(UTC)
        end_date = start_date + timedelta(days=1)
        tz_naive_beginning_datetime = date_utils.get_naive_utc_now() + timedelta(hours=1)
        tz_aware_beginning_datetime = date_utils.default_timezone_to_local_datetime(
            tz_naive_beginning_datetime, address.timezone
        )
        stock = offers_factories.EventStockFactory(
            offer__product=product,
            beginningDatetime=tz_naive_beginning_datetime,
            offer__venue__offererAddress__address=address,
        )
        params = {
            "allocineId": "12345",
            "latitude": 48.85,
            "longitude": 2.35,
            "from": start_date.isoformat(),
            "to": end_date.isoformat(),
        }
        expected_num_queries = 1  # product
        expected_num_queries += 1  # stocks
        expected_num_queries += 1  # screenings
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/movie/calendar", params=params)
            assert response.status_code == 200

        calendar = response.json["calendar"]
        assert len(calendar) == 2
        start_date_day = date_utils.default_timezone_to_local_datetime(
            date_utils.get_naive_utc_now().replace(hour=12), address.timezone
        ).date()
        end_date_day = date_utils.default_timezone_to_local_datetime(
            (date_utils.get_naive_utc_now() + timedelta(days=1)).replace(hour=12), address.timezone
        ).date()

        assert [start_date_day.isoformat(), end_date_day.isoformat()] == [e["date"] for e in calendar]
        today_screenings = [e for e in calendar if e["date"] == start_date_day.isoformat()][0]["screenings"]
        assert len(today_screenings) == 1
        today_day_screenings = today_screenings[0]["dayScreenings"]
        assert len(today_day_screenings) == 1
        today_day_screening = today_day_screenings[0]
        assert today_day_screening["stockId"] == stock.id
        assert today_day_screening["beginningDatetime"] == tz_aware_beginning_datetime.isoformat()

        tomorrow_screenings = [e for e in calendar if e["date"] == end_date_day.isoformat()][0]["screenings"]
        assert len(tomorrow_screenings) == 1
        tomorrow_day_screenings = tomorrow_screenings[0]["dayScreenings"]
        assert len(tomorrow_day_screenings) == 0

    def test_filter_screenings_from_the_past(self, client):
        product = offers_factories.ProductFactory(extraData={"allocineId": 12345}, durationMinutes=113)
        address = AddressFactory(latitude=48.85, longitude=2.35, timezone="Europe/Paris")
        start_date = datetime.now(UTC) - timedelta(days=1)
        end_date = datetime.now(UTC) + timedelta(days=1)

        offers_factories.EventStockFactory(  # past stock
            offer__product=product,
            beginningDatetime=date_utils.get_naive_utc_now() - timedelta(days=1) + timedelta(hours=1),
            offer__venue__offererAddress__address=address,
        )

        future_stock = offers_factories.EventStockFactory(
            offer__product=product,
            beginningDatetime=date_utils.get_naive_utc_now() + timedelta(hours=1),
            offer__venue__offererAddress__address=address,
        )

        params = {
            "allocineId": "12345",
            "latitude": 48.85,
            "longitude": 2.35,
            "from": start_date.isoformat(),
            "to": end_date.isoformat(),
        }
        expected_num_queries = 1  # product
        expected_num_queries += 1  # stocks
        expected_num_queries += 1  # screenings
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/movie/calendar", params=params)
            assert response.status_code == 200, response.json

        calendar = response.json["calendar"]
        assert len(calendar) == 2
        today = date_utils.default_timezone_to_local_datetime(
            date_utils.get_naive_utc_now().replace(hour=12), address.timezone
        ).date()
        tomorrow = date_utils.default_timezone_to_local_datetime(
            (date_utils.get_naive_utc_now() + timedelta(days=1)).replace(hour=12), address.timezone
        ).date()
        assert [today.isoformat(), tomorrow.isoformat()] == [e["date"] for e in calendar]

        today_screenings = [e for e in calendar if e["date"] == today.isoformat()][0]["screenings"]
        assert len(today_screenings) == 1
        today_day_screenings = today_screenings[0]["dayScreenings"]
        assert len(today_day_screenings) == 1
        today_day_screening = today_day_screenings[0]
        assert today_day_screening["stockId"] == future_stock.id

        tomorrow_screenings = [e for e in calendar if e["date"] == tomorrow.isoformat()][0]["screenings"]
        assert len(tomorrow_screenings) == 1
        tomorrow_day_screenings = tomorrow_screenings[0]["dayScreenings"]
        assert len(tomorrow_day_screenings) == 0


class MovieCalendarForUserTest:
    def test_get_movie_shows_for_user(self, client):
        user = users_factories.BeneficiaryFactory()
        product = offers_factories.ProductFactory(extraData={"allocineId": 12345})
        address = AddressFactory(latitude=48.85, longitude=2.35)
        tz_naive_beginning_datetime = date_utils.get_naive_utc_now() + timedelta(hours=1)
        tz_aware_beginning_datetime = date_utils.default_timezone_to_local_datetime(
            tz_naive_beginning_datetime, address.timezone
        )
        stock = offers_factories.EventStockFactory(
            offer__product=product,
            offer__venue__offererAddress__address=address,
            beginningDatetime=tz_naive_beginning_datetime,
        )
        start = datetime.now(UTC)
        end = start + timedelta(days=1)
        params = {
            "allocineId": "12345",
            "latitude": 48.85,
            "longitude": 2.35,
            "from": start,
            "to": end,
        }
        expected_num_queries = 1  # user
        expected_num_queries += 1  # product
        expected_num_queries += 1  # product stocks
        expected_num_queries += 1  # screenings
        expected_num_queries += 1  # deposit
        expected_num_queries += 1  # user bookings
        client.with_token(user)
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/movie/calendar/me", params=params)
            assert response.status_code == 200

        today = date_utils.default_timezone_to_local_datetime(date_utils.get_naive_utc_now(), address.timezone).date()
        tomorrow = date_utils.default_timezone_to_local_datetime(
            date_utils.get_naive_utc_now() + timedelta(days=1), address.timezone
        ).date()
        assert response.json == {
            "calendar": [
                {
                    "date": today.isoformat(),
                    "screenings": [
                        {
                            "address": f"{address.street}, {address.postalCode} {address.city}",
                            "distance": 0.0,
                            "dayScreenings": [
                                {
                                    "beginningDatetime": tz_aware_beginning_datetime.isoformat(),
                                    "bookability": "BOOKABLE",
                                    "features": [],
                                    "price": float(stock.price),
                                    "stockId": stock.id,
                                }
                            ],
                            "label": stock.offer.venue.publicName,
                            "nextScreening": {
                                "beginningDatetime": tz_aware_beginning_datetime.isoformat(),
                                "bookability": "BOOKABLE",
                                "features": [],
                                "price": float(stock.price),
                                "stockId": stock.id,
                            },
                            "offerId": stock.offer.id,
                            "thumbUrl": None,
                            "venueId": stock.offer.venue.id,
                        },
                    ],
                },
                {
                    "date": tomorrow.isoformat(),
                    "screenings": [
                        {
                            "address": f"{address.street}, {address.postalCode} {address.city}",
                            "distance": 0.0,
                            "dayScreenings": [],
                            "label": stock.offer.venue.publicName,
                            "nextScreening": {
                                "beginningDatetime": tz_aware_beginning_datetime.isoformat(),
                                "bookability": "BOOKABLE",
                                "features": [],
                                "price": 10.1,
                                "stockId": stock.id,
                            },
                            "offerId": stock.offer.id,
                            "thumbUrl": None,
                            "venueId": stock.offer.venue.id,
                        },
                    ],
                },
            ],
        }

    def test_when_stock_is_sold_out(self, client):
        user = users_factories.UserFactory(age=100)
        product = offers_factories.ProductFactory(extraData={"allocineId": 12345})
        address = AddressFactory(latitude=48.85, longitude=2.35)
        start = date_utils.get_naive_utc_now().replace(hour=0, minute=0, second=0, microsecond=0)
        end = date_utils.get_naive_utc_now().replace(hour=23, minute=59, second=59, microsecond=999)
        _stock = offers_factories.EventStockFactory(
            offer__product=product,
            offer__venue__offererAddress__address=address,
            offer__venue__offererAddress__label="Cinéma Parisien",
            beginningDatetime=date_utils.get_naive_utc_now() + timedelta(minutes=10),
            quantity=0,
        )
        params = {
            "allocineId": "12345",
            "latitude": 48.85,
            "longitude": 2.35,
            "from": start,
            "to": end,
        }
        expected_num_queries = 1  # user
        expected_num_queries += 1  # product
        expected_num_queries += 1  # product stocks
        expected_num_queries += 1  # screenings
        expected_num_queries += 1  # deposit
        client.with_token(user)
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/movie/calendar/me", params=params)
            assert response.status_code == 200

        today = date_utils.default_timezone_to_local_datetime(date_utils.get_naive_utc_now(), address.timezone).date()
        today_screenings = [e["screenings"] for e in response.json["calendar"] if e["date"] == today.isoformat()][0]
        assert today_screenings[0]["dayScreenings"][0]["bookability"] == "STOCK_IS_SOLD_OUT"

    @pytest.mark.features(DISABLE_BOOST_EXTERNAL_BOOKINGS=True)
    def test_when_offer_booking_is_disabled(self, client):
        user = users_factories.UserFactory(age=100)
        product = offers_factories.ProductFactory(extraData={"allocineId": 12345})
        disabled_provider = get_provider_by_local_class("BoostStocks")
        address = AddressFactory(latitude=48.85, longitude=2.35)
        _stock = offers_factories.EventStockFactory(
            offer__lastProvider=disabled_provider,
            offer__product=product,
            offer__venue__offererAddress__address=address,
            offer__venue__offererAddress__label="Cinéma Parisien",
            beginningDatetime=date_utils.get_naive_utc_now() + timedelta(minutes=10),
            quantity=0,
        )
        start = date_utils.get_naive_utc_now().replace(hour=0, minute=0, second=0, microsecond=0)
        end = date_utils.get_naive_utc_now().replace(hour=23, minute=59, second=59, microsecond=999)
        params = {
            "allocineId": "12345",
            "latitude": 48.85,
            "longitude": 2.35,
            "from": start,
            "to": end,
        }
        expected_num_queries = 1  # user
        expected_num_queries += 1  # product
        expected_num_queries += 1  # product stocks
        expected_num_queries += 1  # screenings
        expected_num_queries += 1  # deposit
        client.with_token(user)
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/movie/calendar/me", params=params)
            assert response.status_code == 200

        today = date_utils.default_timezone_to_local_datetime(date_utils.get_naive_utc_now(), address.timezone).date()
        today_screenings = [e["screenings"] for e in response.json["calendar"] if e["date"] == today.isoformat()][0]
        assert today_screenings[0]["dayScreenings"][0]["bookability"] == "STOCK_BOOKING_IS_DISABLED"

    def test_when_user_cannot_book(self, client):
        user = users_factories.UserFactory(age=100)
        product = offers_factories.ProductFactory(extraData={"allocineId": 12345})
        address = AddressFactory(latitude=48.85, longitude=2.35)
        _stock = offers_factories.EventStockFactory(
            offer__product=product,
            offer__venue__offererAddress__address=address,
            offer__venue__offererAddress__label="Cinéma Parisien",
            beginningDatetime=date_utils.get_naive_utc_now() + timedelta(minutes=10),
        )
        start = date_utils.get_naive_utc_now().replace(hour=0, minute=0, second=0, microsecond=0)
        end = date_utils.get_naive_utc_now().replace(hour=23, minute=59, second=59, microsecond=999)
        params = {
            "allocineId": "12345",
            "latitude": 48.85,
            "longitude": 2.35,
            "from": start,
            "to": end,
        }
        expected_num_queries = 1  # user
        expected_num_queries += 1  # product
        expected_num_queries += 1  # product stocks
        expected_num_queries += 1  # screenings
        expected_num_queries += 1  # deposit
        client.with_token(user)
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/movie/calendar/me", params=params)
            assert response.status_code == 200

        today = date_utils.default_timezone_to_local_datetime(date_utils.get_naive_utc_now(), address.timezone).date()
        today_screenings = [e["screenings"] for e in response.json["calendar"] if e["date"] == today.isoformat()][0]
        assert today_screenings[0]["dayScreenings"][0]["bookability"] == "USER_CANNOT_BOOK"

    def test_when_user_has_not_enough_credit(self, client):
        user = users_factories.BeneficiaryFactory()
        product = offers_factories.ProductFactory(extraData={"allocineId": 12345})
        address = AddressFactory(latitude=48.85, longitude=2.35)
        _stock = offers_factories.EventStockFactory(
            price=1000,
            offer__product=product,
            offer__venue__offererAddress__address=address,
            offer__venue__offererAddress__label="Cinéma Parisien",
            beginningDatetime=date_utils.get_naive_utc_now() + timedelta(minutes=10),
        )
        start = date_utils.get_naive_utc_now().replace(hour=0, minute=0, second=0, microsecond=0)
        end = date_utils.get_naive_utc_now().replace(hour=23, minute=59, second=59, microsecond=999)
        params = {
            "allocineId": "12345",
            "latitude": 48.85,
            "longitude": 2.35,
            "from": start,
            "to": end,
        }
        expected_num_queries = 1  # user
        expected_num_queries += 1  # product
        expected_num_queries += 1  # product stocks
        expected_num_queries += 1  # screenings
        expected_num_queries += 1  # deposit
        expected_num_queries += 1  # user bookings
        client.with_token(user)
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/movie/calendar/me", params=params)
            assert response.status_code == 200

        today = date_utils.default_timezone_to_local_datetime(date_utils.get_naive_utc_now(), address.timezone).date()
        today_screenings = [e["screenings"] for e in response.json["calendar"] if e["date"] == today.isoformat()][0]
        assert today_screenings[0]["dayScreenings"][0]["bookability"] == "USER_HAS_INSUFFICIENT_CREDIT"

    def test_when_user_has_already_booked_offer(self, client):
        user = users_factories.BeneficiaryFactory()
        product = offers_factories.ProductFactory(extraData={"allocineId": 12345})
        address = AddressFactory(latitude=48.85, longitude=2.35)
        stock = offers_factories.EventStockFactory(
            offer__product=product,
            offer__venue__offererAddress__address=address,
            offer__venue__offererAddress__label="Cinéma Parisien",
            beginningDatetime=date_utils.get_naive_utc_now() + timedelta(minutes=10),
        )
        offers_factories.StockFactory(offer=stock.offer)
        _user_booking = BookingFactory(user=user, stock=stock)
        start = date_utils.get_naive_utc_now().replace(hour=0, minute=0, second=0, microsecond=0)
        end = date_utils.get_naive_utc_now().replace(hour=23, minute=59, second=59, microsecond=999)
        params = {
            "allocineId": "12345",
            "latitude": 48.85,
            "longitude": 2.35,
            "from": start,
            "to": end,
        }
        expected_num_queries = 1  # user
        expected_num_queries += 1  # product
        expected_num_queries += 1  # product stocks
        expected_num_queries += 1  # screenings
        expected_num_queries += 1  # deposit
        expected_num_queries += 1  # user bookings
        client.with_token(user)
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/movie/calendar/me", params=params)
            assert response.status_code == 200

        today = date_utils.default_timezone_to_local_datetime(date_utils.get_naive_utc_now(), address.timezone).date()
        today_screenings = [e["screenings"] for e in response.json["calendar"] if e["date"] == today.isoformat()][0]
        assert today_screenings[0]["dayScreenings"][0]["bookability"] == "USER_HAS_ALREADY_BOOKED_OFFER"

    def test_when_user_has_already_booked_related_offer(self, client):
        user = users_factories.BeneficiaryFactory()
        product = offers_factories.ProductFactory(extraData={"allocineId": 12345})
        address = AddressFactory(latitude=48.85, longitude=2.35)
        stock = offers_factories.EventStockFactory(
            offer__product=product,
            offer__venue__offererAddress__address=address,
            offer__venue__offererAddress__label="Cinéma Parisien",
            beginningDatetime=date_utils.get_naive_utc_now() + timedelta(minutes=10),
        )
        another_stock = offers_factories.StockFactory(offer=stock.offer)
        _user_booking = BookingFactory(user=user, stock=another_stock)
        start = date_utils.get_naive_utc_now().replace(hour=0, minute=0, second=0, microsecond=0)
        end = date_utils.get_naive_utc_now().replace(hour=23, minute=59, second=59, microsecond=999)
        params = {
            "allocineId": "12345",
            "latitude": 48.85,
            "longitude": 2.35,
            "from": start,
            "to": end,
        }
        expected_num_queries = 1  # user
        expected_num_queries += 1  # product
        expected_num_queries += 1  # product stocks
        expected_num_queries += 1  # screenings
        expected_num_queries += 1  # deposit
        expected_num_queries += 1  # user bookings
        client.with_token(user)
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/movie/calendar/me", params=params)
            assert response.status_code == 200

        today = date_utils.default_timezone_to_local_datetime(date_utils.get_naive_utc_now(), address.timezone).date()
        today_screenings = [e["screenings"] for e in response.json["calendar"] if e["date"] == today.isoformat()][0]
        assert today_screenings[0]["dayScreenings"][0]["bookability"] == "USER_HAS_ALREADY_BOOKED_RELATED_OFFER"

    def test_bookability_finish_subscription_required(self, client):
        user = users_factories.UserFactory(dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(years=18))
        product = offers_factories.ProductFactory(extraData={"allocineId": 12345})
        address = AddressFactory(latitude=48.85, longitude=2.35)
        offers_factories.EventStockFactory(
            offer__product=product,
            offer__venue__offererAddress__address=address,
            beginningDatetime=date_utils.get_naive_utc_now() + timedelta(minutes=10),
        )
        start = date_utils.get_naive_utc_now().replace(hour=0, minute=0, second=0, microsecond=0)
        end = date_utils.get_naive_utc_now().replace(hour=23, minute=59, second=59, microsecond=999)
        expected_num_queries = 1  # user
        expected_num_queries += 1  # product
        expected_num_queries += 1  # product stocks
        expected_num_queries += 1  # screenings
        expected_num_queries += 1  # deposit
        expected_num_queries += 1  # beneficiary_fraud_review
        expected_num_queries += 1  # beneficiary_fraud_check
        client.with_token(user)
        with assert_num_queries(expected_num_queries):
            response = client.get(
                "/native/v1/movie/calendar/me",
                params={
                    "allocineId": "12345",
                    "latitude": 48.85,
                    "longitude": 2.35,
                    "from": start,
                    "to": end,
                },
            )
            assert response.status_code == 200

        today = date_utils.default_timezone_to_local_datetime(date_utils.get_naive_utc_now(), address.timezone).date()
        today_screenings = [e["screenings"] for e in response.json["calendar"] if e["date"] == today.isoformat()][0]
        assert today_screenings[0]["dayScreenings"][0]["bookability"] == "FINISH_SUBSCRIPTION_REQUIRED"

    def test_bookability_user_application_still_processing(self, client):
        user = users_factories.UserFactory(
            dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(years=18),
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            status=subscription_models.FraudCheckStatus.OK,
            type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
            user=user,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            status=subscription_models.FraudCheckStatus.PENDING,
            type=subscription_models.FraudCheckType.DMS,
            user=user,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            status=subscription_models.FraudCheckStatus.OK,
            type=subscription_models.FraudCheckType.HONOR_STATEMENT,
            user=user,
        )

        product = offers_factories.ProductFactory(extraData={"allocineId": 12345})
        address = AddressFactory(latitude=48.85, longitude=2.35)
        offers_factories.EventStockFactory(
            offer__product=product,
            offer__venue__offererAddress__address=address,
            beginningDatetime=date_utils.get_naive_utc_now() + timedelta(minutes=10),
        )
        start = date_utils.get_naive_utc_now().replace(hour=0, minute=0, second=0, microsecond=0)
        end = date_utils.get_naive_utc_now().replace(hour=23, minute=59, second=59, microsecond=999)
        expected_num_queries = 1  # user
        expected_num_queries += 1  # product
        expected_num_queries += 1  # product stocks
        expected_num_queries += 1  # screenings
        expected_num_queries += 1  # deposit
        expected_num_queries += 1  # beneficiary_fraud_review
        expected_num_queries += 1  # beneficiary_fraud_check
        expected_num_queries += 1  # action_history
        client.with_token(user)
        with assert_num_queries(expected_num_queries):
            response = client.get(
                "/native/v1/movie/calendar/me",
                params={
                    "allocineId": "12345",
                    "latitude": 48.85,
                    "longitude": 2.35,
                    "from": start,
                    "to": end,
                },
            )
            assert response.status_code == 200

        today = date_utils.default_timezone_to_local_datetime(date_utils.get_naive_utc_now(), address.timezone).date()
        today_screenings = [e["screenings"] for e in response.json["calendar"] if e["date"] == today.isoformat()][0]
        assert today_screenings[0]["dayScreenings"][0]["bookability"] == "USER_APPLICATION_STILL_PROCESSING"

    def test_bookability_user_application_has_error(self, client):
        user = users_factories.UserFactory(
            dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(years=18),
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
            status=subscription_models.FraudCheckStatus.OK,
            user=user,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            status=subscription_models.FraudCheckStatus.KO,
            reasonCodes=[subscription_models.FraudReasonCode.INVALID_ID_PIECE_NUMBER],
            type=subscription_models.FraudCheckType.UBBLE,
            user=user,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            status=subscription_models.FraudCheckStatus.OK,
            type=subscription_models.FraudCheckType.HONOR_STATEMENT,
            user=user,
        )

        product = offers_factories.ProductFactory(extraData={"allocineId": 12345})
        address = AddressFactory(latitude=48.85, longitude=2.35)
        offers_factories.EventStockFactory(
            offer__product=product,
            offer__venue__offererAddress__address=address,
            beginningDatetime=date_utils.get_naive_utc_now() + timedelta(minutes=10),
        )
        start = date_utils.get_naive_utc_now().replace(hour=0, minute=0, second=0, microsecond=0)
        end = date_utils.get_naive_utc_now().replace(hour=23, minute=59, second=59, microsecond=999)
        expected_num_queries = 1  # user
        expected_num_queries += 1  # product
        expected_num_queries += 1  # product stocks
        expected_num_queries += 1  # screenings
        expected_num_queries += 1  # deposit
        expected_num_queries += 1  # beneficiary_fraud_review
        expected_num_queries += 1  # beneficiary_fraud_check
        expected_num_queries += 1  # action_history
        client.with_token(user)
        with assert_num_queries(expected_num_queries):
            response = client.get(
                "/native/v1/movie/calendar/me",
                params={
                    "allocineId": "12345",
                    "latitude": 48.85,
                    "longitude": 2.35,
                    "from": start,
                    "to": end,
                },
            )
            assert response.status_code == 200

        today = date_utils.default_timezone_to_local_datetime(date_utils.get_naive_utc_now(), address.timezone).date()
        today_screenings = [e["screenings"] for e in response.json["calendar"] if e["date"] == today.isoformat()][0]
        assert today_screenings[0]["dayScreenings"][0]["bookability"] == "USER_HAS_APPLICATION_ERROR"

    @pytest.mark.parametrize(
        "field_name,value",
        [
            ("allocineId", "https://malware.0rg"),
            ("allocineId", "&'@09839"),
            ("allocineId", "abcdef"),
            ("visa", "https://malware.0rg"),
            ("visa", "&'@09839"),
        ],
    )
    def test_invalid_query_params(self, client, field_name, value):
        user = users_factories.UserFactory(
            dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(years=18),
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
        )
        params = {
            "latitude": 48.85,
            "longitude": 2.35,
            "from": date_utils.get_naive_utc_now(),
            "to": date_utils.get_naive_utc_now() + timedelta(days=1),
            field_name: value,
        }
        client.with_token(user)
        response = client.get("/native/v1/movie/calendar/me", params=params)
        assert response.status_code == 400
        assert list(response.json) == [field_name]

    @pytest.mark.parametrize(
        "field_name,value",
        [
            ("allocineId", "09839"),
            ("visa", "abc1234def"),
            ("visa", "abc"),
            ("visa", "1234"),
        ],
    )
    def test_valid_query_params(self, client, field_name, value):
        user = users_factories.UserFactory(
            dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(years=18),
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
        )
        params = {
            "latitude": 48.85,
            "longitude": 2.35,
            "from": date_utils.get_naive_utc_now(),
            "to": date_utils.get_naive_utc_now() + timedelta(days=1),
            field_name: value,
        }
        client.with_token(user)
        response = client.get("/native/v1/movie/calendar/me", params=params)
        assert response.status_code == 404


class VenueMovieCalendarTest:
    def test_get_venue_movie_calendar(self, client):
        product = offers_factories.ProductFactory(subcategoryId=subcategories.SEANCE_CINE.id, durationMinutes=116)
        address = AddressFactory(timezone="Europe/Paris")
        tz_naive_beginning_datetime = date_utils.get_naive_utc_now() + timedelta(minutes=10)
        tz_aware_beginning_datetime = date_utils.default_timezone_to_local_datetime(
            tz_naive_beginning_datetime, address.timezone
        )
        stock = offers_factories.EventStockFactory(
            offer__product=product,
            offer__venue__offererAddress__address=address,
            beginningDatetime=tz_naive_beginning_datetime,
        )
        start = date_utils.get_naive_utc_now().replace(hour=0, minute=0, second=0, microsecond=0)
        end = date_utils.get_naive_utc_now().replace(hour=23, minute=59, second=59, microsecond=999) + timedelta(
            minutes=10
        )
        venue_id = stock.offer.venue.id
        expected_num_queries = 1  # venue
        expected_num_queries += 1  # offers
        with assert_num_queries(expected_num_queries):
            response = client.get(f"/native/v1/venue/{venue_id}/movie/calendar", params={"from": start, "to": end})
            assert response.status_code == 200

        calendar = response.json["calendar"]
        today = date_utils.default_timezone_to_local_datetime(start.replace(hour=12), address.timezone).date()
        tomorrow = date_utils.default_timezone_to_local_datetime(end.replace(hour=12), address.timezone).date()
        assert calendar == [
            {
                "date": today.isoformat(),
                "screenings": [
                    {
                        "duration": 116,
                        "genres": [],
                        "last30DaysBookings": 0,
                        "movieName": stock.offer.name,
                        "offerId": stock.offer.id,
                        "thumbUrl": None,
                        "dayScreenings": [
                            {
                                "beginningDatetime": tz_aware_beginning_datetime.isoformat(),
                                "bookability": "AUTHENTICATION_REQUIRED",
                                "features": [],
                                "price": 10.1,
                                "stockId": stock.id,
                            }
                        ],
                        "nextScreening": {
                            "beginningDatetime": tz_aware_beginning_datetime.isoformat(),
                            "bookability": "AUTHENTICATION_REQUIRED",
                            "features": [],
                            "price": 10.1,
                            "stockId": stock.id,
                        },
                    }
                ],
            },
            {
                "date": tomorrow.isoformat(),
                "screenings": [
                    {
                        "duration": 116,
                        "genres": [],
                        "last30DaysBookings": 0,
                        "movieName": stock.offer.name,
                        "offerId": stock.offer.id,
                        "thumbUrl": None,
                        "dayScreenings": [],
                        "nextScreening": {
                            "beginningDatetime": tz_aware_beginning_datetime.isoformat(),
                            "bookability": "AUTHENTICATION_REQUIRED",
                            "features": [],
                            "price": 10.1,
                            "stockId": stock.id,
                        },
                    }
                ],
            },
        ]

    def test_day_screenings_are_sorted_by_last_30_days_bookings(self, client):
        tomorrow = date_utils.get_naive_utc_now() + timedelta(days=1)
        beginning_datetime = tomorrow.replace(hour=1)

        start = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
        least_booked_product = offers_factories.ProductFactory(
            last_30_days_booking=1, subcategoryId=subcategories.SEANCE_CINE.id
        )
        most_booked_product = offers_factories.ProductFactory(
            last_30_days_booking=2, subcategoryId=subcategories.SEANCE_CINE.id
        )
        venue = offerers_factories.VenueFactory()
        least_booked_stock = offers_factories.EventStockFactory(
            offer__product=least_booked_product, beginningDatetime=beginning_datetime, offer__venue=venue
        )
        most_booked_stock = offers_factories.EventStockFactory(
            offer__product=most_booked_product, beginningDatetime=beginning_datetime, offer__venue=venue
        )
        venue_id = venue.id
        expected_num_queries = 1  # venue
        expected_num_queries += 1  # offers
        with assert_num_queries(expected_num_queries):
            response = client.get(f"/native/v1/venue/{venue_id}/movie/calendar", params={"from": start, "to": end})
            assert response.status_code == 200

        movie_day = date_utils.default_timezone_to_local_datetime(
            beginning_datetime, venue.offererAddress.address.timezone
        ).date()
        movie_day_screenings = [
            e["screenings"] for e in response.json["calendar"] if e["date"] == movie_day.isoformat()
        ][0]
        assert movie_day_screenings[0]["dayScreenings"][0]["stockId"] == most_booked_stock.id
        assert movie_day_screenings[1]["dayScreenings"][0]["stockId"] == least_booked_stock.id

    def test_day_screenings_are_sorted_by_beginning_datetime(self, client):
        tomorrow = date_utils.get_naive_utc_now() + timedelta(days=1)
        before_screenings = tomorrow.replace(hour=0)
        first_beginning_datetime = tomorrow.replace(hour=1)
        last_beginning_datetime = tomorrow.replace(hour=2)
        after_screenings = tomorrow.replace(hour=3)
        product = offers_factories.ProductFactory(subcategoryId=subcategories.SEANCE_CINE.id)
        offer = offers_factories.OfferFactory(product=product)
        first_screened_stock = offers_factories.EventStockFactory(
            offer=offer, beginningDatetime=first_beginning_datetime
        )
        last_screened_stock = offers_factories.EventStockFactory(offer=offer, beginningDatetime=last_beginning_datetime)
        venue_id = offer.venue.id
        expected_num_queries = 1  # venue
        expected_num_queries += 1  # offers
        with assert_num_queries(expected_num_queries):
            response = client.get(
                f"/native/v1/venue/{venue_id}/movie/calendar",
                params={"from": before_screenings, "to": after_screenings},
            )
            assert response.status_code == 200

        day = date_utils.default_timezone_to_local_datetime(tomorrow, offer.offererAddress.address.timezone).date()
        tomorrow_screenings = [e["screenings"] for e in response.json["calendar"] if e["date"] == day.isoformat()][0]
        assert tomorrow_screenings[0]["dayScreenings"][0]["stockId"] == first_screened_stock.id
        assert tomorrow_screenings[0]["dayScreenings"][1]["stockId"] == last_screened_stock.id

    def test_next_screening_is_closest_requested_day(self, client):
        tomorrow = date_utils.get_naive_utc_now() + timedelta(days=1)
        in_two_days = date_utils.get_naive_utc_now() + timedelta(days=2)
        in_three_days = date_utils.get_naive_utc_now() + timedelta(days=3)
        in_four_days = date_utils.get_naive_utc_now() + timedelta(days=4)
        before_screenings = tomorrow.replace(hour=0)
        after_screenings = date_utils.get_naive_utc_now() + timedelta(days=5)
        product = offers_factories.ProductFactory(subcategoryId=subcategories.SEANCE_CINE.id)
        offer = offers_factories.OfferFactory(product=product)
        tomorrow_stock = offers_factories.EventStockFactory(offer=offer, beginningDatetime=tomorrow)
        in_four_days_stock = offers_factories.EventStockFactory(offer=offer, beginningDatetime=in_four_days)

        venue_id = offer.venue.id
        expected_num_queries = 1  # venue
        expected_num_queries += 1  # offers
        with assert_num_queries(expected_num_queries):
            response = client.get(
                f"/native/v1/venue/{venue_id}/movie/calendar",
                params={"from": before_screenings, "to": after_screenings},
            )
            assert response.status_code == 200

        calendar = response.json["calendar"]
        in_two_days_day = date_utils.default_timezone_to_local_datetime(
            in_two_days, offer.offererAddress.address.timezone
        ).date()
        in_three_days_day = date_utils.default_timezone_to_local_datetime(
            in_three_days, offer.offererAddress.address.timezone
        ).date()
        in_two_days_screenings = [e["screenings"] for e in calendar if e["date"] == in_two_days_day.isoformat()][0]
        in_three_days_screenings = [e["screenings"] for e in calendar if e["date"] == in_three_days_day.isoformat()][0]
        assert in_two_days_screenings[0]["nextScreening"]["stockId"] == tomorrow_stock.id
        assert in_three_days_screenings[0]["nextScreening"]["stockId"] == in_four_days_stock.id

    def test_calendar_is_empty_if_no_screenings_found(self, client):
        tomorrow = (date_utils.get_naive_utc_now() + timedelta(days=1)).date()
        in_two_days = (date_utils.get_naive_utc_now() + timedelta(days=2)).date()
        venue = offerers_factories.VenueFactory()

        venue_id = venue.id
        expected_num_queries = 1  # venue
        expected_num_queries += 1  # offers
        with assert_num_queries(expected_num_queries):
            response = client.get(
                f"/native/v1/venue/{venue_id}/movie/calendar", params={"from": tomorrow, "to": in_two_days}
            )
            assert response.status_code == 200

        assert response.json["calendar"] == [
            {"date": tomorrow.isoformat(), "screenings": []},
            {"date": in_two_days.isoformat(), "screenings": []},
        ]

    def test_sold_out_screening(self, client):
        product = offers_factories.ProductFactory(subcategoryId=subcategories.SEANCE_CINE.id, durationMinutes=116)
        stock = offers_factories.EventStockFactory(
            quantity=0, offer__product=product, beginningDatetime=date_utils.get_naive_utc_now() + timedelta(minutes=10)
        )
        start = date_utils.get_naive_utc_now().replace(hour=0, minute=0, second=0, microsecond=0)
        end = date_utils.get_naive_utc_now().replace(hour=23, minute=59, second=59, microsecond=999)
        venue_id = stock.offer.venue.id
        expected_num_queries = 1  # venue
        expected_num_queries += 1  # offers
        with assert_num_queries(expected_num_queries):
            response = client.get(f"/native/v1/venue/{venue_id}/movie/calendar", params={"from": start, "to": end})
            assert response.status_code == 200

        calendar = response.json["calendar"]
        today = date_utils.default_timezone_to_local_datetime(
            date_utils.get_naive_utc_now(), stock.offer.offererAddress.address.timezone
        ).date()
        today_screenings = [e["screenings"] for e in calendar if e["date"] == today.isoformat()][0]
        assert today_screenings[0]["dayScreenings"][0]["bookability"] == "STOCK_IS_SOLD_OUT"
        assert today_screenings[0]["nextScreening"]["bookability"] == "STOCK_IS_SOLD_OUT"

    @pytest.mark.features(DISABLE_BOOST_EXTERNAL_BOOKINGS=True)
    def test_disabled_booking(self, client):
        product = offers_factories.ProductFactory(subcategoryId=subcategories.SEANCE_CINE.id, durationMinutes=116)
        disabled_provider = get_provider_by_local_class("BoostStocks")
        stock = offers_factories.EventStockFactory(
            offer__lastProvider=disabled_provider,
            offer__product=product,
            beginningDatetime=date_utils.get_naive_utc_now() + timedelta(minutes=10),
        )
        start = date_utils.get_naive_utc_now().replace(hour=0, minute=0, second=0, microsecond=0)
        end = date_utils.get_naive_utc_now().replace(hour=23, minute=59, second=59, microsecond=999)
        venue_id = stock.offer.venue.id
        expected_num_queries = 1  # venue
        expected_num_queries += 1  # offers
        with assert_num_queries(expected_num_queries):
            response = client.get(f"/native/v1/venue/{venue_id}/movie/calendar", params={"from": start, "to": end})
            assert response.status_code == 200

        calendar = response.json["calendar"]
        today = date_utils.default_timezone_to_local_datetime(
            date_utils.get_naive_utc_now(), stock.offer.offererAddress.address.timezone
        ).date()
        today_screenings = [e["screenings"] for e in calendar if e["date"] == today.isoformat()][0]
        assert today_screenings[0]["dayScreenings"][0]["bookability"] == "STOCK_BOOKING_IS_DISABLED"
        assert today_screenings[0]["nextScreening"]["bookability"] == "STOCK_BOOKING_IS_DISABLED"

    def test_returns_404_if_venue_not_found(self, client):
        expected_num_queries = 1  # venue
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/venue/999999999/movie/calendar")
            assert response.status_code == 404

    def test_timezone_aware_query_params(self, client):
        product = offers_factories.ProductFactory(subcategoryId=subcategories.SEANCE_CINE.id, durationMinutes=116)
        address = AddressFactory(timezone="Europe/Paris")
        start_date = datetime.now(UTC)
        end_date = start_date + timedelta(days=1)
        stock = offers_factories.EventStockFactory(
            offer__product=product,
            beginningDatetime=date_utils.get_naive_utc_now() + timedelta(hours=1),
            offer__venue__offererAddress__address=address,
        )
        venue_id = stock.offer.venue.id
        expected_num_queries = 1  # venue
        expected_num_queries += 1  # offers
        with assert_num_queries(expected_num_queries):
            response = client.get(
                f"/native/v1/venue/{venue_id}/movie/calendar",
                params={"from": start_date.isoformat(), "to": end_date.isoformat()},
            )
            assert response.status_code == 200

        calendar = response.json["calendar"]
        assert len(calendar) == 2
        start_date_day = date_utils.default_timezone_to_local_datetime(start_date, address.timezone).date()
        end_date_day = date_utils.default_timezone_to_local_datetime(end_date, address.timezone).date()
        assert [start_date_day.isoformat(), end_date_day.isoformat()] == [e["date"] for e in calendar]
        today_screenings = [e for e in calendar if e["date"] == start_date.date().isoformat()][0]["screenings"]
        assert len(today_screenings) == 1
        today_day_screenings = today_screenings[0]["dayScreenings"]
        assert len(today_day_screenings) == 1
        today_day_screening = today_day_screenings[0]
        assert today_day_screening["stockId"] == stock.id

        tomorrow_screenings = [e for e in calendar if e["date"] == end_date.date().isoformat()][0]["screenings"]
        assert len(tomorrow_screenings) == 1
        tomorrow_day_screenings = tomorrow_screenings[0]["dayScreenings"]
        assert len(tomorrow_day_screenings) == 0

    def test_filter_screenings_from_the_past(self, client):
        product = offers_factories.ProductFactory(subcategoryId=subcategories.SEANCE_CINE.id, durationMinutes=113)
        address = AddressFactory(timezone="Europe/Paris")
        start_date = datetime.now(UTC) - timedelta(days=1)
        end_date = datetime.now(UTC) + timedelta(days=1)

        past_stock = offers_factories.EventStockFactory(
            offer__product=product,
            beginningDatetime=date_utils.get_naive_utc_now() - timedelta(days=1) + timedelta(hours=1),
            offer__venue__offererAddress__address=address,
        )

        future_stock = offers_factories.EventStockFactory(
            beginningDatetime=date_utils.get_naive_utc_now() + timedelta(hours=1),
            offer=past_stock.offer,
        )

        venue_id = past_stock.offer.venueId
        params = {
            "from": start_date.isoformat(),
            "to": end_date.isoformat(),
        }
        expected_num_queries = 1  # venue
        expected_num_queries += 1  # offers
        with assert_num_queries(expected_num_queries):
            response = client.get(f"/native/v1/venue/{venue_id}/movie/calendar", params=params)
            assert response.status_code == 200, response.json

        calendar = response.json["calendar"]
        assert len(calendar) == 2
        today_date = date_utils.default_timezone_to_local_datetime(
            date_utils.get_naive_utc_now(), address.timezone
        ).date()
        tomorrow_date = date_utils.default_timezone_to_local_datetime(end_date, address.timezone).date()
        assert [today_date.isoformat(), tomorrow_date.isoformat()] == [e["date"] for e in calendar]

        today_screenings = [e for e in calendar if e["date"] == today_date.isoformat()][0]["screenings"]
        assert len(today_screenings) == 1
        today_day_screenings = today_screenings[0]["dayScreenings"]
        assert len(today_day_screenings) == 1
        today_day_screening = today_day_screenings[0]
        assert today_day_screening["stockId"] == future_stock.id

        tomorrow_screenings = [e for e in calendar if e["date"] == tomorrow_date.isoformat()][0]["screenings"]
        assert len(tomorrow_screenings) == 1
        tomorrow_day_screenings = tomorrow_screenings[0]["dayScreenings"]
        assert len(tomorrow_day_screenings) == 0


class VenueMovieCalendarForUserTest:
    def test_get_venue_movie_calendar(self, client):
        user = users_factories.BeneficiaryFactory()
        product = offers_factories.ProductFactory(subcategoryId=subcategories.SEANCE_CINE.id, durationMinutes=116)
        address = AddressFactory(timezone="Europe/Paris")
        tz_naive_beginning_datetime = date_utils.get_naive_utc_now() + timedelta(minutes=10)
        tz_aware_beginning_datetime = date_utils.default_timezone_to_local_datetime(
            tz_naive_beginning_datetime, address.timezone
        )
        stock = offers_factories.EventStockFactory(
            offer__product=product,
            beginningDatetime=tz_naive_beginning_datetime,
            offer__venue__offererAddress__address=address,
        )
        start = date_utils.get_naive_utc_now().replace(hour=0, minute=0, second=0, microsecond=0)
        end = (start + timedelta(days=1)).replace(hour=12, minute=0, second=0, microsecond=0)
        venue_id = stock.offer.venue.id
        expected_num_queries = 1  # user
        expected_num_queries += 1  # venue
        expected_num_queries += 1  # offers
        expected_num_queries += 1  # deposit
        expected_num_queries += 1  # user bookings
        client.with_token(user)
        with assert_num_queries(expected_num_queries):
            response = client.get(f"/native/v1/venue/{venue_id}/movie/calendar/me", params={"from": start, "to": end})
            assert response.status_code == 200

        calendar = response.json["calendar"]
        today = date_utils.default_timezone_to_local_datetime(start, address.timezone).date()
        tomorrow = date_utils.default_timezone_to_local_datetime(end, address.timezone).date()
        assert calendar == [
            {
                "date": today.isoformat(),
                "screenings": [
                    {
                        "duration": 116,
                        "genres": [],
                        "last30DaysBookings": 0,
                        "movieName": stock.offer.name,
                        "offerId": stock.offer.id,
                        "thumbUrl": None,
                        "dayScreenings": [
                            {
                                "beginningDatetime": tz_aware_beginning_datetime.isoformat(),
                                "bookability": "BOOKABLE",
                                "features": [],
                                "price": 10.1,
                                "stockId": stock.id,
                            }
                        ],
                        "nextScreening": {
                            "beginningDatetime": tz_aware_beginning_datetime.isoformat(),
                            "bookability": "BOOKABLE",
                            "features": [],
                            "price": 10.1,
                            "stockId": stock.id,
                        },
                    }
                ],
            },
            {
                "date": tomorrow.isoformat(),
                "screenings": [
                    {
                        "duration": 116,
                        "genres": [],
                        "last30DaysBookings": 0,
                        "movieName": stock.offer.name,
                        "offerId": stock.offer.id,
                        "thumbUrl": None,
                        "dayScreenings": [],
                        "nextScreening": {
                            "beginningDatetime": tz_aware_beginning_datetime.isoformat(),
                            "bookability": "BOOKABLE",
                            "features": [],
                            "price": 10.1,
                            "stockId": stock.id,
                        },
                    }
                ],
            },
        ]

    def test_sold_out_screening(self, client):
        user = users_factories.BeneficiaryFactory()
        product = offers_factories.ProductFactory(subcategoryId=subcategories.SEANCE_CINE.id, durationMinutes=116)
        stock = offers_factories.EventStockFactory(
            quantity=0, offer__product=product, beginningDatetime=date_utils.get_naive_utc_now() + timedelta(minutes=10)
        )
        start = date_utils.get_naive_utc_now().replace(hour=0, minute=0, second=0, microsecond=0)
        end = date_utils.get_naive_utc_now() + timedelta(days=1)
        venue_id = stock.offer.venue.id
        expected_num_queries = 1  # user
        expected_num_queries += 1  # venue
        expected_num_queries += 1  # offers
        expected_num_queries += 1  # deposits
        expected_num_queries += 1  # user bookings
        client.with_token(user)
        with assert_num_queries(expected_num_queries):
            response = client.get(f"/native/v1/venue/{venue_id}/movie/calendar/me", params={"from": start, "to": end})
            assert response.status_code == 200

        calendar = response.json["calendar"]
        today = date_utils.default_timezone_to_local_datetime(
            date_utils.get_naive_utc_now(), stock.offer.offererAddress.address.timezone
        ).date()
        today_screenings = [e["screenings"] for e in calendar if e["date"] == today.isoformat()][0]
        assert today_screenings[0]["dayScreenings"][0]["bookability"] == "STOCK_IS_SOLD_OUT"
        assert today_screenings[0]["nextScreening"]["bookability"] == "STOCK_IS_SOLD_OUT"

    @pytest.mark.features(DISABLE_BOOST_EXTERNAL_BOOKINGS=True)
    def test_disabled_booking(self, client):
        user = users_factories.BeneficiaryFactory()
        product = offers_factories.ProductFactory(subcategoryId=subcategories.SEANCE_CINE.id, durationMinutes=116)
        disabled_provider = get_provider_by_local_class("BoostStocks")
        stock = offers_factories.EventStockFactory(
            offer__lastProvider=disabled_provider,
            offer__product=product,
            beginningDatetime=date_utils.get_naive_utc_now() + timedelta(hours=1),
        )
        start = date_utils.get_naive_utc_now().replace(hour=0, minute=0, second=0, microsecond=0)
        end = date_utils.get_naive_utc_now() + timedelta(days=1)
        venue_id = stock.offer.venue.id
        expected_num_queries = 1  # user
        expected_num_queries += 1  # venue
        expected_num_queries += 1  # offers
        expected_num_queries += 1  # deposits
        expected_num_queries += 1  # user bookings
        client.with_token(user)
        with assert_num_queries(expected_num_queries):
            response = client.get(f"/native/v1/venue/{venue_id}/movie/calendar/me", params={"from": start, "to": end})
            assert response.status_code == 200

        calendar = response.json["calendar"]
        today = date_utils.default_timezone_to_local_datetime(
            date_utils.get_naive_utc_now(), stock.offer.offererAddress.address.timezone
        ).date()
        today_screenings = [e["screenings"] for e in calendar if e["date"] == today.isoformat()][0]
        assert today_screenings[0]["dayScreenings"][0]["bookability"] == "STOCK_BOOKING_IS_DISABLED"
        assert today_screenings[0]["nextScreening"]["bookability"] == "STOCK_BOOKING_IS_DISABLED"

    def test_when_user_cannot_book(self, client):
        user = users_factories.UserFactory(age=100)
        product = offers_factories.ProductFactory(subcategoryId=subcategories.SEANCE_CINE.id, durationMinutes=116)
        disabled_provider = get_provider_by_local_class("BoostStocks")
        stock = offers_factories.EventStockFactory(
            offer__lastProvider=disabled_provider,
            offer__product=product,
            beginningDatetime=date_utils.get_naive_utc_now() + timedelta(minutes=10),
        )
        start = date_utils.get_naive_utc_now().replace(hour=0, minute=0, second=0, microsecond=0)
        end = date_utils.get_naive_utc_now() + timedelta(days=1)
        venue_id = stock.offer.venue.id
        expected_num_queries = 1  # user
        expected_num_queries += 1  # venue
        expected_num_queries += 1  # offers
        expected_num_queries += 1  # deposits
        client.with_token(user)
        with assert_num_queries(expected_num_queries):
            response = client.get(f"/native/v1/venue/{venue_id}/movie/calendar/me", params={"from": start, "to": end})
            assert response.status_code == 200

        calendar = response.json["calendar"]
        today = date_utils.default_timezone_to_local_datetime(
            date_utils.get_naive_utc_now(), stock.offer.offererAddress.address.timezone
        ).date()
        today_screenings = [e["screenings"] for e in calendar if e["date"] == today.isoformat()][0]
        assert today_screenings[0]["dayScreenings"][0]["bookability"] == "USER_CANNOT_BOOK"
        assert today_screenings[0]["nextScreening"]["bookability"] == "USER_CANNOT_BOOK"

    def test_bookability_finish_subscription_required(self, client):
        user = users_factories.UserFactory(dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(years=18))
        product = offers_factories.ProductFactory(subcategoryId=subcategories.SEANCE_CINE.id, durationMinutes=116)
        stock = offers_factories.EventStockFactory(
            offer__product=product, beginningDatetime=date_utils.get_naive_utc_now() + timedelta(minutes=10)
        )
        start = date_utils.get_naive_utc_now().replace(hour=0, minute=0, second=0, microsecond=0)
        end = date_utils.get_naive_utc_now() + timedelta(days=1)
        venue_id = stock.offer.venue.id
        expected_num_queries = 1  # user
        expected_num_queries += 1  # venue
        expected_num_queries += 1  # offers
        expected_num_queries += 1  # deposit
        expected_num_queries += 1  # beneficiary_fraud_review
        expected_num_queries += 1  # beneficiary_fraud_check
        client.with_token(user)
        with assert_num_queries(expected_num_queries):
            response = client.get(f"/native/v1/venue/{venue_id}/movie/calendar/me", params={"from": start, "to": end})
            assert response.status_code == 200

        calendar = response.json["calendar"]
        today = date_utils.default_timezone_to_local_datetime(
            date_utils.get_naive_utc_now(), stock.offer.offererAddress.address.timezone
        ).date()
        today_screenings = [e["screenings"] for e in calendar if e["date"] == today.isoformat()][0]
        assert today_screenings[0]["dayScreenings"][0]["bookability"] == "FINISH_SUBSCRIPTION_REQUIRED"

    def test_bookability_user_application_still_processing(self, client):
        user = users_factories.UserFactory(
            dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(years=18),
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            status=subscription_models.FraudCheckStatus.OK,
            type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
            user=user,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            status=subscription_models.FraudCheckStatus.PENDING,
            type=subscription_models.FraudCheckType.DMS,
            user=user,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            status=subscription_models.FraudCheckStatus.OK,
            type=subscription_models.FraudCheckType.HONOR_STATEMENT,
            user=user,
        )

        product = offers_factories.ProductFactory(subcategoryId=subcategories.SEANCE_CINE.id, durationMinutes=116)
        stock = offers_factories.EventStockFactory(
            offer__product=product, beginningDatetime=date_utils.get_naive_utc_now() + timedelta(minutes=10)
        )
        start = date_utils.get_naive_utc_now().replace(hour=0, minute=0, second=0, microsecond=0)
        end = date_utils.get_naive_utc_now() + timedelta(days=1)
        venue_id = stock.offer.venue.id
        expected_num_queries = 1  # user
        expected_num_queries += 1  # venue
        expected_num_queries += 1  # offers
        expected_num_queries += 1  # deposit
        expected_num_queries += 1  # beneficiary_fraud_review
        expected_num_queries += 1  # beneficiary_fraud_check
        expected_num_queries += 1  # action_history
        client.with_token(user)
        with assert_num_queries(expected_num_queries):
            response = client.get(f"/native/v1/venue/{venue_id}/movie/calendar/me", params={"from": start, "to": end})
            assert response.status_code == 200

        today = date_utils.default_timezone_to_local_datetime(
            date_utils.get_naive_utc_now(), stock.offer.offererAddress.address.timezone
        ).date()
        today_screenings = [e["screenings"] for e in response.json["calendar"] if e["date"] == today.isoformat()][0]
        assert today_screenings[0]["dayScreenings"][0]["bookability"] == "USER_APPLICATION_STILL_PROCESSING"

    def test_bookability_user_application_has_error(self, client):
        user = users_factories.UserFactory(
            dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(years=18),
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
            status=subscription_models.FraudCheckStatus.OK,
            user=user,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            status=subscription_models.FraudCheckStatus.KO,
            reasonCodes=[subscription_models.FraudReasonCode.INVALID_ID_PIECE_NUMBER],
            type=subscription_models.FraudCheckType.UBBLE,
            user=user,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            status=subscription_models.FraudCheckStatus.OK,
            type=subscription_models.FraudCheckType.HONOR_STATEMENT,
            user=user,
        )
        product = offers_factories.ProductFactory(subcategoryId=subcategories.SEANCE_CINE.id, durationMinutes=116)
        stock = offers_factories.EventStockFactory(
            offer__product=product, beginningDatetime=date_utils.get_naive_utc_now() + timedelta(minutes=10)
        )
        start = date_utils.get_naive_utc_now().replace(hour=0, minute=0, second=0, microsecond=0)
        end = date_utils.get_naive_utc_now() + timedelta(days=1)
        venue_id = stock.offer.venue.id
        expected_num_queries = 1  # user
        expected_num_queries += 1  # venue
        expected_num_queries += 1  # offers
        expected_num_queries += 1  # deposit
        expected_num_queries += 1  # beneficiary_fraud_review
        expected_num_queries += 1  # beneficiary_fraud_check
        expected_num_queries += 1  # action_history
        client.with_token(user)
        with assert_num_queries(expected_num_queries):
            response = client.get(f"/native/v1/venue/{venue_id}/movie/calendar/me", params={"from": start, "to": end})
            assert response.status_code == 200

        today = date_utils.default_timezone_to_local_datetime(
            date_utils.get_naive_utc_now(), stock.offer.offererAddress.address.timezone
        ).date()
        today_screenings = [e["screenings"] for e in response.json["calendar"] if e["date"] == today.isoformat()][0]
        assert today_screenings[0]["dayScreenings"][0]["bookability"] == "USER_HAS_APPLICATION_ERROR"

    def test_bookability_user_has_already_booked_offer(self, client):
        user = users_factories.BeneficiaryFactory()
        product = offers_factories.ProductFactory(subcategoryId=subcategories.SEANCE_CINE.id, durationMinutes=116)
        stock = offers_factories.EventStockFactory(
            offer__product=product,
            beginningDatetime=date_utils.get_naive_utc_now() + timedelta(minutes=10),
        )
        offers_factories.EventStockFactory(offer=stock.offer)
        _user_booking = BookingFactory(user=user, stock=stock)
        start = date_utils.get_naive_utc_now().replace(hour=0, minute=0, second=0, microsecond=0)
        end = date_utils.get_naive_utc_now() + timedelta(days=1)
        venue_id = stock.offer.venue.id

        expected_num_queries = 1  # user
        expected_num_queries += 1  # venue
        expected_num_queries += 1  # offers
        expected_num_queries += 1  # deposit
        expected_num_queries += 1  # user bookings
        client.with_token(user)
        with assert_num_queries(expected_num_queries):
            response = client.get(f"/native/v1/venue/{venue_id}/movie/calendar/me", params={"from": start, "to": end})
            assert response.status_code == 200

        today = date_utils.default_timezone_to_local_datetime(
            date_utils.get_naive_utc_now(), stock.offer.offererAddress.address.timezone
        ).date()
        today_screenings = [e["screenings"] for e in response.json["calendar"] if e["date"] == today.isoformat()][0]
        assert today_screenings[0]["dayScreenings"][0]["bookability"] == "USER_HAS_ALREADY_BOOKED_OFFER"

    def test_bookability_user_has_already_booked_related_offer(self, client):
        user = users_factories.BeneficiaryFactory()
        product = offers_factories.ProductFactory(subcategoryId=subcategories.SEANCE_CINE.id, durationMinutes=116)
        stock = offers_factories.EventStockFactory(
            offer__product=product,
            beginningDatetime=date_utils.get_naive_utc_now() + timedelta(minutes=10),
        )
        another_stock = offers_factories.EventStockFactory(offer=stock.offer)
        _user_booking = BookingFactory(user=user, stock=another_stock)
        start = date_utils.get_naive_utc_now().replace(hour=0, minute=0, second=0, microsecond=0)
        end = date_utils.get_naive_utc_now() + timedelta(days=1)
        venue_id = stock.offer.venue.id

        expected_num_queries = 1  # user
        expected_num_queries += 1  # venue
        expected_num_queries += 1  # offers
        expected_num_queries += 1  # deposit
        expected_num_queries += 1  # user bookings
        client.with_token(user)
        with assert_num_queries(expected_num_queries):
            response = client.get(f"/native/v1/venue/{venue_id}/movie/calendar/me", params={"from": start, "to": end})
            assert response.status_code == 200

        today = date_utils.default_timezone_to_local_datetime(
            date_utils.get_naive_utc_now(), stock.offer.offererAddress.address.timezone
        ).date()
        today_screenings = [e["screenings"] for e in response.json["calendar"] if e["date"] == today.isoformat()][0]
        assert today_screenings[0]["dayScreenings"][0]["bookability"] == "USER_HAS_ALREADY_BOOKED_RELATED_OFFER"

    def test_returns_404_if_venue_not_found(self, client):
        user = users_factories.BeneficiaryFactory()
        client.with_token(user)
        expected_num_queries = 1  # user
        expected_num_queries += 1  # venue
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/venue/999999999/movie/calendar/me")
            assert response.status_code == 404

    def test_timezone_aware_query_params(self, client):
        user = users_factories.BeneficiaryFactory()
        product = offers_factories.ProductFactory(subcategoryId=subcategories.SEANCE_CINE.id, durationMinutes=116)
        address = AddressFactory(timezone="Europe/Paris")
        start_date = datetime.now(UTC)
        end_date = start_date + timedelta(days=1)
        stock = offers_factories.EventStockFactory(
            offer__product=product,
            beginningDatetime=date_utils.get_naive_utc_now() + timedelta(hours=1),
            offer__venue__offererAddress__address=address,
        )
        venue_id = stock.offer.venue.id
        expected_num_queries = 1  # user
        expected_num_queries += 1  # venue
        expected_num_queries += 1  # offers
        expected_num_queries += 1  # deposit
        expected_num_queries += 1  # user bookings
        client.with_token(user)
        with assert_num_queries(expected_num_queries):
            response = client.get(
                f"/native/v1/venue/{venue_id}/movie/calendar/me",
                params={"from": start_date.isoformat(), "to": end_date.isoformat()},
            )
            assert response.status_code == 200

        calendar = response.json["calendar"]
        start_date_day = date_utils.default_timezone_to_local_datetime(
            date_utils.get_naive_utc_now(), address.timezone
        ).date()
        end_date_day = date_utils.default_timezone_to_local_datetime(
            date_utils.get_naive_utc_now() + timedelta(days=1), address.timezone
        ).date()
        assert len(calendar) == 2
        assert [start_date_day.isoformat(), end_date_day.isoformat()] == [e["date"] for e in calendar]
        today_screenings = [e for e in calendar if e["date"] == start_date_day.isoformat()][0]["screenings"]
        assert len(today_screenings) == 1
        today_day_screenings = today_screenings[0]["dayScreenings"]
        assert len(today_day_screenings) == 1
        today_day_screening = today_day_screenings[0]
        assert today_day_screening["stockId"] == stock.id

        tomorrow_screenings = [e for e in calendar if e["date"] == end_date_day.isoformat()][0]["screenings"]
        assert len(tomorrow_screenings) == 1
        tomorrow_day_screenings = tomorrow_screenings[0]["dayScreenings"]
        assert len(tomorrow_day_screenings) == 0

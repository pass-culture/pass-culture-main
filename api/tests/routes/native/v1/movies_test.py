from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta

import pytest

import pcapi.core.offers.factories as offers_factories
from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.categories import subcategories
from pcapi.core.geography.factories import AddressFactory
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.providers.repository import get_provider_by_local_class
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories
from pcapi.utils import date as date_utils


pytestmark = pytest.mark.usefixtures("db_session")


class MovieCalendarTest:
    def test_get_movie_shows_with_allocine_id(self, client):
        product = offers_factories.ProductFactory(extraData={"allocineId": 12345})
        address = AddressFactory(latitude=48.85, longitude=2.35)
        stock = offers_factories.EventStockFactory(
            offer__product=product,
            offer__venue__offererAddress__address=address,
            offer__venue__offererAddress__label="Cinéma Parisien",
            beginningDatetime=datetime.now() + timedelta(hours=1),
        )
        today = date.today()
        tomorrow = date.today() + timedelta(days=1)
        params = {
            "allocineId": "12345",
            "latitude": 48.85,
            "longitude": 2.35,
            "from": today,
            "to": tomorrow,
        }
        expected_num_queries = 1  # product
        expected_num_queries += 1  # stocks
        expected_num_queries += 1  # screenings
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/movie/calendar", params=params)
            assert response.status_code == 200

        calendar = response.json["calendar"]
        assert calendar == {
            today.isoformat(): [
                {
                    "address": f"{address.street}, {address.postalCode} {address.city}",
                    "distance": 0.0,
                    "dayScreenings": [
                        {
                            "beginningDatetime": date_utils.format_into_utc_date(stock.beginningDatetime),
                            "bookability": "BOOKABLE",
                            "features": [],
                            "price": float(stock.price),
                            "stockId": stock.id,
                        }
                    ],
                    "label": stock.offer.offererAddress.label,
                    "nextScreening": {
                        "beginningDatetime": date_utils.format_into_utc_date(stock.beginningDatetime),
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
            tomorrow.isoformat(): [
                {
                    "address": f"{address.street}, {address.postalCode} {address.city}",
                    "distance": 0.0,
                    "dayScreenings": [],
                    "label": stock.offer.offererAddress.label,
                    "nextScreening": {
                        "beginningDatetime": date_utils.format_into_utc_date(stock.beginningDatetime),
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
        }

    def test_get_movie_shows_with_visa(self, client):
        product = offers_factories.ProductFactory(extraData={"visa": "12345"})
        address = AddressFactory(latitude=48.85, longitude=2.35)
        offers_factories.EventStockFactory(
            offer__product=product,
            offer__venue__offererAddress__address=address,
            beginningDatetime=datetime.now() + timedelta(hours=1),
        )

        today = date.today()
        tomorrow = date.today() + timedelta(days=1)
        params = {
            "visa": "12345",
            "latitude": 48.85,
            "longitude": 2.35,
            "from": today,
            "to": tomorrow,
        }
        expected_num_queries = 1  # product
        expected_num_queries += 1  # stocks
        expected_num_queries += 1  # screenings
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/movie/calendar", params=params)
            assert response.status_code == 200

        assert len(response.json["calendar"][today.isoformat()]) == 1
        assert len(response.json["calendar"][tomorrow.isoformat()]) == 1

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
        today = date.today()
        tomorrow = date.today() + timedelta(days=1)
        params = {
            "allocineId": "12345",
            "latitude": 48.85,
            "longitude": 2.35,
            "from": today,
            "to": tomorrow,
        }
        expected_num_queries = 1  # product
        expected_num_queries += 1  # stocks
        expected_num_queries += 1  # screenings
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/movie/calendar", params=params)
            assert response.status_code == 200

        assert response.json["calendar"][today.isoformat()] == []
        assert response.json["calendar"][tomorrow.isoformat()] == []

    def test_screenings_are_sorted_by_distance_then_screening_day(self, client):
        product = offers_factories.ProductFactory(extraData={"allocineId": 12345})
        closest_address_for_today = AddressFactory(latitude=48.85, longitude=2.35)
        closest_address_for_tomorrow = AddressFactory(latitude=48.85, longitude=2.35)
        furthest_address_for_today = AddressFactory(latitude=48.84, longitude=2.35)
        furthest_address_for_tomorrow = AddressFactory(latitude=48.84, longitude=2.35)
        today_closest_stock = offers_factories.EventStockFactory(
            offer__product=product,
            offer__venue__offererAddress__address=closest_address_for_today,
            beginningDatetime=datetime.now() + timedelta(hours=1),
        )
        today_furthest_stock = offers_factories.EventStockFactory(
            offer__product=product,
            offer__venue__offererAddress__address=furthest_address_for_today,
            beginningDatetime=datetime.now() + timedelta(hours=1),
        )
        tomorrow_closest_stock = offers_factories.EventStockFactory(
            offer__product=product,
            offer__venue__offererAddress__address=closest_address_for_tomorrow,
            beginningDatetime=datetime.now() + timedelta(hours=23),
        )
        tomorrow_furthest_stock = offers_factories.EventStockFactory(
            offer__product=product,
            offer__venue__offererAddress__address=furthest_address_for_tomorrow,
            beginningDatetime=datetime.now() + timedelta(hours=23),
        )

        today = date.today()
        tomorrow = date.today() + timedelta(days=1)
        params = {
            "allocineId": "12345",
            "latitude": 48.85,
            "longitude": 2.35,
            "from": datetime.combine(today, time.min),
            "to": datetime.combine(tomorrow, time.max),
        }
        expected_num_queries = 1  # product
        expected_num_queries += 1  # stocks
        expected_num_queries += 1  # screenings
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/movie/calendar", params=params)
            assert response.status_code == 200

        today_screenings = response.json["calendar"][today.isoformat()]
        tomorrow_screenings = response.json["calendar"][tomorrow.isoformat()]
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
            beginningDatetime=datetime.now() + timedelta(hours=1),
        )
        last_stock = offers_factories.EventStockFactory(
            offer__product=product,
            offer__venue=venue,
            beginningDatetime=datetime.now() + timedelta(hours=2),
        )

        today = date.today()
        tomorrow = date.today() + timedelta(days=1)
        params = {
            "allocineId": "12345",
            "latitude": 48.85,
            "longitude": 2.35,
            "from": today,
            "to": tomorrow,
        }
        expected_num_queries = 1  # product
        expected_num_queries += 1  # stocks
        expected_num_queries += 1  # screenings
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/movie/calendar", params=params)
            assert response.status_code == 200

        today_screenings = response.json["calendar"][today.isoformat()]
        assert today_screenings[0]["dayScreenings"][0]["stockId"] == first_stock.id
        assert today_screenings[0]["dayScreenings"][1]["stockId"] == last_stock.id

    def test_next_screening_is_closest_from_today(self, client):
        product = offers_factories.ProductFactory(extraData={"allocineId": 12345})
        address = AddressFactory(latitude=48.85, longitude=2.35)
        venue = offerers_factories.VenueFactory(offererAddress__address=address)
        closest_stock_from_tomorrow = offers_factories.EventStockFactory(
            offer__product=product,
            offer__venue=venue,
            beginningDatetime=datetime.now() + timedelta(hours=2),
        )
        _furthest_stock_from_tomorrow = offers_factories.EventStockFactory(
            offer__product=product,
            offer__venue=venue,
            beginningDatetime=datetime.now() + timedelta(days=3, hours=1),
        )

        today = date.today()
        tomorrow = date.today() + timedelta(days=1)
        in_three_days = date.today() + timedelta(days=3)
        params = {
            "allocineId": "12345",
            "latitude": 48.85,
            "longitude": 2.35,
            "from": today,
            "to": in_three_days,
        }
        expected_num_queries = 1  # product
        expected_num_queries += 1  # stocks
        expected_num_queries += 1  # screenings
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/movie/calendar", params=params)
            assert response.status_code == 200

        tomorrow_screenings = response.json["calendar"][tomorrow.isoformat()]
        assert tomorrow_screenings[0]["nextScreening"]["stockId"] == closest_stock_from_tomorrow.id

    def test_screenings_are_within_around_radius(self, client):
        product = offers_factories.ProductFactory(extraData={"allocineId": 12345})
        closest_address = AddressFactory(latitude=48.8, longitude=2.35)
        furthest_address = AddressFactory(latitude=48.0, longitude=2.35)
        _closest_stock = offers_factories.EventStockFactory(
            offer__product=product,
            offer__venue__offererAddress__address=closest_address,
            beginningDatetime=datetime.now() + timedelta(hours=1),
        )
        _furthest_stock = offers_factories.EventStockFactory(
            offer__product=product,
            offer__venue__offererAddress__address=furthest_address,
            beginningDatetime=datetime.now() + timedelta(hours=1),
        )

        start_of_day = datetime.combine(date.today(), time.min)
        end_of_day = datetime.combine(date.today(), time.max)
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

        today_screenings = response.json["calendar"][start_of_day.date().isoformat()]
        assert len(today_screenings) == 1
        assert len(today_screenings[0]["dayScreenings"]) == 1
        assert today_screenings[0]["distance"] < 10_000

    def test_sold_out_screening(self, client):
        product = offers_factories.ProductFactory(extraData={"allocineId": 12345})
        address = AddressFactory(latitude=48.85, longitude=2.35)
        _sold_out_stock = offers_factories.EventStockFactory(
            quantity=1,
            dnBookedQuantity=1,
            offer__product=product,
            offer__venue__offererAddress__address=address,
            beginningDatetime=datetime.now() + timedelta(hours=1),
        )
        today = date.today()
        tomorrow = date.today() + timedelta(days=1)
        params = {
            "allocineId": "12345",
            "latitude": 48.85,
            "longitude": 2.35,
            "from": today,
            "to": tomorrow,
        }
        expected_num_queries = 1  # product
        expected_num_queries += 1  # stocks
        expected_num_queries += 1  # screenings
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/movie/calendar", params=params)
            assert response.status_code == 200

        calendar = response.json["calendar"]
        assert calendar[today.isoformat()][0]["dayScreenings"][0]["bookability"] == "STOCK_IS_SOLD_OUT"
        assert calendar[today.isoformat()][0]["nextScreening"]["bookability"] == "STOCK_IS_SOLD_OUT"

    @pytest.mark.features(DISABLE_BOOST_EXTERNAL_BOOKINGS=True)
    def test_disabled_booking(self, client):
        product = offers_factories.ProductFactory(extraData={"allocineId": 12345})
        disabled_provider = get_provider_by_local_class("BoostStocks")
        address = AddressFactory(latitude=48.85, longitude=2.35)
        _stock = offers_factories.EventStockFactory(
            offer__lastProvider=disabled_provider,
            offer__product=product,
            offer__venue__offererAddress__address=address,
            beginningDatetime=datetime.now() + timedelta(hours=1),
        )
        today = date.today()
        tomorrow = date.today() + timedelta(days=1)
        params = {
            "allocineId": "12345",
            "latitude": 48.85,
            "longitude": 2.35,
            "from": today,
            "to": tomorrow,
        }
        expected_num_queries = 1  # product
        expected_num_queries += 1  # stocks
        expected_num_queries += 1  # screenings
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/movie/calendar", params=params)
            assert response.status_code == 200

        calendar = response.json["calendar"]
        assert calendar[today.isoformat()][0]["dayScreenings"][0]["bookability"] == "STOCK_BOOKING_IS_DISABLED"
        assert calendar[today.isoformat()][0]["nextScreening"]["bookability"] == "STOCK_BOOKING_IS_DISABLED"


class MovieCalendarForUserTest:
    def test_get_movie_shows_for_user(self, client):
        user = users_factories.BeneficiaryFactory()
        product = offers_factories.ProductFactory(extraData={"allocineId": 12345})
        address = AddressFactory(latitude=48.85, longitude=2.35)
        stock = offers_factories.EventStockFactory(
            offer__product=product,
            offer__venue__offererAddress__address=address,
            offer__venue__offererAddress__label="Cinéma Parisien",
            beginningDatetime=datetime.now() + timedelta(hours=1),
        )
        today = date.today()
        tomorrow = date.today() + timedelta(days=1)
        params = {
            "allocineId": "12345",
            "latitude": 48.85,
            "longitude": 2.35,
            "from": today,
            "to": tomorrow,
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

        assert response.json == {
            "calendar": {
                today.isoformat(): [
                    {
                        "address": f"{address.street}, {address.postalCode} {address.city}",
                        "distance": 0.0,
                        "dayScreenings": [
                            {
                                "beginningDatetime": date_utils.format_into_utc_date(stock.beginningDatetime),
                                "bookability": "BOOKABLE",
                                "features": [],
                                "price": float(stock.price),
                                "stockId": stock.id,
                            }
                        ],
                        "label": stock.offer.offererAddress.label,
                        "nextScreening": {
                            "beginningDatetime": date_utils.format_into_utc_date(stock.beginningDatetime),
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
                tomorrow.isoformat(): [
                    {
                        "address": f"{address.street}, {address.postalCode} {address.city}",
                        "distance": 0.0,
                        "dayScreenings": [],
                        "label": stock.offer.offererAddress.label,
                        "nextScreening": {
                            "beginningDatetime": date_utils.format_into_utc_date(stock.beginningDatetime),
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
        }

    def test_when_stock_is_sold_out(self, client):
        user = users_factories.UserFactory(age=100)
        product = offers_factories.ProductFactory(extraData={"allocineId": 12345})
        address = AddressFactory(latitude=48.85, longitude=2.35)
        _stock = offers_factories.EventStockFactory(
            offer__product=product,
            offer__venue__offererAddress__address=address,
            offer__venue__offererAddress__label="Cinéma Parisien",
            beginningDatetime=datetime.now() + timedelta(hours=1),
            quantity=0,
        )
        today = date.today()
        tomorrow = date.today() + timedelta(days=1)
        params = {
            "allocineId": "12345",
            "latitude": 48.85,
            "longitude": 2.35,
            "from": today,
            "to": tomorrow,
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

        assert response.json["calendar"][today.isoformat()][0]["dayScreenings"][0]["bookability"] == "STOCK_IS_SOLD_OUT"

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
            beginningDatetime=datetime.now() + timedelta(hours=1),
            quantity=0,
        )
        today = date.today()
        tomorrow = date.today() + timedelta(days=1)
        params = {
            "allocineId": "12345",
            "latitude": 48.85,
            "longitude": 2.35,
            "from": today,
            "to": tomorrow,
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

        assert (
            response.json["calendar"][today.isoformat()][0]["dayScreenings"][0]["bookability"]
            == "STOCK_BOOKING_IS_DISABLED"
        )

    def test_when_user_cannot_book(self, client):
        user = users_factories.UserFactory(age=100)
        product = offers_factories.ProductFactory(extraData={"allocineId": 12345})
        address = AddressFactory(latitude=48.85, longitude=2.35)
        _stock = offers_factories.EventStockFactory(
            offer__product=product,
            offer__venue__offererAddress__address=address,
            offer__venue__offererAddress__label="Cinéma Parisien",
            beginningDatetime=datetime.now() + timedelta(hours=1),
        )
        today = date.today()
        tomorrow = date.today() + timedelta(days=1)
        params = {
            "allocineId": "12345",
            "latitude": 48.85,
            "longitude": 2.35,
            "from": today,
            "to": tomorrow,
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

        assert response.json["calendar"][today.isoformat()][0]["dayScreenings"][0]["bookability"] == "USER_CANNOT_BOOK"

    def test_when_user_has_not_enough_credit(self, client):
        user = users_factories.BeneficiaryFactory()
        product = offers_factories.ProductFactory(extraData={"allocineId": 12345})
        address = AddressFactory(latitude=48.85, longitude=2.35)
        _stock = offers_factories.EventStockFactory(
            price=1000,
            offer__product=product,
            offer__venue__offererAddress__address=address,
            offer__venue__offererAddress__label="Cinéma Parisien",
            beginningDatetime=datetime.now() + timedelta(hours=1),
        )
        today = date.today()
        tomorrow = date.today() + timedelta(days=1)
        params = {
            "allocineId": "12345",
            "latitude": 48.85,
            "longitude": 2.35,
            "from": today,
            "to": tomorrow,
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

        assert (
            response.json["calendar"][today.isoformat()][0]["dayScreenings"][0]["bookability"]
            == "USER_HAS_INSUFFICIENT_CREDIT"
        )

    def test_when_user_has_already_booked_offer(self, client):
        user = users_factories.BeneficiaryFactory()
        product = offers_factories.ProductFactory(extraData={"allocineId": 12345})
        address = AddressFactory(latitude=48.85, longitude=2.35)
        stock = offers_factories.EventStockFactory(
            offer__product=product,
            offer__venue__offererAddress__address=address,
            offer__venue__offererAddress__label="Cinéma Parisien",
            beginningDatetime=datetime.now() + timedelta(hours=1),
        )
        another_stock = offers_factories.StockFactory(offer=stock.offer)
        _user_booking = BookingFactory(user=user, stock=another_stock)
        today = date.today()
        tomorrow = date.today() + timedelta(days=1)
        params = {
            "allocineId": "12345",
            "latitude": 48.85,
            "longitude": 2.35,
            "from": today,
            "to": tomorrow,
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

        assert (
            response.json["calendar"][today.isoformat()][0]["dayScreenings"][0]["bookability"]
            == "USER_HAS_ALREADY_BOOKED_OFFER"
        )


class VenueMovieCalendarTest:
    def test_get_venue_movie_calendar(self, client):
        product = offers_factories.ProductFactory(subcategoryId=subcategories.SEANCE_CINE.id, durationMinutes=116)
        stock = offers_factories.EventStockFactory(
            offer__product=product, beginningDatetime=datetime.now() + timedelta(hours=1)
        )
        today = date.today()
        tomorrow = date.today() + timedelta(days=1)
        venue_id = stock.offer.venue.id
        expected_num_queries = 1  # offers
        with assert_num_queries(expected_num_queries):
            response = client.get(f"/native/v1/venue/{venue_id}/movie/calendar", params={"from": today, "to": tomorrow})
            assert response.status_code == 200

        calendar = response.json["calendar"]
        assert calendar == {
            today.isoformat(): [
                {
                    "duration": 116,
                    "genres": [],
                    "last30DaysBookings": 0,
                    "movieName": stock.offer.name,
                    "offerId": stock.offer.id,
                    "thumbUrl": None,
                    "dayScreenings": [
                        {
                            "beginningDatetime": date_utils.format_into_utc_date(stock.beginningDatetime),
                            "bookability": "BOOKABLE",
                            "features": [],
                            "price": 10.1,
                            "stockId": stock.id,
                        }
                    ],
                    "nextScreening": {
                        "beginningDatetime": date_utils.format_into_utc_date(stock.beginningDatetime),
                        "bookability": "BOOKABLE",
                        "features": [],
                        "price": 10.1,
                        "stockId": stock.id,
                    },
                }
            ],
            tomorrow.isoformat(): [
                {
                    "duration": 116,
                    "genres": [],
                    "last30DaysBookings": 0,
                    "movieName": stock.offer.name,
                    "offerId": stock.offer.id,
                    "thumbUrl": None,
                    "dayScreenings": [],
                    "nextScreening": {
                        "beginningDatetime": date_utils.format_into_utc_date(stock.beginningDatetime),
                        "bookability": "BOOKABLE",
                        "features": [],
                        "price": 10.1,
                        "stockId": stock.id,
                    },
                }
            ],
        }

    def test_day_screenings_are_sorted_by_last_30_days_bookings(self, client):
        tomorrow = datetime.today() + timedelta(days=1)
        beginning_datetime = tomorrow.replace(hour=1)
        movie_day = tomorrow.date()
        day_after = movie_day + timedelta(days=1)
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
        expected_num_queries = 1  # offers
        with assert_num_queries(expected_num_queries):
            response = client.get(
                f"/native/v1/venue/{venue_id}/movie/calendar", params={"from": movie_day, "to": day_after}
            )
            assert response.status_code == 200

        movie_day_screenings = response.json["calendar"][movie_day.isoformat()]
        assert movie_day_screenings[0]["dayScreenings"][0]["stockId"] == most_booked_stock.id
        assert movie_day_screenings[1]["dayScreenings"][0]["stockId"] == least_booked_stock.id

    def test_day_screenings_are_sorted_by_beginning_datetime(self, client):
        tomorrow = datetime.today() + timedelta(days=1)
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
        expected_num_queries = 1  # offers
        with assert_num_queries(expected_num_queries):
            response = client.get(
                f"/native/v1/venue/{venue_id}/movie/calendar",
                params={"from": before_screenings, "to": after_screenings},
            )
            assert response.status_code == 200

        tomorrow_screenings = response.json["calendar"][tomorrow.date().isoformat()]
        assert tomorrow_screenings[0]["dayScreenings"][0]["stockId"] == first_screened_stock.id
        assert tomorrow_screenings[0]["dayScreenings"][1]["stockId"] == last_screened_stock.id

    def test_next_screening_is_closest_requested_day(self, client):
        tomorrow = datetime.today() + timedelta(days=1)
        in_two_days = datetime.today() + timedelta(days=2)
        in_three_days = datetime.today() + timedelta(days=3)
        in_four_days = datetime.today() + timedelta(days=4)
        before_screenings = tomorrow.replace(hour=0)
        after_screenings = datetime.today() + timedelta(days=5)
        product = offers_factories.ProductFactory(subcategoryId=subcategories.SEANCE_CINE.id)
        offer = offers_factories.OfferFactory(product=product)
        tomorrow_stock = offers_factories.EventStockFactory(offer=offer, beginningDatetime=tomorrow)
        in_four_days_stock = offers_factories.EventStockFactory(offer=offer, beginningDatetime=in_four_days)

        venue_id = offer.venue.id
        expected_num_queries = 1  # offers
        with assert_num_queries(expected_num_queries):
            response = client.get(
                f"/native/v1/venue/{venue_id}/movie/calendar",
                params={"from": before_screenings, "to": after_screenings},
            )
            assert response.status_code == 200

        calendar = response.json["calendar"]
        assert calendar[in_two_days.date().isoformat()][0]["nextScreening"]["stockId"] == tomorrow_stock.id
        assert calendar[in_three_days.date().isoformat()][0]["nextScreening"]["stockId"] == in_four_days_stock.id

    def test_calendar_is_empty_if_no_screenings_found(self, client):
        tomorrow = (datetime.today() + timedelta(days=1)).date()
        in_two_days = (datetime.today() + timedelta(days=2)).date()
        venue = offerers_factories.VenueFactory()

        venue_id = venue.id
        expected_num_queries = 1  # offers
        with assert_num_queries(expected_num_queries):
            response = client.get(
                f"/native/v1/venue/{venue_id}/movie/calendar", params={"from": tomorrow, "to": in_two_days}
            )
            assert response.status_code == 200

        assert response.json["calendar"] == {tomorrow.isoformat(): [], in_two_days.isoformat(): []}

    def test_calendar_is_empty_if_venue_not_found(self, client):
        tomorrow = (datetime.today() + timedelta(days=1)).date()
        in_two_days = (datetime.today() + timedelta(days=2)).date()

        fake_venue_id = 999999
        expected_num_queries = 1  # offers
        with assert_num_queries(expected_num_queries):
            response = client.get(
                f"/native/v1/venue/{fake_venue_id}/movie/calendar", params={"from": tomorrow, "to": in_two_days}
            )
            assert response.status_code == 200

        assert response.json["calendar"] == {tomorrow.isoformat(): [], in_two_days.isoformat(): []}

    def test_sold_out_screening(self, client):
        product = offers_factories.ProductFactory(subcategoryId=subcategories.SEANCE_CINE.id, durationMinutes=116)
        stock = offers_factories.EventStockFactory(
            quantity=0, offer__product=product, beginningDatetime=datetime.now() + timedelta(hours=1)
        )
        today = date.today()
        tomorrow = date.today() + timedelta(days=1)
        venue_id = stock.offer.venue.id
        expected_num_queries = 1  # offers
        with assert_num_queries(expected_num_queries):
            response = client.get(f"/native/v1/venue/{venue_id}/movie/calendar", params={"from": today, "to": tomorrow})
            assert response.status_code == 200

        calendar = response.json["calendar"]
        print(calendar)
        assert calendar[today.isoformat()][0]["dayScreenings"][0]["bookability"] == "STOCK_IS_SOLD_OUT"
        assert calendar[today.isoformat()][0]["nextScreening"]["bookability"] == "STOCK_IS_SOLD_OUT"

    @pytest.mark.features(DISABLE_BOOST_EXTERNAL_BOOKINGS=True)
    def test_disabled_booking(self, client):
        product = offers_factories.ProductFactory(subcategoryId=subcategories.SEANCE_CINE.id, durationMinutes=116)
        disabled_provider = get_provider_by_local_class("BoostStocks")
        stock = offers_factories.EventStockFactory(
            offer__lastProvider=disabled_provider,
            offer__product=product,
            beginningDatetime=datetime.now() + timedelta(hours=1),
        )
        today = date.today()
        tomorrow = date.today() + timedelta(days=1)
        venue_id = stock.offer.venue.id
        expected_num_queries = 1  # offers
        with assert_num_queries(expected_num_queries):
            response = client.get(f"/native/v1/venue/{venue_id}/movie/calendar", params={"from": today, "to": tomorrow})
            assert response.status_code == 200

        calendar = response.json["calendar"]
        assert calendar[today.isoformat()][0]["dayScreenings"][0]["bookability"] == "STOCK_BOOKING_IS_DISABLED"
        assert calendar[today.isoformat()][0]["nextScreening"]["bookability"] == "STOCK_BOOKING_IS_DISABLED"


class VenueMovieCalendarForUserTest:
    def test_get_venue_movie_calendar(self, client):
        user = users_factories.BeneficiaryFactory()
        product = offers_factories.ProductFactory(subcategoryId=subcategories.SEANCE_CINE.id, durationMinutes=116)
        stock = offers_factories.EventStockFactory(
            offer__product=product, beginningDatetime=datetime.now() + timedelta(hours=1)
        )
        today = date.today()
        tomorrow = date.today() + timedelta(days=1)
        venue_id = stock.offer.venue.id
        expected_num_queries = 1  # user
        expected_num_queries += 1  # offers
        expected_num_queries += 1  # deposit
        expected_num_queries += 1  # user bookings
        client.with_token(user)
        with assert_num_queries(expected_num_queries):
            response = client.get(
                f"/native/v1/venue/{venue_id}/movie/calendar/me", params={"from": today, "to": tomorrow}
            )
            assert response.status_code == 200

        calendar = response.json["calendar"]
        assert calendar == {
            today.isoformat(): [
                {
                    "duration": 116,
                    "genres": [],
                    "last30DaysBookings": 0,
                    "movieName": stock.offer.name,
                    "offerId": stock.offer.id,
                    "thumbUrl": None,
                    "dayScreenings": [
                        {
                            "beginningDatetime": date_utils.format_into_utc_date(stock.beginningDatetime),
                            "bookability": "BOOKABLE",
                            "features": [],
                            "price": 10.1,
                            "stockId": stock.id,
                        }
                    ],
                    "nextScreening": {
                        "beginningDatetime": date_utils.format_into_utc_date(stock.beginningDatetime),
                        "bookability": "BOOKABLE",
                        "features": [],
                        "price": 10.1,
                        "stockId": stock.id,
                    },
                }
            ],
            tomorrow.isoformat(): [
                {
                    "duration": 116,
                    "genres": [],
                    "last30DaysBookings": 0,
                    "movieName": stock.offer.name,
                    "offerId": stock.offer.id,
                    "thumbUrl": None,
                    "dayScreenings": [],
                    "nextScreening": {
                        "beginningDatetime": date_utils.format_into_utc_date(stock.beginningDatetime),
                        "bookability": "BOOKABLE",
                        "features": [],
                        "price": 10.1,
                        "stockId": stock.id,
                    },
                }
            ],
        }

    def test_sold_out_screening(self, client):
        user = users_factories.BeneficiaryFactory()
        product = offers_factories.ProductFactory(subcategoryId=subcategories.SEANCE_CINE.id, durationMinutes=116)
        stock = offers_factories.EventStockFactory(
            quantity=0, offer__product=product, beginningDatetime=datetime.now() + timedelta(hours=1)
        )
        today = date.today()
        tomorrow = date.today() + timedelta(days=1)
        venue_id = stock.offer.venue.id
        expected_num_queries = 1  # user
        expected_num_queries += 1  # offers
        expected_num_queries += 1  # deposits
        expected_num_queries += 1  # user bookings
        client.with_token(user)
        with assert_num_queries(expected_num_queries):
            response = client.get(
                f"/native/v1/venue/{venue_id}/movie/calendar/me", params={"from": today, "to": tomorrow}
            )
            assert response.status_code == 200

        calendar = response.json["calendar"]
        print(calendar)
        assert calendar[today.isoformat()][0]["dayScreenings"][0]["bookability"] == "STOCK_IS_SOLD_OUT"
        assert calendar[today.isoformat()][0]["nextScreening"]["bookability"] == "STOCK_IS_SOLD_OUT"

    @pytest.mark.features(DISABLE_BOOST_EXTERNAL_BOOKINGS=True)
    def test_disabled_booking(self, client):
        user = users_factories.BeneficiaryFactory()
        product = offers_factories.ProductFactory(subcategoryId=subcategories.SEANCE_CINE.id, durationMinutes=116)
        disabled_provider = get_provider_by_local_class("BoostStocks")
        stock = offers_factories.EventStockFactory(
            offer__lastProvider=disabled_provider,
            offer__product=product,
            beginningDatetime=datetime.now() + timedelta(hours=1),
        )
        today = date.today()
        tomorrow = date.today() + timedelta(days=1)
        venue_id = stock.offer.venue.id
        expected_num_queries = 1  # user
        expected_num_queries += 1  # offers
        expected_num_queries += 1  # deposits
        expected_num_queries += 1  # user bookings
        client.with_token(user)
        with assert_num_queries(expected_num_queries):
            response = client.get(
                f"/native/v1/venue/{venue_id}/movie/calendar/me", params={"from": today, "to": tomorrow}
            )
            assert response.status_code == 200

        calendar = response.json["calendar"]
        assert calendar[today.isoformat()][0]["dayScreenings"][0]["bookability"] == "STOCK_BOOKING_IS_DISABLED"
        assert calendar[today.isoformat()][0]["nextScreening"]["bookability"] == "STOCK_BOOKING_IS_DISABLED"

    def test_when_user_cannot_book(self, client):
        user = users_factories.UserFactory(age=100)
        product = offers_factories.ProductFactory(subcategoryId=subcategories.SEANCE_CINE.id, durationMinutes=116)
        disabled_provider = get_provider_by_local_class("BoostStocks")
        stock = offers_factories.EventStockFactory(
            offer__lastProvider=disabled_provider,
            offer__product=product,
            beginningDatetime=datetime.now() + timedelta(hours=1),
        )
        today = date.today()
        tomorrow = date.today() + timedelta(days=1)
        venue_id = stock.offer.venue.id
        expected_num_queries = 1  # user
        expected_num_queries += 1  # offers
        expected_num_queries += 1  # deposits
        client.with_token(user)
        with assert_num_queries(expected_num_queries):
            response = client.get(
                f"/native/v1/venue/{venue_id}/movie/calendar/me", params={"from": today, "to": tomorrow}
            )
            assert response.status_code == 200

        calendar = response.json["calendar"]
        assert calendar[today.isoformat()][0]["dayScreenings"][0]["bookability"] == "USER_CANNOT_BOOK"
        assert calendar[today.isoformat()][0]["nextScreening"]["bookability"] == "USER_CANNOT_BOOK"

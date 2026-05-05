from datetime import datetime
from datetime import timezone
from typing import Any
from unittest.mock import patch

import pytest
from dateutil.tz import tz

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.bookings.models as bookings_models
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.core.categories import subcategories
from pcapi.core.external_bookings.factories import ExternalBookingFactory
from pcapi.core.testing import assert_num_queries
from pcapi.utils.date import utc_datetime_to_department_timezone


BOOKING_PERIOD_PARAMS = "bookingPeriodBeginningDate=2020-08-10&bookingPeriodEndingDate=2020-08-12"

BOOKING_PERIOD = (datetime(2020, 8, 10, tzinfo=timezone.utc).date(), datetime(2020, 8, 12, tzinfo=timezone.utc).date())


class GetAllBookingsTest:
    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.core.bookings.repository.find_by_venue")
    def test_call_repository_with_user_and_page(self, find_by_venue, client: Any):
        find_by_venue.return_value = ([], 0)
        pro = users_factories.ProFactory()
        offerer = offerers_factories.UserOffererFactory(user=pro).offerer
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        venue_id = venue.id

        auth_client = client.with_session_auth(pro.email)
        # get user_session + user
        # check has_access
        with assert_num_queries(2):
            response = auth_client.get(
                f"/bookings/pro?{BOOKING_PERIOD_PARAMS}&bookingStatusFilter=booked&page=3&venueId={venue_id}"
            )
            assert response.status_code == 200

        find_by_venue.assert_called_once_with(
            pro_user_id=pro.id,
            venue_id=venue_id,
            booking_period=BOOKING_PERIOD,
            status_filter=bookings_models.BookingStatusFilter.BOOKED,
            event_date=None,
            offer_id=None,
            offerer_address_id=None,
            page=3,
            per_page_limit=500,
        )

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.core.bookings.repository.find_by_venue")
    def test_call_repository_with_page_1(self, find_by_venue, client: Any):
        find_by_venue.return_value = ([], 0)
        pro = users_factories.ProFactory()
        offerer = offerers_factories.UserOffererFactory(user=pro).offerer
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        venue_id = venue.id

        auth_client = client.with_session_auth(pro.email)
        # get user_session + user
        # check has_access
        with assert_num_queries(2):
            response = auth_client.get(
                f"/bookings/pro?{BOOKING_PERIOD_PARAMS}&bookingStatusFilter=booked&venueId={venue_id}"
            )
            assert response.status_code == 200

        find_by_venue.assert_called_once_with(
            pro_user_id=pro.id,
            venue_id=venue_id,
            booking_period=BOOKING_PERIOD,
            status_filter=bookings_models.BookingStatusFilter.BOOKED,
            event_date=None,
            offer_id=None,
            offerer_address_id=None,
            page=1,
            per_page_limit=500,
        )

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.core.bookings.repository.find_by_venue")
    def test_call_repository_with_venue_id(self, find_by_venue, client: Any):
        find_by_venue.return_value = ([], 0)
        pro = users_factories.ProFactory()
        offerer = offerers_factories.UserOffererFactory(user=pro).offerer
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        venue_id = venue.id

        auth_client = client.with_session_auth(pro.email)
        # get user_session + user
        # check has_access
        with assert_num_queries(2):
            response = auth_client.get(
                f"/bookings/pro?{BOOKING_PERIOD_PARAMS}&bookingStatusFilter=booked&venueId={venue_id}"
            )
            assert response.status_code == 200

        find_by_venue.assert_called_once_with(
            pro_user_id=pro.id,
            venue_id=venue_id,
            booking_period=BOOKING_PERIOD,
            status_filter=bookings_models.BookingStatusFilter.BOOKED,
            event_date=None,
            offer_id=None,
            offerer_address_id=None,
            page=1,
            per_page_limit=500,
        )

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.core.bookings.repository.find_by_venue")
    def test_call_repository_with_offer_id(self, find_by_venue, client: Any):
        find_by_venue.return_value = ([], 0)
        pro = users_factories.ProFactory()
        offerer = offerers_factories.UserOffererFactory(user=pro).offerer
        offer = offers_factories.OfferFactory(venue__managingOfferer=offerer)

        venue_id = offer.venue.id
        offer_id = offer.id
        auth_client = client.with_session_auth(pro.email)
        # get user_session + user
        # check has_access
        with assert_num_queries(2):
            response = auth_client.get(
                f"/bookings/pro?{BOOKING_PERIOD_PARAMS}&bookingStatusFilter=booked&venueId={venue_id}&offerId={offer_id}"
            )
            assert response.status_code == 200

        find_by_venue.assert_called_once_with(
            pro_user_id=pro.id,
            venue_id=venue_id,
            booking_period=BOOKING_PERIOD,
            status_filter=bookings_models.BookingStatusFilter.BOOKED,
            event_date=None,
            offer_id=offer.id,
            offerer_address_id=None,
            page=1,
            per_page_limit=500,
        )


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    expected_num_queries = 1  # Fetch the session + user
    expected_num_queries += 1  # Check has_access
    # the user timezones query is duplicated for better readability
    expected_num_queries += 1  # Fetch user timezones (for the count)
    expected_num_queries += 1  # Fetch user timezones (for the query)
    expected_num_queries += 1  # CTE built over booking, stock and external_booking
    expected_num_queries += 1  # 4.external_booking

    @pytest.mark.parametrize(
        "offerer_factory", [offerers_factories.OffererFactory, offerers_factories.ClosedOffererFactory]
    )
    def test_when_user_is_linked_to_a_valid_offerer(self, client: Any, offerer_factory):
        stock = offers_factories.StockFactory(
            offer__ean="1234567891234",
            offer__venue__managingOfferer=offerer_factory(),
        )
        used_booking = bookings_factories.UsedBookingFactory(
            dateCreated=datetime(2020, 8, 11, 12, 0, 0),
            dateUsed=datetime(2020, 8, 13, 12, 0, 0),
            token="ABCDEF",
            user__email="beneficiary@example.com",
            user__firstName="Hermione",
            user__lastName="Granger",
            user__phoneNumber="0100000000",
            stock=stock,
        )
        offerer = used_booking.offerer
        book_stock = offers_factories.StockFactory(
            offer__subcategoryId=subcategories.LIVRE_PAPIER.id, offer__venue=stock.offer.venue
        )
        confirmed_book_booking = bookings_factories.BookingFactory(
            dateCreated=datetime(2020, 8, 11, 11, 0, 0),
            token="GHIJKL",
            status=bookings_models.BookingStatus.CONFIRMED,
            user__email="ron@example.com",
            user__firstName="Ron",
            user__lastName="Weasley",
            user__phoneNumber="0200000000",
            stock=book_stock,
        )
        pro_user = users_factories.ProFactory(email="pro@example.com")
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        venue_id = used_booking.stock.offer.venue.id

        client = client.with_session_auth(pro_user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(
                f"/bookings/pro?{BOOKING_PERIOD_PARAMS}&bookingStatusFilter=booked&venueId={venue_id}"
            )
            assert response.status_code == 200
        expected_bookings_recap = [
            {
                "stock": {
                    "offerName": used_booking.stock.offer.name,
                    "offerId": used_booking.stock.offer.id,
                    "offerIsEducational": False,
                    "eventBeginningDatetime": None,
                    "offerEan": "1234567891234",
                },
                "beneficiary": {
                    "email": "beneficiary@example.com",
                    "firstname": "Hermione",
                    "lastname": "Granger",
                    "phonenumber": "+33100000000",
                },
                "bookingDate": used_booking.dateCreated.astimezone(tz.gettz("Europe/Paris")).isoformat(),
                "bookingAmount": 10.1,
                "bookingPriceCategoryLabel": None,
                "bookingToken": "ABCDEF",
                "bookingStatus": "validated",
                "bookingIsDuo": False,
                "bookingStatusHistory": [
                    {
                        "status": "booked",
                        "date": used_booking.dateCreated.astimezone(tz.gettz("Europe/Paris")).isoformat(),
                    },
                    {
                        "status": "validated",
                        "date": used_booking.dateUsed.astimezone(tz.gettz("Europe/Paris")).isoformat(),
                    },
                ],
            },
            {
                "stock": {
                    "offerName": confirmed_book_booking.stock.offer.name,
                    "offerId": confirmed_book_booking.stock.offer.id,
                    "offerIsEducational": False,
                    "eventBeginningDatetime": None,
                    "offerEan": None,
                },
                "beneficiary": {
                    "email": "ron@example.com",
                    "firstname": "Ron",
                    "lastname": "Weasley",
                    "phonenumber": "+33200000000",
                },
                "bookingDate": confirmed_book_booking.dateCreated.astimezone(tz.gettz("Europe/Paris")).isoformat(),
                "bookingAmount": 10.1,
                "bookingPriceCategoryLabel": None,
                "bookingToken": None,
                "bookingStatus": "booked",
                "bookingIsDuo": False,
                "bookingStatusHistory": [
                    {
                        "status": "booked",
                        "date": confirmed_book_booking.dateCreated.astimezone(tz.gettz("Europe/Paris")).isoformat(),
                    },
                ],
            },
        ]
        assert response.status_code == 200
        assert response.json["bookingsRecap"] == expected_bookings_recap
        assert response.json["page"] == 1
        assert response.json["pages"] == 1
        assert response.json["total"] == 2

    def test_should_return_duo_booking_twice(self, client: Any):
        duo_booking = bookings_factories.UsedBookingFactory(
            dateCreated=datetime(2020, 8, 11, 12, 0, 0),
            quantity=2,
        )
        pro_user = users_factories.ProFactory(email="pro@example.com")
        offerers_factories.UserOffererFactory(user=pro_user, offerer=duo_booking.offerer)
        venue_id = duo_booking.stock.offer.venue.id
        client = client.with_session_auth(pro_user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(
                f"/bookings/pro?{BOOKING_PERIOD_PARAMS}&bookingStatusFilter=booked&venueId={venue_id}"
            )
            assert response.status_code == 200

        assert response.json["page"] == 1
        assert response.json["pages"] == 1
        assert response.json["total"] == 2
        assert len(response.json["bookingsRecap"]) == 2
        assert response.json["bookingsRecap"][0] == response.json["bookingsRecap"][1]
        assert response.json["bookingsRecap"][0]["bookingIsDuo"] is True

    def when_requested_with_event_date(self, client: Any):
        requested_date = "2020-08-12"
        stock = offers_factories.EventStockFactory(beginningDatetime=datetime(2020, 8, 12))
        booking = bookings_factories.BookingFactory(stock=stock, token="AAAAAA", dateCreated=datetime(2020, 8, 11))
        bookings_factories.BookingFactory(stock=offers_factories.EventStockFactory(), token="BBBBBB")
        pro_user = users_factories.ProFactory(email="pro@example.com")
        offerer = stock.offer.venue.managingOfferer
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        venue_id = stock.offer.venue.id

        client = client.with_session_auth(pro_user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(
                f"/bookings/pro?{BOOKING_PERIOD_PARAMS}&bookingStatusFilter=booked&eventDate={requested_date}&venueId={venue_id}"
            )

        assert response.status_code == 200
        assert len(response.json["bookingsRecap"]) == 1
        assert response.json["bookingsRecap"][0]["bookingToken"] == booking.token
        assert response.json["page"] == 1
        assert response.json["pages"] == 1
        assert response.json["total"] == 1

    def when_requested_with_booking_period_dates(self, client: Any):
        booking_date = datetime(2020, 8, 12, 20, 00, tzinfo=timezone.utc)
        booking_period_beginning_date = "2020-08-10"
        booking_period_ending_date = "2020-08-12"
        booking = bookings_factories.BookingFactory(dateCreated=booking_date, token="AAAAAA")
        bookings_factories.BookingFactory(token="BBBBBB")
        pro_user = users_factories.ProFactory(email="pro@example.com")
        offerers_factories.UserOffererFactory(user=pro_user, offerer=booking.offerer)

        venue_id = booking.venue.id
        client = client.with_session_auth(pro_user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(
                "/bookings/pro?bookingPeriodBeginningDate=%s&bookingPeriodEndingDate=%s&bookingStatusFilter=booked&venueId=%s"
                % (booking_period_beginning_date, booking_period_ending_date, venue_id)
            )

        assert response.status_code == 200
        assert len(response.json["bookingsRecap"]) == 1
        assert response.json["bookingsRecap"][0]["bookingDate"] == datetime.isoformat(
            utc_datetime_to_department_timezone(
                booking.dateCreated, booking.venue.offererAddress.address.departmentCode
            )
        )

        assert response.json["page"] == 1
        assert response.json["pages"] == 1
        assert response.json["total"] == 1

    def test_should_not_return_booking_token_when_booking_is_external(self, client: Any):
        booking_date = datetime(2020, 8, 11, 10, 00, tzinfo=timezone.utc)
        externalbooking = ExternalBookingFactory(
            booking__dateCreated=booking_date,
            booking__status=bookings_models.BookingStatus.USED,
            booking__dateUsed=datetime(2020, 8, 11, 20, 00, tzinfo=timezone.utc),
        )
        pro_user = users_factories.ProFactory(email="pro@example.com")
        offerers_factories.UserOffererFactory(user=pro_user, offerer=externalbooking.booking.offerer)

        # when
        venue_id = externalbooking.booking.venue.id
        client = client.with_session_auth(pro_user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(f"/bookings/pro?{BOOKING_PERIOD_PARAMS}&venueId={venue_id}")
            assert response.status_code == 200

        assert response.json["bookingsRecap"][0]["bookingToken"] is None


@pytest.mark.usefixtures("db_session")
class Returns400Test:
    num_queries = 2  # session + rollback

    def when_page_number_is_not_a_number(self, client: Any):
        pro = users_factories.ProFactory()

        client = client.with_session_auth(pro.email)
        with assert_num_queries(self.num_queries):
            response = client.get(f"/bookings/pro?{BOOKING_PERIOD_PARAMS}&page=not-a-number")
            assert response.status_code == 400

        assert response.json["page"] == ["Saisissez un entier valide"]

    def when_date_format_incorrect(self, client: Any):
        pro = users_factories.ProFactory()

        client = client.with_session_auth(pro.email)
        with assert_num_queries(self.num_queries):
            response = client.get(
                "/bookings/pro?bookingPeriodBeginningDate=20234-08-10&bookingPeriodEndingDate=2020-08-12"
            )
            assert response.status_code == 400

    def when_beginning_date_is_out_of_range(self, client: Any):
        # Ensure that we don't crash because of timezone shift
        user_offerer = offerers_factories.UserOffererFactory()
        bookings_factories.UsedBookingFactory(stock__offer__venue__managingOfferer=user_offerer.offerer)

        client = client.with_session_auth(user_offerer.user.email)
        with assert_num_queries(self.num_queries):
            response = client.get(
                "/bookings/pro?bookingPeriodBeginningDate=0001-01-01&bookingPeriodEndingDate=2025-11-21"
            )
            assert response.status_code == 400

    def when_ending_date_is_out_of_range(self, client: Any):
        # Ensure that we don't crash because of timezone shift
        user_offerer = offerers_factories.UserOffererFactory()
        bookings_factories.UsedBookingFactory(stock__offer__venue__managingOfferer=user_offerer.offerer)

        client = client.with_session_auth(user_offerer.user.email)
        with assert_num_queries(self.num_queries):
            response = client.get(
                "/bookings/pro?bookingPeriodBeginningDate=2025-11-21&bookingPeriodEndingDate=0001-01-01"
            )
            assert response.status_code == 400

    def when_booking_period_and_event_date_is_not_given(self, client: Any):
        pro = users_factories.ProFactory()
        offerer = offerers_factories.UserOffererFactory(user=pro).offerer
        offerer_id = offerer.id

        client = client.with_session_auth(pro.email)
        with assert_num_queries(self.num_queries):
            response = client.get(f"/bookings/pro?offererId={offerer_id}")
            assert response.status_code == 400

        assert response.json["eventDate"] == ["Ce champ est obligatoire si aucune période n'est renseignée."]
        assert response.json["bookingPeriodBeginningDate"] == [
            "Ce champ est obligatoire si la date d'évènement n'est renseignée"
        ]
        assert response.json["bookingPeriodEndingDate"] == [
            "Ce champ est obligatoire si la date d'évènement n'est renseignée"
        ]

    def when_venue_id_is_missing(self, client: Any):
        pro = users_factories.ProFactory()
        client = client.with_session_auth(pro.email)
        with assert_num_queries(self.num_queries):
            response = client.get(f"/bookings/pro?{BOOKING_PERIOD_PARAMS}&bookingStatusFilter=booked")
            assert response.status_code == 400

        assert response.json["venueId"] == ["Ce champ est obligatoire"]


@pytest.mark.usefixtures("db_session")
class Returns404Test:
    def when_user_has_no_access_to_venue(self, client: Any):
        pro = users_factories.ProFactory()
        venue = offerers_factories.VenueFactory()
        venue_id = venue.id

        client = client.with_session_auth(pro.email)

        response = client.get(f"/bookings/pro?{BOOKING_PERIOD_PARAMS}&bookingStatusFilter=booked&venueId={venue_id}")
        assert response.status_code == 404

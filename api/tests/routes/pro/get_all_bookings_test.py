from datetime import datetime
from datetime import timezone
from typing import Any
from unittest.mock import patch

from dateutil.tz import tz
import pytest

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.bookings.models as bookings_models
from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.external_bookings.factories import ExternalBookingFactory
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.testing import assert_no_duplicated_queries
from pcapi.core.testing import assert_num_queries
import pcapi.core.users.factories as users_factories
from pcapi.utils.date import utc_datetime_to_department_timezone


BOOKING_PERIOD_PARAMS = "bookingPeriodBeginningDate=2020-08-10&bookingPeriodEndingDate=2020-08-12"

BOOKING_PERIOD = (datetime(2020, 8, 10, tzinfo=timezone.utc).date(), datetime(2020, 8, 12, tzinfo=timezone.utc).date())


class GetAllBookingsTest:
    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.core.bookings.repository.find_by_pro_user")
    def test_call_repository_with_user_and_page(self, find_by_pro_user, client: Any):
        find_by_pro_user.return_value = ([], 0)
        pro = users_factories.ProFactory()

        auth_client = client.with_session_auth(pro.email)
        # get user_session
        # get user
        with assert_num_queries(2):
            response = auth_client.get(f"/bookings/pro?{BOOKING_PERIOD_PARAMS}&bookingStatusFilter=booked&page=3")
            assert response.status_code == 200

        find_by_pro_user.assert_called_once_with(
            user=pro,
            booking_period=BOOKING_PERIOD,
            status_filter=bookings_models.BookingStatusFilter.BOOKED,
            event_date=None,
            venue_id=None,
            offer_id=None,
            offerer_address_id=None,
            page=3,
            per_page_limit=1000,
        )

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.core.bookings.repository.find_by_pro_user")
    def test_call_repository_with_page_1(self, find_by_pro_user, client: Any):
        find_by_pro_user.return_value = ([], 0)
        pro = users_factories.ProFactory()

        auth_client = client.with_session_auth(pro.email)
        # get user_session
        # get user
        with assert_num_queries(2):
            response = auth_client.get(f"/bookings/pro?{BOOKING_PERIOD_PARAMS}&bookingStatusFilter=booked")
            assert response.status_code == 200

        find_by_pro_user.assert_called_once_with(
            user=pro,
            booking_period=BOOKING_PERIOD,
            status_filter=bookings_models.BookingStatusFilter.BOOKED,
            event_date=None,
            venue_id=None,
            offer_id=None,
            offerer_address_id=None,
            page=1,
            per_page_limit=1000,
        )

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.core.bookings.repository.find_by_pro_user")
    def test_call_repository_with_venue_id(self, find_by_pro_user, client: Any):
        find_by_pro_user.return_value = ([], 0)
        pro = users_factories.ProFactory()
        venue = offerers_factories.VenueFactory()

        auth_client = client.with_session_auth(pro.email)
        # get venue
        # get user_session
        # get user
        with assert_num_queries(3):
            response = auth_client.get(
                f"/bookings/pro?{BOOKING_PERIOD_PARAMS}&bookingStatusFilter=booked&venueId={venue.id}"
            )
            assert response.status_code == 200

        find_by_pro_user.assert_called_once_with(
            user=pro,
            booking_period=BOOKING_PERIOD,
            status_filter=bookings_models.BookingStatusFilter.BOOKED,
            event_date=None,
            venue_id=venue.id,
            offer_id=None,
            offerer_address_id=None,
            page=1,
            per_page_limit=1000,
        )

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.core.bookings.repository.find_by_pro_user")
    def test_call_repository_with_offer_id(self, find_by_pro_user, client: Any):
        find_by_pro_user.return_value = ([], 0)
        pro = users_factories.ProFactory()
        offer = offers_factories.OfferFactory()

        auth_client = client.with_session_auth(pro.email)
        # get offer
        # get user_session
        # get user
        with assert_num_queries(3):
            response = auth_client.get(
                f"/bookings/pro?{BOOKING_PERIOD_PARAMS}&bookingStatusFilter=booked&offerId={offer.id}"
            )
            assert response.status_code == 200

        find_by_pro_user.assert_called_once_with(
            user=pro,
            booking_period=BOOKING_PERIOD,
            status_filter=bookings_models.BookingStatusFilter.BOOKED,
            event_date=None,
            venue_id=None,
            offer_id=offer.id,
            offerer_address_id=None,
            page=1,
            per_page_limit=1000,
        )


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    # 1.session
    # 2.user
    # 3.anon_1
    # 4.external_booking
    expected_num_queries = 4

    def when_user_is_admin(self, client: Any):
        admin = users_factories.AdminFactory()
        user_offerer = offerers_factories.UserOffererFactory()
        bookings_factories.BookingFactory(
            dateCreated=datetime(2020, 8, 11, 12, 0, 0),
            stock__offer__venue__managingOfferer=user_offerer.offerer,
        )

        client = client.with_session_auth(admin.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(f"/bookings/pro?{BOOKING_PERIOD_PARAMS}&bookingStatusFilter=booked")
            assert response.status_code == 200
            assert len(response.json["bookingsRecap"]) == 1

    def test_when_user_is_linked_to_a_valid_offerer(self, client: Any):
        stock = offers_factories.StockFactory(offer__extraData={"ean": "1234567891234"})
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

        client = client.with_session_auth(pro_user.email)
        with assert_num_queries(self.expected_num_queries):
            with assert_no_duplicated_queries():
                response = client.get(f"/bookings/pro?{BOOKING_PERIOD_PARAMS}&bookingStatusFilter=booked")
                assert response.status_code == 200

        expected_bookings_recap = [
            {
                "stock": {
                    "stockIdentifier": used_booking.stock.id,
                    "offerName": used_booking.stock.offer.name,
                    "offerId": used_booking.stock.offer.id,
                    "offerIsEducational": False,
                    "eventBeginningDatetime": None,
                    "offerIsbn": "1234567891234",
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
                    "stockIdentifier": confirmed_book_booking.stock.id,
                    "offerName": confirmed_book_booking.stock.offer.name,
                    "offerId": confirmed_book_booking.stock.offer.id,
                    "offerIsEducational": False,
                    "eventBeginningDatetime": None,
                    "offerIsbn": None,
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

    def when_requested_with_event_date(self, client: Any):
        requested_date = "2020-08-12"
        stock = offers_factories.EventStockFactory(beginningDatetime=datetime(2020, 8, 12))
        booking = bookings_factories.BookingFactory(stock=stock, token="AAAAAA", dateCreated=datetime(2020, 8, 11))
        bookings_factories.BookingFactory(stock=offers_factories.EventStockFactory(), token="BBBBBB")
        pro_user = users_factories.ProFactory(email="pro@example.com")
        offerer = stock.offer.venue.managingOfferer
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)

        client = client.with_session_auth(pro_user.email)
        with assert_num_queries(self.expected_num_queries):
            with assert_no_duplicated_queries():
                response = client.get(
                    f"/bookings/pro?{BOOKING_PERIOD_PARAMS}&bookingStatusFilter=booked&eventDate={requested_date}"
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

        client = client.with_session_auth(pro_user.email)
        with assert_num_queries(self.expected_num_queries):
            with assert_no_duplicated_queries():
                response = client.get(
                    "/bookings/pro?bookingPeriodBeginningDate=%s&bookingPeriodEndingDate=%s&bookingStatusFilter=booked"
                    % (booking_period_beginning_date, booking_period_ending_date)
                )

        assert response.status_code == 200
        assert len(response.json["bookingsRecap"]) == 1
        assert response.json["bookingsRecap"][0]["bookingDate"] == datetime.isoformat(
            utc_datetime_to_department_timezone(booking.dateCreated, booking.venue.departementCode)
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
        client = client.with_session_auth(pro_user.email)
        expected_num_queries = 4  # user + session + SELECT DISTINCT booking + bookingToken
        with assert_num_queries(expected_num_queries):
            response = client.get(f"/bookings/pro?{BOOKING_PERIOD_PARAMS}")
            assert response.status_code == 200

        assert response.json["bookingsRecap"][0]["bookingToken"] is None


@pytest.mark.usefixtures("db_session")
class Returns400Test:
    def when_page_number_is_not_a_number(self, client: Any):
        pro = users_factories.ProFactory()

        client = client.with_session_auth(pro.email)
        with assert_num_queries(2):  # user + session
            response = client.get(f"/bookings/pro?{BOOKING_PERIOD_PARAMS}&page=not-a-number")
            assert response.status_code == 400

        assert response.json["page"] == ["Saisissez un nombre valide"]

    def when_date_format_incorrect(self, client: Any):
        pro = users_factories.ProFactory()

        client = client.with_session_auth(pro.email)
        with assert_num_queries(2):  # user + session
            response = client.get(
                "/bookings/pro?bookingPeriodBeginningDate=20234-08-10&bookingPeriodEndingDate=2020-08-12"
            )
            assert response.status_code == 400

    def when_booking_period_and_event_date_is_not_given(self, client: Any):
        pro = users_factories.ProFactory()

        client = client.with_session_auth(pro.email)
        with assert_num_queries(2):  # user + session
            response = client.get("/bookings/pro")
            assert response.status_code == 400

        assert response.json["eventDate"] == ["Ce champ est obligatoire si aucune période n'est renseignée."]
        assert response.json["bookingPeriodBeginningDate"] == [
            "Ce champ est obligatoire si la date d'évènement n'est renseignée"
        ]
        assert response.json["bookingPeriodEndingDate"] == [
            "Ce champ est obligatoire si la date d'évènement n'est renseignée"
        ]

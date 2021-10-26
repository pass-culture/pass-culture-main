from datetime import datetime
from datetime import timezone
from unittest.mock import patch

from dateutil.tz import tz
import pytest

from pcapi.core import testing
import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.factories import VenueFactory
from pcapi.core.testing import assert_num_queries
import pcapi.core.users.factories as users_factories
from pcapi.utils.date import format_into_timezoned_date
from pcapi.utils.date import utc_datetime_to_department_timezone
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


BOOKING_PERIOD_PARAMS = "bookingPeriodBeginningDate=2020-08-10&bookingPeriodEndingDate=2020-08-12"

BOOKING_PERIOD = (datetime(2020, 8, 10, tzinfo=timezone.utc).date(), datetime(2020, 8, 12, tzinfo=timezone.utc).date())


class GetAllBookingsTest:
    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.core.bookings.repository.find_by_pro_user_id")
    def test_call_repository_with_user_and_page(self, find_by_pro_user_id, app):
        pro = users_factories.ProFactory()
        TestClient(app.test_client()).with_session_auth(pro.email).get(f"/bookings/pro?{BOOKING_PERIOD_PARAMS}&page=3")
        find_by_pro_user_id.assert_called_once_with(
            user_id=pro.id,
            booking_period=BOOKING_PERIOD,
            event_date=None,
            venue_id=None,
            page=3,
            is_user_admin=False,
        )

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.core.bookings.repository.find_by_pro_user_id")
    def test_call_repository_with_page_1(self, find_by_pro_user_id, app):
        pro = users_factories.ProFactory()
        TestClient(app.test_client()).with_session_auth(pro.email).get(f"/bookings/pro?{BOOKING_PERIOD_PARAMS}")
        find_by_pro_user_id.assert_called_once_with(
            user_id=pro.id,
            booking_period=BOOKING_PERIOD,
            event_date=None,
            venue_id=None,
            page=1,
            is_user_admin=False,
        )

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.core.bookings.repository.find_by_pro_user_id")
    def test_call_repository_with_venue_id(self, find_by_pro_user_id, app):
        # Given
        pro = users_factories.ProFactory()
        venue = VenueFactory()

        # When
        TestClient(app.test_client()).with_session_auth(pro.email).get(
            f"/bookings/pro?{BOOKING_PERIOD_PARAMS}&venueId={humanize(venue.id)}"
        )

        # Then
        find_by_pro_user_id.assert_called_once_with(
            user_id=pro.id,
            booking_period=BOOKING_PERIOD,
            event_date=None,
            venue_id=venue.id,
            page=1,
            is_user_admin=False,
        )


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    def when_user_is_admin(self, app):
        admin = users_factories.AdminFactory()
        user_offerer = offers_factories.UserOffererFactory()
        bookings_factories.BookingFactory(
            dateCreated=datetime(2020, 8, 11, 12, 0, 0),
            stock__offer__venue__managingOfferer=user_offerer.offerer,
        )

        client = TestClient(app.test_client()).with_session_auth(admin.email)
        response = client.get(f"/bookings/pro?{BOOKING_PERIOD_PARAMS}")

        assert response.status_code == 200
        assert len(response.json["bookings_recap"]) == 1

    def when_booking_is_educational(self, app):
        admin = users_factories.AdminFactory()
        user_offerer = offers_factories.UserOffererFactory()
        bookings_factories.EducationalBookingFactory(
            dateCreated=datetime(2020, 8, 11, 12, 0, 0),
            stock__offer__venue__managingOfferer=user_offerer.offerer,
            educationalBooking__educationalRedactor__firstName="Georges",
            educationalBooking__educationalRedactor__lastName="Moustaki",
            educationalBooking__educationalRedactor__email="redactor@email.com",
        )

        client = TestClient(app.test_client()).with_session_auth(admin.email)
        response = client.get(f"/bookings/pro?{BOOKING_PERIOD_PARAMS}")

        assert response.status_code == 200
        assert response.json["bookings_recap"][0]["stock"]["offer_is_educational"] is True
        assert response.json["bookings_recap"][0]["beneficiary"] == {
            "email": "redactor@email.com",
            "firstname": "Georges",
            "lastname": "Moustaki",
            "phonenumber": None,
        }

    def when_user_is_linked_to_a_valid_offerer(self, app):
        booking = bookings_factories.UsedIndividualBookingFactory(
            dateCreated=datetime(2020, 8, 11, 12, 0, 0),
            dateUsed=datetime(2020, 8, 13, 12, 0, 0),
            token="ABCDEF",
            individualBooking__user__email="beneficiary@example.com",
            individualBooking__user__firstName="Hermione",
            individualBooking__user__lastName="Granger",
            individualBooking__user__phoneNumber="0100000000",
        )
        pro_user = users_factories.ProFactory(email="pro@example.com")
        offers_factories.UserOffererFactory(user=pro_user, offerer=booking.offerer)

        client = TestClient(app.test_client()).with_session_auth(pro_user.email)
        with assert_num_queries(testing.AUTHENTICATION_QUERIES + 2):
            response = client.get(f"/bookings/pro?{BOOKING_PERIOD_PARAMS}")

        expected_bookings_recap = [
            {
                "stock": {
                    "offer_name": booking.stock.offer.name,
                    "offer_identifier": humanize(booking.stock.offer.id),
                    "event_beginning_datetime": None,
                    "offer_isbn": None,
                    "offer_is_educational": False,
                },
                "beneficiary": {
                    "email": "beneficiary@example.com",
                    "firstname": "Hermione",
                    "lastname": "Granger",
                    "phonenumber": "0100000000",
                },
                "booking_date": format_into_timezoned_date(
                    booking.dateCreated.astimezone(tz.gettz("Europe/Paris")),
                ),
                "booking_amount": 10.0,
                "booking_token": "ABCDEF",
                "booking_status": "validated",
                "booking_is_duo": False,
                "booking_status_history": [
                    {
                        "status": "booked",
                        "date": format_into_timezoned_date(
                            booking.dateCreated.astimezone(tz.gettz("Europe/Paris")),
                        ),
                    },
                    {
                        "status": "validated",
                        "date": format_into_timezoned_date(
                            booking.dateUsed.astimezone(tz.gettz("Europe/Paris")),
                        ),
                    },
                ],
                "offerer": {
                    "name": booking.offerer.name,
                },
                "venue": {
                    "identifier": humanize(booking.venueId),
                    "is_virtual": booking.venue.isVirtual,
                    "name": booking.venue.name,
                },
            }
        ]
        assert response.status_code == 200
        assert response.json["bookings_recap"] == expected_bookings_recap
        assert response.json["page"] == 1
        assert response.json["pages"] == 1
        assert response.json["total"] == 1

    def when_requested_event_date_is_iso_format(self, app):
        requested_date = datetime(2020, 8, 12, 20, 00)
        requested_date_iso_format = "2020-08-12T00:00:00Z"
        stock = offers_factories.EventStockFactory(beginningDatetime=requested_date)
        booking = bookings_factories.BookingFactory(stock=stock, token="AAAAAA", dateCreated=datetime(2020, 8, 11))
        bookings_factories.BookingFactory(stock=offers_factories.EventStockFactory(), token="BBBBBB")
        pro_user = users_factories.ProFactory(email="pro@example.com")
        offerer = stock.offer.venue.managingOfferer
        offers_factories.UserOffererFactory(user=pro_user, offerer=offerer)

        client = TestClient(app.test_client()).with_session_auth(pro_user.email)
        with assert_num_queries(testing.AUTHENTICATION_QUERIES + 2):
            response = client.get(f"/bookings/pro?{BOOKING_PERIOD_PARAMS}&eventDate={requested_date_iso_format}")

        assert response.status_code == 200
        assert len(response.json["bookings_recap"]) == 1
        assert response.json["bookings_recap"][0]["booking_token"] == booking.token
        assert response.json["page"] == 1
        assert response.json["pages"] == 1
        assert response.json["total"] == 1

    def when_requested_booking_period_dates_are_iso_format(self, app):
        booking_date = datetime(2020, 8, 12, 20, 00, tzinfo=timezone.utc)
        booking_period_beginning_date_iso = "2020-08-10"
        booking_period_ending_date_iso = "2020-08-12"
        booking = bookings_factories.BookingFactory(dateCreated=booking_date, token="AAAAAA")
        bookings_factories.BookingFactory(token="BBBBBB")
        pro_user = users_factories.ProFactory(email="pro@example.com")
        offers_factories.UserOffererFactory(user=pro_user, offerer=booking.offerer)

        client = TestClient(app.test_client()).with_session_auth(pro_user.email)
        with assert_num_queries(testing.AUTHENTICATION_QUERIES + 2):
            response = client.get(
                "/bookings/pro?bookingPeriodBeginningDate=%s&bookingPeriodEndingDate=%s"
                % (booking_period_beginning_date_iso, booking_period_ending_date_iso)
            )

        assert response.status_code == 200
        assert len(response.json["bookings_recap"]) == 1
        assert response.json["bookings_recap"][0]["booking_date"] == datetime.isoformat(
            utc_datetime_to_department_timezone(booking.dateCreated, booking.venue.departementCode)
        )
        assert response.json["page"] == 1
        assert response.json["pages"] == 1
        assert response.json["total"] == 1


@pytest.mark.usefixtures("db_session")
class Returns400Test:
    def when_page_number_is_not_a_number(self, app):
        pro = users_factories.ProFactory()

        client = TestClient(app.test_client()).with_session_auth(pro.email)
        response = client.get("/bookings/pro?page=not-a-number")

        assert response.status_code == 400
        assert response.json["page"] == ["Saisissez un nombre valide"]

    def when_booking_period_is_not_given(self, app):
        pro = users_factories.ProFactory()

        client = TestClient(app.test_client()).with_session_auth(pro.email)
        response = client.get("/bookings/pro")

        assert response.status_code == 400
        assert response.json["bookingPeriodBeginningDate"] == ["Ce champ est obligatoire"]
        assert response.json["bookingPeriodEndingDate"] == ["Ce champ est obligatoire"]

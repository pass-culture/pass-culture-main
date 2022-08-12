from datetime import datetime
from datetime import timezone
from unittest.mock import patch

from dateutil.tz import tz
import pytest

from pcapi.core import testing
from pcapi.core.booking_providers.factories import ExternalBookingFactory
import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.bookings.models as bookings_models
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
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
    @patch("pcapi.core.bookings.repository.find_by_pro_user")
    def test_call_repository_with_user_and_page(self, find_by_pro_user, app):
        pro = users_factories.ProFactory()
        response = (
            TestClient(app.test_client())
            .with_session_auth(pro.email)
            .get(f"/bookings/pro?{BOOKING_PERIOD_PARAMS}&bookingStatusFilter=booked&page=3")
        )

        assert response.status_code == 200
        find_by_pro_user.assert_called_once_with(
            user=pro,
            booking_period=BOOKING_PERIOD,
            status_filter=bookings_models.BookingStatusFilter.BOOKED,
            event_date=None,
            venue_id=None,
            offer_type=None,
            page=3,
        )

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.core.bookings.repository.find_by_pro_user")
    def test_call_repository_with_page_1(self, find_by_pro_user, app):
        pro = users_factories.ProFactory()
        TestClient(app.test_client()).with_session_auth(pro.email).get(
            f"/bookings/pro?{BOOKING_PERIOD_PARAMS}&bookingStatusFilter=booked"
        )
        find_by_pro_user.assert_called_once_with(
            user=pro,
            booking_period=BOOKING_PERIOD,
            status_filter=bookings_models.BookingStatusFilter.BOOKED,
            event_date=None,
            venue_id=None,
            offer_type=None,
            page=1,
        )

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.core.bookings.repository.find_by_pro_user")
    def test_call_repository_with_venue_id(self, find_by_pro_user, app):
        # Given
        pro = users_factories.ProFactory()
        venue = offerers_factories.VenueFactory()

        # When
        TestClient(app.test_client()).with_session_auth(pro.email).get(
            f"/bookings/pro?{BOOKING_PERIOD_PARAMS}&bookingStatusFilter=booked&venueId={humanize(venue.id)}"
        )

        # Then
        find_by_pro_user.assert_called_once_with(
            user=pro,
            booking_period=BOOKING_PERIOD,
            status_filter=bookings_models.BookingStatusFilter.BOOKED,
            event_date=None,
            venue_id=venue.id,
            offer_type=None,
            page=1,
        )


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    def when_user_is_admin(self, app):
        admin = users_factories.AdminFactory()
        user_offerer = offerers_factories.UserOffererFactory()
        bookings_factories.BookingFactory(
            dateCreated=datetime(2020, 8, 11, 12, 0, 0),
            stock__offer__venue__managingOfferer=user_offerer.offerer,
        )

        client = TestClient(app.test_client()).with_session_auth(admin.email)
        response = client.get(f"/bookings/pro?{BOOKING_PERIOD_PARAMS}&bookingStatusFilter=booked")

        assert response.status_code == 200
        assert len(response.json["bookingsRecap"]) == 1

    def test_when_user_is_linked_to_a_valid_offerer(self, app):
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
        offerers_factories.UserOffererFactory(user=pro_user, offerer=booking.offerer)

        client = TestClient(app.test_client()).with_session_auth(pro_user.email)
        with assert_num_queries(testing.AUTHENTICATION_QUERIES + 2):
            response = client.get(f"/bookings/pro?{BOOKING_PERIOD_PARAMS}&bookingStatusFilter=booked")

        expected_bookings_recap = [
            {
                "stock": {
                    "offer_name": booking.stock.offer.name,
                    "offer_identifier": humanize(booking.stock.offer.id),
                    "offer_is_educational": False,
                    "event_beginning_datetime": None,
                    "offer_isbn": None,
                    "stock_identifier": humanize(booking.stock.id),
                },
                "beneficiary": {
                    "email": "beneficiary@example.com",
                    "firstname": "Hermione",
                    "lastname": "Granger",
                    "phonenumber": "+33100000000",
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
            }
        ]
        assert response.status_code == 200
        assert response.json["bookingsRecap"] == expected_bookings_recap
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
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)

        client = TestClient(app.test_client()).with_session_auth(pro_user.email)
        with assert_num_queries(testing.AUTHENTICATION_QUERIES + 2):
            response = client.get(
                f"/bookings/pro?{BOOKING_PERIOD_PARAMS}&bookingStatusFilter=booked&eventDate={requested_date_iso_format}"
            )

        assert response.status_code == 200
        assert len(response.json["bookingsRecap"]) == 1
        assert response.json["bookingsRecap"][0]["booking_token"] == booking.token
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
        offerers_factories.UserOffererFactory(user=pro_user, offerer=booking.offerer)

        client = TestClient(app.test_client()).with_session_auth(pro_user.email)
        with assert_num_queries(testing.AUTHENTICATION_QUERIES + 2):
            response = client.get(
                "/bookings/pro?bookingPeriodBeginningDate=%s&bookingPeriodEndingDate=%s&bookingStatusFilter=booked"
                % (booking_period_beginning_date_iso, booking_period_ending_date_iso)
            )

        assert response.status_code == 200
        assert len(response.json["bookingsRecap"]) == 1
        assert response.json["bookingsRecap"][0]["booking_date"] == datetime.isoformat(
            utc_datetime_to_department_timezone(booking.dateCreated, booking.venue.departementCode)
        )
        assert response.json["page"] == 1
        assert response.json["pages"] == 1
        assert response.json["total"] == 1

    def test_should_not_return_booking_token_when_booking_is_external(self, app, client):
        booking_date = datetime(2020, 8, 11, 10, 00, tzinfo=timezone.utc)
        externalbooking = ExternalBookingFactory(
            booking__dateCreated=booking_date,
            booking__status=bookings_models.BookingStatus.USED,
            booking__dateUsed=datetime(2020, 8, 11, 20, 00, tzinfo=timezone.utc),
        )
        pro_user = users_factories.ProFactory(email="pro@example.com")
        offerers_factories.UserOffererFactory(user=pro_user, offerer=externalbooking.booking.offerer)

        # when
        response = client.with_session_auth(pro_user.email).get(f"/bookings/pro?{BOOKING_PERIOD_PARAMS}")

        assert response.status_code == 200
        assert response.json["bookingsRecap"][0]["booking_token"] is None


@pytest.mark.usefixtures("db_session")
class Returns400Test:
    def when_page_number_is_not_a_number(self, app):
        pro = users_factories.ProFactory()

        client = TestClient(app.test_client()).with_session_auth(pro.email)
        response = client.get(f"/bookings/pro?{BOOKING_PERIOD_PARAMS}&page=not-a-number")

        assert response.status_code == 400
        assert response.json["page"] == ["Saisissez un nombre valide"]

    def when_booking_period_and_event_date_is_not_given(self, app):
        pro = users_factories.ProFactory()

        client = TestClient(app.test_client()).with_session_auth(pro.email)
        response = client.get("/bookings/pro")

        assert response.status_code == 400
        assert response.json["eventDate"] == ["Ce champ est obligatoire si aucune période n'est renseignée."]
        assert response.json["bookingPeriodBeginningDate"] == [
            "Ce champ est obligatoire si la date d'évènement n'est renseignée"
        ]
        assert response.json["bookingPeriodEndingDate"] == [
            "Ce champ est obligatoire si la date d'évènement n'est renseignée"
        ]

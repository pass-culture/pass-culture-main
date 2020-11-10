import datetime
from collections import namedtuple

import pytest

from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.bookings.factories import BookingWithoutConfirmationDateFactory
from pcapi.core.offers.factories import StockFactory
from pcapi.core.users.factories import UserFactory
from pcapi.scripts.booking.update_confirmation_date_from_existing_bookings import _select_all_event_bookings_without_confirmation_date, _update_target_bookings, \
    fill_missing_confirmation_dates_of_all_event_bookings_without_confirmation_date, \
    fill_missing_confirmation_dates_of_event_bookings_without_confirmation_date_not_cancelled_not_used, get_all_event_bookings_without_confirmation_date_count, \
    get_event_bookings_without_confirmation_date_not_cancelled_not_used_count


@pytest.mark.usefixtures("db_session")
class UpdateConfirmationDateFromExistingBookingsTest:
    @pytest.fixture(name='test_data')
    def test_data_fixture(self):
        last_year = datetime.datetime(2019, 7, 14, 3)
        today_at_2 = datetime.datetime(2020, 11, 5, 2)
        tomorrow_at_13 = datetime.datetime(2020, 11, 6, 13)
        user = UserFactory()
        event_stock = StockFactory(beginningDatetime=tomorrow_at_13, price=0)
        TestDataFixture = namedtuple(
            'TestDataFixture',
            ['last_year', 'today_at_2', 'tomorrow_at_13', 'user', 'event_stock']
        )
        return TestDataFixture(last_year, today_at_2, tomorrow_at_13, user, event_stock)

    def test_select_existing_event_bookings_without_confirmation_date(self, test_data):
        event_booking_with_confirmation_date = BookingFactory(dateCreated=test_data.today_at_2, stock__beginningDatetime=test_data.tomorrow_at_13)
        event_booking_without_confirmation_date = BookingWithoutConfirmationDateFactory(dateCreated=test_data.today_at_2, stock__beginningDatetime=test_data.tomorrow_at_13)
        event_booking_without_confirmation_date_from_last_year = BookingWithoutConfirmationDateFactory(
            dateCreated=test_data.last_year, stock__beginningDatetime=test_data.tomorrow_at_13
        )

        bookings_without_confirmation_date = _select_all_event_bookings_without_confirmation_date().all()

        assert bookings_without_confirmation_date == [event_booking_without_confirmation_date, event_booking_without_confirmation_date_from_last_year]
        assert event_booking_with_confirmation_date not in bookings_without_confirmation_date
        assert get_all_event_bookings_without_confirmation_date_count() == 2

    def test_update_target_bookings(self, test_data):
        event_booking_without_confirmation_date = BookingWithoutConfirmationDateFactory(dateCreated=test_data.today_at_2, stock__beginningDatetime=test_data.tomorrow_at_13)
        event_booking_without_confirmation_date_from_last_year = BookingWithoutConfirmationDateFactory(
            dateCreated=test_data.last_year, stock__beginningDatetime=test_data.tomorrow_at_13
        )

        bookings_without_confirmation_date_query = _select_all_event_bookings_without_confirmation_date()
        _update_target_bookings(target_bookings_query=bookings_without_confirmation_date_query, batch_size=100)

        assert get_all_event_bookings_without_confirmation_date_count() == 0
        assert event_booking_without_confirmation_date.confirmationDate == test_data.today_at_2
        assert event_booking_without_confirmation_date_from_last_year.confirmationDate == test_data.last_year + datetime.timedelta(hours=48)

    def test_fill_missing_confirmation_dates_of_all_event_bookings_without_confirmation_date(self, test_data):
        BookingWithoutConfirmationDateFactory.create_batch(100, dateCreated=test_data.today_at_2, stock=test_data.event_stock, user=test_data.user)
        assert get_all_event_bookings_without_confirmation_date_count() == 100

        fill_missing_confirmation_dates_of_all_event_bookings_without_confirmation_date(batch_size=10)

        assert get_all_event_bookings_without_confirmation_date_count() == 0

    def test_fill_missing_confirmation_dates_of_event_bookings_without_confirmation_date_not_cancelled_not_used(self, test_data):
        BookingWithoutConfirmationDateFactory.create_batch(7, dateCreated=test_data.today_at_2, stock=test_data.event_stock, user=test_data.user)
        BookingWithoutConfirmationDateFactory.create_batch(5, dateCreated=test_data.today_at_2, stock=test_data.event_stock, user=test_data.user, isUsed=True)
        BookingWithoutConfirmationDateFactory.create_batch(5, dateCreated=test_data.today_at_2, stock=test_data.event_stock, user=test_data.user, isCancelled=True)

        assert get_event_bookings_without_confirmation_date_not_cancelled_not_used_count() == 7
        assert get_all_event_bookings_without_confirmation_date_count() == 17

        fill_missing_confirmation_dates_of_event_bookings_without_confirmation_date_not_cancelled_not_used(batch_size=50)

        assert get_event_bookings_without_confirmation_date_not_cancelled_not_used_count() == 0
        assert get_all_event_bookings_without_confirmation_date_count() == 10

import pytest

from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.bookings.models import Booking
from pcapi.models import db
from pcapi.utils import date as date_utils


@pytest.mark.usefixtures("db_session")
class BookingFactoryTest:
    def test_cancellation_limit_date_is_saved_to_db(self):
        booking = BookingFactory(stock__beginningDatetime=date_utils.get_naive_utc_now())
        generated_cancellation_limit_date = booking.cancellationLimitDate

        booking_from_db = db.session.query(Booking).first()

        assert booking_from_db.cancellationLimitDate == generated_cancellation_limit_date

    def test_cancellation_limit_date_is_none_for_a_thing(self):
        non_event_booking = BookingFactory(stock__beginningDatetime=None)
        assert not non_event_booking.cancellationLimitDate

    def test_cancellation_limit_date_is_generated_for_event(self):
        event_booking = BookingFactory(stock__beginningDatetime=date_utils.get_naive_utc_now())
        assert event_booking.cancellationLimitDate

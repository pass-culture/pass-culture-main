import datetime

import pytest

from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.bookings.models import Booking


@pytest.mark.usefixtures("db_session")
class BookingFactoryTest:
    def test_confirmation_date_is_saved_to_db(self):
        booking = BookingFactory(stock__beginningDatetime=datetime.datetime.utcnow())
        generated_confirmation_date = booking.confirmationDate

        booking_from_db = Booking.query.first()

        assert booking_from_db.confirmationDate == generated_confirmation_date

    def test_confirmation_date_is_none_for_non_event(self):
        non_event_booking = BookingFactory()
        assert not non_event_booking.confirmationDate

    def test_confirmation_date_is_generated_for_event(self):
        event_booking = BookingFactory(stock__beginningDatetime=datetime.datetime.utcnow())
        assert event_booking.confirmationDate


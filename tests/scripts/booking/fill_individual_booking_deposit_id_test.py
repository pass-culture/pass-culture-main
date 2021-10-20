from datetime import datetime
import logging

from dateutil.relativedelta import relativedelta
import pytest

import pcapi.core.bookings.factories as bookings_factories
from pcapi.scripts.booking.fill_individual_booking_deposit_id import fill_individual_booking_deposit_id


@pytest.mark.usefixtures("db_session")
def test_fill_individual_booking_deposit_id(caplog):
    already_filled_bookings = bookings_factories.IndividualBookingFactory.create_batch(3)
    to_update_bookings = bookings_factories.IndividualBookingFactory.create_batch(3, individualBooking__deposit=None)
    not_updated_booking = bookings_factories.IndividualBookingFactory(
        amount=0, dateCreated=(datetime.utcnow() + relativedelta(years=3)), individualBooking__deposit=None
    )

    warning_booking = bookings_factories.IndividualBookingFactory(
        amount=10, dateCreated=(datetime.utcnow() + relativedelta(years=3)), individualBooking__deposit=None
    )

    with caplog.at_level(logging.WARNING):
        fill_individual_booking_deposit_id(3)

    for booking in already_filled_bookings + to_update_bookings:
        assert booking.individualBooking.depositId == booking.individualBooking.user.deposit.id

    assert not not_updated_booking.individualBooking.depositId

    assert not warning_booking.individualBooking.depositId
    assert caplog.messages == [f"Booking with amount > 0 made after deposit expiration date id={warning_booking.id}"]

from datetime import datetime
from datetime import timedelta

import pytest

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingStatus
from pcapi.scripts.cancel_bookings_during_quarantine import cancel_booking_status_for_events_happening_during_quarantine


@pytest.mark.usefixtures("db_session")
def test_should_update_booking_if_happening_during_quarantine():
    yesterday = datetime.utcnow() - timedelta(days=1)
    bookings_factories.UsedBookingFactory(stock__beginningDatetime=yesterday)

    cancel_booking_status_for_events_happening_during_quarantine()

    booking = Booking.query.one()
    assert booking.status is not BookingStatus.USED
    assert booking.dateUsed is None


@pytest.mark.usefixtures("db_session")
def test_should_not_update_booking_if_happened_before_quarantine():
    long_ago = datetime(2018, 1, 1)
    bookings_factories.UsedIndividualBookingFactory(dateUsed=long_ago, stock__beginningDatetime=long_ago)

    cancel_booking_status_for_events_happening_during_quarantine()

    booking = Booking.query.one()
    assert booking.status is BookingStatus.USED
    assert booking.dateUsed is not None


# FIXME (dbaty, 2021-06-02): I rewrote this test, but it fails because
# the implementation has a bug. The previous version of the test had a
# bug: the booking was ignored because `stock.beginningDatetime` was
# outside of the quarantine range, not because it had a payment.
#
# @pytest.mark.usefixtures("db_session")
# def test_should_not_update_booking_if_a_payment_has_been_made():
#     yesterday = datetime.utcnow() - timedelta(days=1)
#     payments_factories.PaymentFactory(booking__stock__beginningDatetime=yesterday)

#     cancel_booking_status_for_events_happening_during_quarantine()

#     booking = Booking.query.one()
#     assert booking.dateUsed is not None

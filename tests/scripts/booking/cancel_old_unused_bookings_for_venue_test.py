from datetime import datetime
from datetime import timedelta

import pytest

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingCancellationReasons
from pcapi.core.bookings.models import BookingStatus
import pcapi.core.offers.factories as offers_factories
from pcapi.scripts.booking.cancel_old_unused_bookings_for_venue import cancel_old_unused_bookings_for_venue
from pcapi.utils.human_ids import humanize


@pytest.mark.usefixtures("db_session")
def test_should_cancel_old_unused_bookings_for_venue():
    venue = offers_factories.VenueFactory()
    other_venue = offers_factories.VenueFactory()

    to_cancel_booking = bookings_factories.BookingFactory(
        dateCreated=(datetime.now() - timedelta(days=40)), stock__offer__venue=venue
    )

    used_booking = bookings_factories.BookingFactory(
        dateCreated=(datetime.now() - timedelta(days=40)),
        stock__offer__venue=venue,
        isUsed=True,
        status=BookingStatus.USED,
    )

    recent_booking = bookings_factories.BookingFactory(
        dateCreated=(datetime.now() - timedelta(days=10)), stock__offer__venue=venue
    )

    other_venue_booking = bookings_factories.BookingFactory(
        dateCreated=(datetime.now() - timedelta(days=40)),
        stock__offer__venue=other_venue,
    )

    cancel_old_unused_bookings_for_venue(humanize(venue.id), BookingCancellationReasons.OFFERER)

    to_cancel_booking_result = Booking.query.get(to_cancel_booking.id)
    used_booking_result = Booking.query.get(used_booking.id)
    recent_booking_result = Booking.query.get(recent_booking.id)
    other_venue_booking = Booking.query.get(other_venue_booking.id)

    assert to_cancel_booking_result.isCancelled
    assert to_cancel_booking_result.status is BookingStatus.CANCELLED
    assert to_cancel_booking_result.cancellationReason is BookingCancellationReasons.OFFERER
    assert not used_booking_result.isCancelled
    assert used_booking_result.status is not BookingStatus.CANCELLED
    assert not recent_booking_result.isCancelled
    assert recent_booking_result.status is not BookingStatus.CANCELLED
    assert not other_venue_booking.isCancelled
    assert other_venue_booking.status is not BookingStatus.CANCELLED


def test_should_throw_error_for_unknown_venue():
    with pytest.raises(Exception):
        cancel_old_unused_bookings_for_venue(humanize(1), BookingCancellationReasons.OFFERER)

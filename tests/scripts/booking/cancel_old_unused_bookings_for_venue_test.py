from datetime import datetime
from datetime import timedelta

import pytest

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.bookings.models import Booking
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
    )

    recent_booking = bookings_factories.BookingFactory(
        dateCreated=(datetime.now() - timedelta(days=10)), stock__offer__venue=venue
    )

    other_venue_booking = bookings_factories.BookingFactory(
        dateCreated=(datetime.now() - timedelta(days=40)),
        stock__offer__venue=other_venue,
    )

    cancel_old_unused_bookings_for_venue(humanize(venue.id))

    to_cancel_booking_result = Booking.query.get(to_cancel_booking.id)
    used_booking_result = Booking.query.get(used_booking.id)
    recent_booking_result = Booking.query.get(recent_booking.id)
    other_venue_booking = Booking.query.get(other_venue_booking.id)

    assert to_cancel_booking_result.isCancelled
    assert not used_booking_result.isCancelled
    assert not recent_booking_result.isCancelled
    assert not other_venue_booking.isCancelled


def test_should_throw_error_for_unknown_venue():
    with pytest.raises(Exception):
        cancel_old_unused_bookings_for_venue(humanize(1))

from datetime import datetime
from datetime import timedelta
import logging

from sqlalchemy.sql.sqltypes import DateTime

from pcapi.core.bookings.api import _cancel_booking
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingCancellationReasons
from pcapi.core.offerers.repository import find_venue_by_id
from pcapi.repository import repository
from pcapi.utils.human_ids import dehumanize


logger = logging.getLogger(__name__)


def cancel_old_unused_bookings_for_venue(humanized_venue_id: str, reason: BookingCancellationReasons) -> None:
    venue_id = dehumanize(humanized_venue_id)
    if venue_id is None:
        return

    venue = find_venue_by_id(venue_id)

    if venue is None:
        raise Exception(f"There is no venue with id {humanized_venue_id}")

    limit_date = datetime.now() - timedelta(days=30)

    old_unused_bookings = _get_old_unused_bookings_from_venue_id(venue.id, limit_date)

    for booking in old_unused_bookings:
        _cancel_booking(booking, reason)

    if len(old_unused_bookings) > 0:
        repository.save(*old_unused_bookings)
        logger.info("'%i' bookings cancelled for venue '%s'", len(old_unused_bookings), venue.name)


def _get_old_unused_bookings_from_venue_id(venue_id: int, limit_date: DateTime) -> list[Booking]:
    return Booking.query.filter(
        ~Booking.isCancelled,
        ~Booking.isUsed,
        Booking.dateCreated < limit_date,
        Booking.venueId == venue_id,
    ).all()

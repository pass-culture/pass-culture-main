from datetime import datetime

from sqlalchemy import and_

import pcapi.core.bookings.api as bookings_api
from pcapi.models import Booking
from pcapi.models import Payment
from pcapi.models import Stock


def cancel_booking_status_for_events_happening_during_quarantine() -> None:
    bookings = find_bookings_to_cancel()
    cancel_bookings(bookings)


def find_bookings_to_cancel() -> list[Booking]:
    minimal_date = datetime(2020, 3, 14, 0, 0, 0)
    return (
        Booking.query.join(Stock)
        .filter(
            and_(Stock.beginningDatetime > minimal_date),
            (Stock.beginningDatetime <= datetime.utcnow()),
        )
        .outerjoin(Payment, Payment.bookingId == Booking.id)
        .all()
    )


def cancel_bookings(bookings: list[Booking]) -> None:
    for booking in bookings:
        bookings_api.mark_as_unused(booking)

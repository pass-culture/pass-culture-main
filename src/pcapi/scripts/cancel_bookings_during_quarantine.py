from datetime import datetime

from sqlalchemy import and_

from pcapi.models import Booking
from pcapi.models import Payment
from pcapi.models import Stock
from pcapi.repository import repository


def cancel_booking_status_for_events_happening_during_quarantine():
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


def cancel_bookings(bookings: list[Booking]):
    for booking in bookings:
        booking.markAsUnused()
    repository.save(*bookings)

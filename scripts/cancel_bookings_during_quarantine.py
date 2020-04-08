from datetime import datetime
from typing import List

from sqlalchemy import and_

from models import Booking, Stock, Payment
from repository import repository


def cancel_booking_status_for_events_happening_during_quarantine():
    bookings = find_bookings_to_cancel()
    cancel_bookings(bookings)


def find_bookings_to_cancel() -> List[Booking]:
    minimal_date = datetime(2020, 3, 14, 0, 0, 0)
    return Booking.query \
        .join(Stock) \
        .filter(and_(Stock.beginningDatetime > minimal_date), (Stock.beginningDatetime < datetime.utcnow())) \
        .outerjoin(Payment, Payment.bookingId == Booking.id) \
        .all()


def cancel_bookings(bookings: List[Booking]):
    for booking in bookings:
        booking.isUsed = False
        booking.dateUsed = None
    repository.save(*bookings)

from datetime import datetime
from typing import List

from sqlalchemy import and_

from models import BookingSQLEntity, StockSQLEntity, Payment
from repository import repository


def cancel_booking_status_for_events_happening_during_quarantine():
    bookings = find_bookings_to_cancel()
    cancel_bookings(bookings)


def find_bookings_to_cancel() -> List[BookingSQLEntity]:
    minimal_date = datetime(2020, 3, 14, 0, 0, 0)
    return BookingSQLEntity.query \
        .join(StockSQLEntity) \
        .filter(and_(StockSQLEntity.beginningDatetime > minimal_date), (StockSQLEntity.beginningDatetime < datetime.utcnow())) \
        .outerjoin(Payment, Payment.bookingId == BookingSQLEntity.id) \
        .all()


def cancel_bookings(bookings: List[BookingSQLEntity]):
    for booking in bookings:
        booking.isUsed = False
        booking.dateUsed = None
    repository.save(*bookings)

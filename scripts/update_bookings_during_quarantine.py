from datetime import datetime
from typing import List
from models import Booking, Stock, Payment
from repository import repository


def update_booking_status_for_events_happening_during_quarantine():
    bookings = find_bookings_to_update()
    update_bookings(bookings)


def find_bookings_to_update() -> List[Booking]:
    return Booking.query \
        .join(Stock) \
        .filter(Stock.beginningDatetime > datetime(2020, 3, 14, 0, 0, 0)) \
        .filter(Stock.beginningDatetime < datetime.utcnow()) \
        .outerjoin(Payment, Payment.bookingId == Booking.id) \
        .all()


def update_bookings(bookings: List[Booking]):
    for booking in bookings:
        booking.isUsed = False
        booking.dateUsed = None
    repository.save(*bookings)

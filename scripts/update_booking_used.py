from datetime import datetime

from repository import repository
from repository import booking_queries


def update_booking_used_after_stock_occurrence():
    bookings_to_process = booking_queries.find_not_used_and_not_cancelled()
    bookings_id_errors = []

    for booking in bookings_to_process:
        if booking.stock.beginningDatetime:
            now = datetime.utcnow()
            if booking.stock.isEventDeletable is False:
                booking.isUsed = True
                booking.dateUsed = now
                try:
                    repository.save(booking)
                except Exception:
                    bookings_id_errors.append(booking.id)

    print("Bookings id in error %s" % bookings_id_errors)

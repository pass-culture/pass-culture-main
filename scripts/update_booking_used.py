from datetime import datetime

from domain.stocks import STOCK_DELETION_DELAY
from models import Booking, PcObject
from repository.booking_queries import find_all_not_used_and_not_cancelled


def update_booking_used_after_stock_occurrence():
    bookings_to_process = find_all_not_used_and_not_cancelled()

    for booking in bookings_to_process:
        if datetime.utcnow() > booking.stock.endDatetime + STOCK_DELETION_DELAY:
            booking.isUsed = True
            booking.dateUsed = datetime.utcnow()

    PcObject.save(*bookings_to_process)

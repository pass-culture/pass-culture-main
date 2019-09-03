from datetime import datetime

from domain.stocks import STOCK_DELETION_DELAY
from models import Booking, PcObject


def update_booking_used():
    bookings_to_process = Booking.query \
        .filter(Booking.isUsed == False) \
        .filter(Booking.isCancelled == False) \
        .all()

    for booking in bookings_to_process:
        if datetime.utcnow() > booking.stock.endDatetime + STOCK_DELETION_DELAY:
            booking.isUsed = True
            booking.dateUsed = datetime.utcnow()

    PcObject.save(*bookings_to_process)

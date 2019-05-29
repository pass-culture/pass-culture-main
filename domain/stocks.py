from typing import List

from models import Booking, Stock


def delete_stock_and_cancel_bookings(stock: Stock) -> List[Booking]:
    stock.isSoftDeleted = True
    return list(map(_cancel, stock.bookings))


def _cancel(booking: Booking):
    booking.isCancelled = True
    return booking

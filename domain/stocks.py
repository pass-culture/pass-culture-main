from datetime import datetime, timedelta
from typing import List

from models import Booking, Stock, ApiErrors

STOCK_DELETION_DELAY = timedelta(hours=48)


def delete_stock_and_cancel_bookings(stock: Stock) -> List[Booking]:
    if _is_thing(stock):
        stock.isSoftDeleted = True
        _cancel_unused_bookings(stock)
        return stock.bookings

    limit_date_for_stock_deletion = stock.endDatetime + STOCK_DELETION_DELAY
    now = datetime.utcnow()

    if now <= limit_date_for_stock_deletion:
        stock.isSoftDeleted = True
        _cancel_all_bookings(stock)
    else:
        raise TooLateToDeleteError()

    return stock.bookings


class TooLateToDeleteError(ApiErrors):
    def __init__(self):
        super().__init__(
            errors={"global": ["L'événement s'est terminé il y a plus de deux jours, la suppression est impossible."]}
        )


def _is_thing(stock: Stock) -> bool:
    return stock.beginningDatetime is None


def _cancel_unused_bookings(stock: Stock):
    for booking in stock.bookings:
        if not booking.isUsed:
            booking.isCancelled = True


def _cancel_all_bookings(stock: Stock):
    for booking in stock.bookings:
        booking.isCancelled = True

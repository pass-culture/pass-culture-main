from typing import List, Dict

from models import Booking, Stock, ApiErrors


def delete_stock_and_cancel_bookings(stock: Stock) -> List[Booking]:
    unused_bookings = []

    if _is_thing(stock):
        stock.isSoftDeleted = True

        for booking in stock.bookings:
            if not booking.isUsed and not booking.isCancelled:
                booking.isCancelled = True
                unused_bookings.append(booking)

        return unused_bookings

    if stock.isEventDeletable:
        stock.isSoftDeleted = True
        for booking in stock.bookings:
            if not booking.isCancelled:
                booking.isCancelled = True
                unused_bookings.append(booking)
    else:
        raise TooLateToDeleteError()

    return unused_bookings


def have_beginning_date_been_modified(request_data: Dict, stock: Stock) -> bool:
    return True if 'beginningDatetime' in request_data \
                   and request_data['beginningDatetime'] != stock.beginningDatetime else False


class TooLateToDeleteError(ApiErrors):
    def __init__(self):
        super().__init__(
            errors={"global": ["L'événement s'est terminé il y a plus de deux jours, la suppression est impossible."]}
        )


def _is_thing(stock: Stock) -> bool:
    return stock.beginningDatetime is None

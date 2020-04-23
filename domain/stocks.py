from datetime import datetime
from typing import List, Dict

from models import BookingSQLEntity, StockSQLEntity, ApiErrors


def delete_stock_and_cancel_bookings(stock: StockSQLEntity) -> List[BookingSQLEntity]:
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


def have_beginning_date_been_modified(request_data: Dict, stock_beginning_date: datetime) -> bool:
    if 'beginningDatetime' in request_data:
        new_date = _deserialize_datetime(request_data['beginningDatetime'])
        if new_date != stock_beginning_date:
            return True
    return False


def _deserialize_datetime(value):
    valid_patterns = ['%Y-%m-%dT%H:%M:%S.%fZ', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%SZ']
    datetime_value = None

    for pattern in valid_patterns:
        try:
            datetime_value = datetime.strptime(value, pattern)
        except ValueError:
            continue

    return datetime_value


class TooLateToDeleteError(ApiErrors):
    def __init__(self):
        super().__init__(
            errors={"global": ["L'événement s'est terminé il y a plus de deux jours, la suppression est impossible."]}
        )


def _is_thing(stock: StockSQLEntity) -> bool:
    return stock.beginningDatetime is None

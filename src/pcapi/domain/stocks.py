from typing import List

from pcapi.models import ApiErrors
from pcapi.models import Booking
from pcapi.models import StockSQLEntity


def delete_stock_and_cancel_bookings(stock: StockSQLEntity) -> List[Booking]:
    # FIXME (dbaty): Temporary, to avoid import loop, until we move
    # this function to the validation, too.
    import pcapi.core.offers.validation as offer_validation

    unused_bookings = []

    offer_validation.check_offer_is_editable(stock.offer)

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


class TooLateToDeleteError(ApiErrors):
    def __init__(self):
        super().__init__(
            errors={"global": ["L'événement s'est terminé il y a plus de deux jours, la suppression est impossible."]}
        )


def _is_thing(stock: StockSQLEntity) -> bool:
    return stock.beginningDatetime is None

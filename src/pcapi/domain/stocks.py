from datetime import datetime
from enum import Enum
from typing import Dict
from typing import List

from pcapi.models import ApiErrors
from pcapi.models import Booking
from pcapi.models import StockSQLEntity


class LocalProviderNames(Enum):
    titelive = 'TiteLiveStocks'
    titeliveThings = 'TiteLiveThings'
    fnac = 'FnacStocks'
    libraires = 'LibrairesStocks'
    praxiel = 'PraxielStocks'


def check_stock_is_not_imported(stock: StockSQLEntity):
    local_class = stock.offer.lastProvider.localClass if stock.offer.lastProvider else ''
    is_from_provider = stock.offer.isFromProvider is True

    if is_from_provider and _is_stocks_provider_generated_offer(local_class):
        api_errors = ApiErrors()
        api_errors.add_error('global', 'Les offres importées ne sont pas modifiables')
        raise api_errors



def delete_stock_and_cancel_bookings(stock: StockSQLEntity) -> List[Booking]:
    unused_bookings = []

    check_stock_is_not_imported(stock)

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

def _is_stocks_provider_generated_offer(local_class: str) -> bool:
    for local_provider in LocalProviderNames:
        if local_provider.value == local_class:
            return True
    return False

class TooLateToDeleteError(ApiErrors):
    def __init__(self):
        super().__init__(
            errors={"global": ["L'événement s'est terminé il y a plus de deux jours, la suppression est impossible."]}
        )


def _is_thing(stock: StockSQLEntity) -> bool:
    return stock.beginningDatetime is None

from datetime import datetime
from typing import List

from models import Offer, Stock


def is_eligible_for_indexing(offer: Offer) -> bool:
    if offer is None:
        return False

    venue = offer.venue
    offerer = venue.managingOfferer
    not_deleted_stocks = offer.notDeletedStocks

    if offerer.isActive \
            and offerer.validationToken is None \
            and offer.isActive \
            and _has_remaining_stocks(not_deleted_stocks) \
            and _has_stocks_in_future(not_deleted_stocks) \
            and venue.validationToken is None:
        return True

    return False


def _has_remaining_stocks(stocks: List[Stock]) -> bool:
    remaining_stocks_quantity = 0
    for stock in stocks:
        is_unlimited = stock.available is None
        if is_unlimited:
            return True
        else:
            remaining_stocks_quantity += stock.remainingQuantity
    return remaining_stocks_quantity > 0


def _has_stocks_in_future(stocks: List[Stock]) -> bool:
    for stock in stocks:
        if stock.bookingLimitDatetime and stock.bookingLimitDatetime > datetime.now():
            return True
    return False

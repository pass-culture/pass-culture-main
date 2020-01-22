from datetime import datetime
from typing import List

from models import Offer, Stock


class InconsistentOffer(Exception):
    def __init__(self, message=''):
        self.message = message

    def __str__(self):
        return self.message


def update_is_active_status(offers: List[Offer], status: bool) -> List[Offer]:
    for offer in offers:
        offer.isActive = status

    return offers


def has_remaining_stocks(stocks: List[Stock]) -> bool:
    remaining_stocks_quantity = 0
    for stock in stocks:
        is_unlimited = stock.available is None
        if is_unlimited:
            return True
        remaining_stocks_quantity += stock.remainingQuantity
    return remaining_stocks_quantity > 0


def has_at_least_one_stock_in_the_future(stocks: List[Stock]) -> bool:
    now = datetime.now()

    for stock in stocks:
        if stock.bookingLimitDatetime is None or stock.bookingLimitDatetime > now:
            return True

    return False

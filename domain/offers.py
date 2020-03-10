from datetime import datetime
from typing import List, Optional

from local_providers import AllocineStocks
from models import Booking, Offer, Stock, User


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


def is_from_allocine(offer: Offer) -> bool:
    return offer.isFromProvider and offer.lastProvider.localClass == AllocineStocks.__name__


def find_first_matching_booking_from_offer_by_user(offer: Offer, user: User) -> Optional[Booking]:
    for stock in offer.stocks:
        sorted_booking_by_date_created = sorted(stock.bookings,
                                                key=lambda booking: booking.dateCreated, reverse=True)
        for booking in sorted_booking_by_date_created:
            if booking.userId == user.id:
                return booking

    return None

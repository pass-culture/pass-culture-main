from typing import List, Optional

from local_providers import AllocineStocks
from models import Booking, Offer, UserSQLEntity


def update_is_active_status(offers: List[Offer], status: bool) -> List[Offer]:
    for offer in offers:
        offer.isActive = status

    return offers


def is_from_allocine(offer: Offer) -> bool:
    return offer.isFromProvider and offer.lastProvider.localClass == AllocineStocks.__name__


def find_first_matching_booking_from_offer_by_user(offer: Offer, user: UserSQLEntity) -> Optional[Booking]:
    for stock in offer.stocks:
        sorted_booking_by_date_created = sorted(stock.bookings,
                                                key=lambda booking: booking.dateCreated, reverse=True)
        for booking in sorted_booking_by_date_created:
            if booking.userId == user.id:
                return booking

    return None

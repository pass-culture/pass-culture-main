from typing import List

from pcapi.core.bookings.models import Booking
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.core.users.models import User


def find_bookings_by_beneficiary(user: User) -> List[Booking]:
    return Booking.query.filter(Booking.user == user).all()


def find_stocks_booked_by_beneficiary(user: User) -> List[Stock]:
    return (
        Booking.query.filter(Booking.user == user)
        .join(Stock)
        .filter(Stock.id == Booking.stockId)
        .with_entities(Stock.offerId)
        .all()
    )


def find_offers_booked_by_beneficiary_by_stocks(stock: List[Stock]) -> List[Offer]:
    return Offer.query.filter(Offer.id.in_(stock)).all()

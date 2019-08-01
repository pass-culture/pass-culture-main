from typing import List
from models import Booking, Favorite, Mediation, Offer, User


def create_favorite(mediation: Mediation, offer: Offer, user: User) -> Favorite:
    favorite = Favorite()
    favorite.mediation = mediation
    favorite.offer = offer
    favorite.user = user
    return favorite

def find_first_matching_booking_from_favorite(favorite: Favorite, user: User) -> Booking:
    for stock in favorite.offer.stocks:
         for booking in stock.bookings:
            if booking.userId == user.id:
                return booking

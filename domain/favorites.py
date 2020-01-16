from models import Booking, Favorite, Mediation, Offer, User


def create_favorite(mediation: Mediation, offer: Offer, user: User) -> Favorite:
    favorite = Favorite()
    favorite.mediation = mediation
    favorite.offer = offer
    favorite.user = user
    return favorite


def find_first_matching_booking_from_favorite(favorite: Favorite, user: User) -> Booking:
    for stock in favorite.offer.stocks:
        sortedBookingByDateCreated = sorted(stock.bookings,
                                            key=lambda booking: booking.dateCreated, reverse=True)
        for booking in sortedBookingByDateCreated:
            if booking.userId == user.id:
                return booking

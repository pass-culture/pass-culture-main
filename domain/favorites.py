from models import Booking, Favorite, Mediation, Offer, User


def create_favorite(mediation: Mediation, offer: Offer, user: User) -> Favorite:
    favorite = Favorite()
    favorite.mediation = mediation
    favorite.offer = offer
    favorite.user = user
    return favorite

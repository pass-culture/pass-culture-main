from models import Favorite, Mediation, Offer, UserSQLEntity


def create_favorite(mediation: Mediation, offer: Offer, user: UserSQLEntity) -> Favorite:
    favorite = Favorite()
    favorite.mediation = mediation
    favorite.offer = offer
    favorite.user = user
    return favorite

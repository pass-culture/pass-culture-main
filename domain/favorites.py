from models import FavoriteSQLEntity, Mediation, Offer, UserSQLEntity


def create_favorite(mediation: Mediation, offer: Offer, user: UserSQLEntity) -> FavoriteSQLEntity:
    favorite = FavoriteSQLEntity()
    favorite.mediation = mediation
    favorite.offer = offer
    favorite.user = user
    return favorite

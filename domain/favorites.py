from models import FavoriteSQLEntity, MediationSQLEntity, OfferSQLEntity, UserSQLEntity


def create_favorite(mediation: MediationSQLEntity, offer: OfferSQLEntity, user: UserSQLEntity) -> FavoriteSQLEntity:
    favorite = FavoriteSQLEntity()
    favorite.mediation = mediation
    favorite.offer = offer
    favorite.user = user
    return favorite

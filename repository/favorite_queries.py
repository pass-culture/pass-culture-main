from models import Favorite

from sqlalchemy.orm.query import Query


def find_favorite_for_offer_mediation_and_user(mediation_id: int, offer_id: int, user_id: int) -> Query:
    return Favorite.query \
        .filter(Favorite.offerId == offer_id) \
        .filter(Favorite.mediationId == mediation_id) \
        .filter(Favorite.userId == user_id)

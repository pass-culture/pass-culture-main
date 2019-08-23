from typing import List

from models import Favorite

from sqlalchemy.orm.query import Query


def find_favorite_for_offer_and_user(offer_id: int, user_id: int) -> Query:
    return Favorite.query \
        .filter(Favorite.offerId == offer_id) \
        .filter(Favorite.userId == user_id)


def find_all_favorites_by_user_id(user_id: int) -> List[Favorite]:
    return Favorite.query \
        .filter(Favorite.userId == user_id) \
        .all()

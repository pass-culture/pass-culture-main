from typing import List

from sqlalchemy.orm.query import Query

from pcapi.models import Favorite


def find_favorite_for_offer_and_user(offer_id: int, user_id: int) -> Query:
    return Favorite.query.filter(Favorite.offerId == offer_id).filter(Favorite.userId == user_id)


def get_favorites_for_offers(offer_ids: List[int]) -> List[Favorite]:
    return Favorite.query.filter(Favorite.offerId.in_(offer_ids)).all()

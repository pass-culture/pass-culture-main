from typing import List

from sqlalchemy.orm.query import Query

from models import FavoriteSQLEntity, UserSQLEntity


def find_favorite_for_offer_and_user(offer_id: int, user_id: int) -> Query:
    return FavoriteSQLEntity.query \
        .filter(FavoriteSQLEntity.offerId == offer_id) \
        .filter(FavoriteSQLEntity.userId == user_id)


def get_favorites_for_offers(offer_ids: List[int]) -> List[FavoriteSQLEntity]:
    return FavoriteSQLEntity.query \
        .filter(FavoriteSQLEntity.offerId.in_(offer_ids)) \
        .all()


def get_only_offer_ids_from_favorites(user: UserSQLEntity) -> List[int]:
    favorites = FavoriteSQLEntity.query \
        .filter_by(userId=user.id) \
        .with_entities(FavoriteSQLEntity.offerId) \
        .all()
    return [favorite.offerId for favorite in favorites]

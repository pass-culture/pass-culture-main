from typing import List

from sqlalchemy.orm import joinedload
from sqlalchemy.orm.query import Query

from models import FavoriteSQLEntity, UserSQLEntity, Offer, StockSQLEntity, VenueSQLEntity


def find_favorite_for_offer_and_user(offer_id: int, user_id: int) -> Query:
    return FavoriteSQLEntity.query \
        .filter(FavoriteSQLEntity.offerId == offer_id) \
        .filter(FavoriteSQLEntity.userId == user_id)


def find_all_favorites_by_user_id(user_id: int) -> List[FavoriteSQLEntity]:
    return FavoriteSQLEntity.query \
        .filter(FavoriteSQLEntity.userId == user_id) \
        .options(
            joinedload(FavoriteSQLEntity.offer).
            joinedload(Offer.venue).
            joinedload(VenueSQLEntity.managingOfferer)
        ) \
        .options(
            joinedload(FavoriteSQLEntity.offer).
            joinedload(Offer.stocks).
            joinedload(StockSQLEntity.bookings)
        ) \
        .options(
            joinedload(FavoriteSQLEntity.offer).
            joinedload(Offer.product)
        ) \
        .options(
            joinedload(FavoriteSQLEntity.offer).
            joinedload(Offer.mediations)
        ) \
        .all()


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

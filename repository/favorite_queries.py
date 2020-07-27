from typing import List

from sqlalchemy.orm import joinedload
from sqlalchemy.orm.query import Query

from models import Favorite, UserSQLEntity, Offer, StockSQLEntity, VenueSQLEntity


def find_favorite_for_offer_and_user(offer_id: int, user_id: int) -> Query:
    return Favorite.query \
        .filter(Favorite.offerId == offer_id) \
        .filter(Favorite.userId == user_id)


def find_all_favorites_by_user_id(user_id: int) -> List[Favorite]:
    return Favorite.query \
        .filter(Favorite.userId == user_id) \
        .options(
            joinedload(Favorite.offer).
            joinedload(Offer.venue).
            joinedload(VenueSQLEntity.managingOfferer)
        ) \
        .options(
            joinedload(Favorite.offer).
            joinedload(Offer.stocks).
            joinedload(StockSQLEntity.bookings)
        ) \
        .options(
            joinedload(Favorite.offer).
            joinedload(Offer.product)
        ) \
        .options(
            joinedload(Favorite.offer).
            joinedload(Offer.mediations)
        ) \
        .all()


def get_favorites_for_offers(offer_ids: List[int]) -> List[Favorite]:
    return Favorite.query \
        .filter(Favorite.offerId.in_(offer_ids)) \
        .all()


def get_only_offer_ids_from_favorites(user: UserSQLEntity) -> List[int]:
    favorites = Favorite.query \
        .filter_by(userId=user.id) \
        .with_entities(Favorite.offerId) \
        .all()
    return [favorite.offerId for favorite in favorites]

from typing import List

from sqlalchemy.orm import joinedload

from domain.favorite.favorite import Favorite
from domain.favorite.favorite_repository import FavoriteRepository
from infrastructure.repository.favorite import favorite_domain_converter
from models import FavoriteSQLEntity, OfferSQLEntity, StockSQLEntity, VenueSQLEntity


class FavoriteSQLRepository(FavoriteRepository):
    def find_by_beneficiary(self, beneficiary_identifier: int) -> List[Favorite]:
        favorite_sql_entities = FavoriteSQLEntity.query \
            .filter(FavoriteSQLEntity.userId == beneficiary_identifier) \
            .options(
                joinedload(FavoriteSQLEntity.offer)
                .joinedload(OfferSQLEntity.venue)
                .joinedload(VenueSQLEntity.managingOfferer)
            ) \
            .options(
                joinedload(FavoriteSQLEntity.offer)
                .joinedload(OfferSQLEntity.stocks)
                .joinedload(StockSQLEntity.bookings)
            ) \
            .options(
                joinedload(FavoriteSQLEntity.offer)
                .joinedload(OfferSQLEntity.product)
            ) \
            .options(
                joinedload(FavoriteSQLEntity.offer)
                .joinedload(OfferSQLEntity.mediations)
            ) \
            .all()

        return [favorite_domain_converter.to_domain(favorite_sql_entity) for favorite_sql_entity in favorite_sql_entities]

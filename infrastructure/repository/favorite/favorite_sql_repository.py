from sqlalchemy.orm import joinedload

from domain.favorite.favorite_repository import FavoriteRepository
from models import FavoriteSQLEntity, Offer, StockSQLEntity, VenueSQLEntity


class FavoriteSQLRepository(FavoriteRepository):
    def find_by_beneficiary(self, beneficiary_identifier: int) -> FavoriteSQLEntity:
        return FavoriteSQLEntity.query \
            .filter(FavoriteSQLEntity.userId == beneficiary_identifier) \
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

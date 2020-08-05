from typing import List

from sqlalchemy.orm import joinedload

from domain.favorite.favorite import Favorite
from domain.favorite.favorite_repository import FavoriteRepository
from infrastructure.repository.favorite import favorite_domain_converter
from models import FavoriteSQLEntity, OfferSQLEntity, StockSQLEntity, VenueSQLEntity, BookingSQLEntity


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
                joinedload(FavoriteSQLEntity.mediation)
                ) \
            .options(
                joinedload(FavoriteSQLEntity.offer)
                .joinedload(OfferSQLEntity.stocks)
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

        offer_ids = [favorite_sql_entity.offer.id for favorite_sql_entity in favorite_sql_entities]

        bookings = OfferSQLEntity.query \
            .filter(OfferSQLEntity.id.in_(offer_ids)) \
            .join(StockSQLEntity) \
            .join(BookingSQLEntity) \
            .filter(BookingSQLEntity.userId == beneficiary_identifier) \
            .filter(BookingSQLEntity.isCancelled == False) \
            .with_entities(
                BookingSQLEntity.id.label('booking_id'),
                OfferSQLEntity.id.label('offer_id'),
                StockSQLEntity.id.label('stock_id')
                ) \
            .all()

        bookings_by_offer_id = {booking.offer_id: {'id': booking.booking_id, 'stock_id': booking.stock_id} for booking in bookings}

        return [favorite_domain_converter.to_domain(favorite_sql_entity, self._booking_of_offer_if_booked(bookings_by_offer_id, favorite_sql_entity.offerId)) for favorite_sql_entity in
                favorite_sql_entities]

    def _booking_of_offer_if_booked(self, bookings_by_offer_id: dict, offer_id: int) -> dict:
        return bookings_by_offer_id.get(offer_id, None)

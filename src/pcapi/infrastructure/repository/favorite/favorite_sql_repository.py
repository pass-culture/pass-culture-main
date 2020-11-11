from typing import Dict
from typing import List

from sqlalchemy.orm import joinedload

from pcapi.domain.favorite.favorite import Favorite
from pcapi.domain.favorite.favorite_repository import FavoriteRepository
from pcapi.infrastructure.repository.favorite import favorite_domain_converter
from pcapi.models import Booking
from pcapi.models import FavoriteSQLEntity
from pcapi.models import Offer
from pcapi.models import StockSQLEntity
from pcapi.models import VenueSQLEntity


class FavoriteSQLRepository(FavoriteRepository):
    def find_by_beneficiary(self, beneficiary_identifier: int) -> List[Favorite]:
        favorite_sql_entities = (
            FavoriteSQLEntity.query.filter(FavoriteSQLEntity.userId == beneficiary_identifier)
            .options(
                joinedload(FavoriteSQLEntity.offer).joinedload(Offer.venue).joinedload(VenueSQLEntity.managingOfferer)
            )
            .options(joinedload(FavoriteSQLEntity.mediation))
            .options(joinedload(FavoriteSQLEntity.offer).joinedload(Offer.stocks))
            .options(joinedload(FavoriteSQLEntity.offer).joinedload(Offer.product))
            .options(joinedload(FavoriteSQLEntity.offer).joinedload(Offer.mediations))
            .all()
        )

        offer_ids = [favorite_sql_entity.offer.id for favorite_sql_entity in favorite_sql_entities]

        bookings = (
            Offer.query.filter(Offer.id.in_(offer_ids))
            .join(StockSQLEntity)
            .join(Booking)
            .filter(Booking.userId == beneficiary_identifier)
            .filter(Booking.isCancelled == False)
            .with_entities(
                Booking.id.label("booking_id"), Offer.id.label("offer_id"), StockSQLEntity.id.label("stock_id")
            )
            .all()
        )

        bookings_by_offer_id = {
            booking.offer_id: {"id": booking.booking_id, "stock_id": booking.stock_id} for booking in bookings
        }

        return [
            favorite_domain_converter.to_domain(
                favorite_sql_entity, bookings_by_offer_id.get(favorite_sql_entity.offerId, None)
            )
            for favorite_sql_entity in favorite_sql_entities
        ]

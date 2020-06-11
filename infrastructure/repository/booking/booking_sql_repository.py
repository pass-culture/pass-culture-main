from typing import List

from domain.booking.booking import Booking
from domain.booking.booking_repository import BookingRepository
from infrastructure.repository.booking import booking_domain_converter, booking_with_offerer_domain_converter
from models import BookingSQLEntity, StockSQLEntity
from repository import repository


class BookingSQLRepository(BookingRepository):
    def find_active_bookings_by_user_id(self, user_id: int) -> List[Booking]:
        booking_sql_entities: List = BookingSQLEntity.query \
            .filter_by(userId=user_id) \
            .filter_by(isCancelled=False) \
            .all()

        return [booking_domain_converter.to_domain(booking_sql_entity) for booking_sql_entity in booking_sql_entities]

    def find_not_cancelled_booking_by(self, offer_id: int, user_id: int) -> Booking:
        booking_sql_entity = BookingSQLEntity.query \
            .join(StockSQLEntity) \
            .filter(StockSQLEntity.offerId == offer_id) \
            .filter(BookingSQLEntity.userId == user_id) \
            .filter(BookingSQLEntity.isCancelled == False) \
            .first()
        return booking_domain_converter.to_domain(booking_sql_entity)

    def save(self, booking: Booking) -> Booking:
        booking_sql_entity = booking_domain_converter.to_model(booking)
        repository.save(booking_sql_entity)
        return booking_domain_converter.to_domain(booking_sql_entity)

    def find_booking_with_offerer(self, booking_id) -> Booking:
        booking_sql_entity = BookingSQLEntity.query \
            .filter_by(id=booking_id) \
            .first()
        return booking_with_offerer_domain_converter.to_domain(booking_sql_entity)

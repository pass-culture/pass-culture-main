from typing import List

from domain.booking.booking import Booking
from domain.booking.booking_repository import BookingRepository
from models import BookingSQLEntity
from repository import repository
from repository.booking import booking_domain_adapter


class BookingSQLRepository(BookingRepository):
    def find_active_bookings_by_user_id(self, user_id: int) -> List[Booking]:
        booking_sql_entities: List = BookingSQLEntity.query \
            .filter_by(userId=user_id) \
            .filter_by(isCancelled=False) \
            .all()

        return [booking_domain_adapter.to_domain(booking_sql_entity) for booking_sql_entity in booking_sql_entities]

    def save(self, booking: Booking) -> Booking:
        booking_sql_entity = booking_domain_adapter.to_model(booking)
        repository.save(booking_sql_entity)
        return booking_domain_adapter.to_domain(booking_sql_entity)

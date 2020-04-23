from typing import List

from domain.booking.booking import Booking
from domain.booking.booking_repository import BookingRepository
from models import BookingSQLEntity


class BookingSQLRepository(BookingRepository):
    def find_active_bookings_by_user_id(self, user_id: int) -> List[Booking]:
        booking_sql_entities: List = BookingSQLEntity.query \
            .filter_by(userId=user_id) \
            .filter_by(isCancelled=False) \
            .all()

        bookings = []

        for booking_sql_entity in booking_sql_entities:
            bookings.append(self.to_domain(booking_sql_entity))

        return bookings

    def to_domain(self, booking_sql_entity: BookingSQLEntity) -> Booking:
        return Booking(user=booking_sql_entity.user,
                       stock=booking_sql_entity.stock,
                       amount=booking_sql_entity.amount,
                       quantity=booking_sql_entity.quantity)

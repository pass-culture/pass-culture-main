from typing import List

from domain.booking.booking import Booking
from domain.booking.booking_repository import BookingRepository
from models import BookingSQLEntity
from repository import repository
from utils.token import random_token


class BookingSQLRepository(BookingRepository):
    def find_active_bookings_by_user_id(self, user_id: int) -> List[Booking]:
        booking_sql_entities: List = BookingSQLEntity.query \
            .filter_by(userId=user_id) \
            .filter_by(isCancelled=False) \
            .all()

        return [self.to_domain(booking_sql_entity) for booking_sql_entity in booking_sql_entities]

    def to_domain(self, booking_sql_entity: BookingSQLEntity) -> Booking:
        return Booking(user=booking_sql_entity.user,
                       stock=booking_sql_entity.stock,
                       amount=booking_sql_entity.amount,
                       quantity=booking_sql_entity.quantity,
                       identifier=booking_sql_entity.id,
                       recommendation_id=booking_sql_entity.recommendationId)

    def to_model(self, booking: Booking) -> BookingSQLEntity:
        booking_sql_entity = BookingSQLEntity()
        booking_sql_entity.userId = booking.user.id
        booking_sql_entity.stockId = booking.stock.id
        booking_sql_entity.amount = booking.amount
        booking_sql_entity.quantity = booking.quantity
        booking_sql_entity.token = random_token()
        booking_sql_entity.id = booking.identifier

        return booking_sql_entity


    def save(self, booking: Booking) -> None:
        booking_sql_entity = self.to_model(booking)
        print(booking_sql_entity.__dict__)
        repository.save(booking_sql_entity)

from typing import List, Dict

from pcapi.domain.booking.booking import Booking
from pcapi.domain.booking.booking_exceptions import BookingDoesntExist
from pcapi.domain.booking.booking_repository import BookingRepository
from pcapi.domain.expenses import get_expenses
from pcapi.infrastructure.repository.booking import booking_domain_converter
from pcapi.models import BookingSQLEntity, StockSQLEntity
from pcapi.repository import repository
from sqlalchemy.orm import Query, joinedload


class BookingSQLRepository(BookingRepository):
    def get_expenses_by_user_id(self, user_id: int) -> Dict:
        bookings_query = BookingSQLEntity.query \
            .filter_by(userId=user_id) \
            .filter_by(isCancelled=False)

        bookings = bookings_query.options(
            joinedload(BookingSQLEntity.stock).
            joinedload(StockSQLEntity.offer)).all()

        return get_expenses(bookings)

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

    def find_booking_by_id_and_beneficiary_id(self, booking_id: int, beneficiary_id: int) -> Booking:
        booking_sql_entity = BookingSQLEntity.query \
            .filter(BookingSQLEntity.id == booking_id) \
            .filter(BookingSQLEntity.userId == beneficiary_id) \
            .first()

        if booking_sql_entity is None:
            raise BookingDoesntExist()

        return booking_domain_converter.to_domain(booking_sql_entity)

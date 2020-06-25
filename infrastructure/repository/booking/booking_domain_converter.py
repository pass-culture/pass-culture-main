from domain.booking.booking import Booking
from models import BookingSQLEntity
from infrastructure.repository.stock import stock_domain_converter
from infrastructure.repository.beneficiary import beneficiary_domain_converter
from utils.token import random_token


def to_domain(booking_sql_entity: BookingSQLEntity) -> Booking:
    user = beneficiary_domain_converter.to_domain(booking_sql_entity.user)
    stock = stock_domain_converter.to_domain(booking_sql_entity.stock)

    return Booking(beneficiary=user,
                   stock=stock,
                   amount=booking_sql_entity.amount,
                   quantity=booking_sql_entity.quantity,
                   recommendation_id=booking_sql_entity.recommendationId,
                   identifier=booking_sql_entity.id,
                   token=booking_sql_entity.token,
                   date_booked=booking_sql_entity.dateCreated,
                   is_cancelled=booking_sql_entity.isCancelled,
                   is_used=booking_sql_entity.isUsed)


def to_model(booking: Booking) -> BookingSQLEntity:
    booking_sql_entity = BookingSQLEntity.query.get(booking.identifier)
    if not booking_sql_entity:
        booking_sql_entity = BookingSQLEntity()
        booking_sql_entity.token = random_token()
    else:
        booking_sql_entity.token = booking_sql_entity.token
    booking_sql_entity.userId = booking.beneficiary.identifier
    booking_sql_entity.stockId = booking.stock.identifier
    booking_sql_entity.amount = booking.amount
    booking_sql_entity.quantity = booking.quantity
    booking_sql_entity.id = booking.identifier
    booking_sql_entity.isCancelled = booking.isCancelled
    booking_sql_entity.isUsed = booking.is_used

    return booking_sql_entity

from domain.booking.booking import Booking
from models import BookingSQLEntity
from repository.stock import stock_domain_adapter
from repository.user import user_domain_adapter
from utils.token import random_token


def to_domain(booking_sql_entity: BookingSQLEntity) -> Booking:
    user = user_domain_adapter.to_domain(booking_sql_entity.user)
    stock = stock_domain_adapter.to_domain(booking_sql_entity.stock)

    return Booking(user=user,
                   stock=stock,
                   amount=booking_sql_entity.amount,
                   quantity=booking_sql_entity.quantity,
                   identifier=booking_sql_entity.id,
                   recommendation_id=booking_sql_entity.recommendationId)


def to_model(booking: Booking) -> BookingSQLEntity:
    booking_sql_entity = BookingSQLEntity()
    booking_sql_entity.userId = booking.user.identifier
    booking_sql_entity.stockId = booking.stock.identifier
    booking_sql_entity.amount = booking.amount
    booking_sql_entity.quantity = booking.quantity
    booking_sql_entity.token = random_token()
    booking_sql_entity.id = booking.identifier

    return booking_sql_entity

from domain.booking.booking import Booking
from domain.booking.booking_with_offerer.booking_with_offerer import BookingWithOfferer
from infrastructure.repository.beneficiary import beneficiary_domain_converter
from infrastructure.repository.stock import stock_domain_converter
from models import BookingSQLEntity


def to_domain(booking_sql_entity: BookingSQLEntity) -> Booking:
    user = beneficiary_domain_converter.to_domain(booking_sql_entity.user)
    stock = stock_domain_converter.to_domain(booking_sql_entity.stock)

    return BookingWithOfferer(beneficiary=user,
                              stock=stock,
                              amount=booking_sql_entity.amount,
                              quantity=booking_sql_entity.quantity,
                              recommendation_id=booking_sql_entity.recommendationId,
                              identifier=booking_sql_entity.id,
                              token=booking_sql_entity.token,
                              date_booked=booking_sql_entity.dateCreated,
                              is_cancelled=booking_sql_entity.isCancelled,
                              is_used=booking_sql_entity.isUsed,
                              managing_offerer_id=stock.offer.venue.managingOffererId)

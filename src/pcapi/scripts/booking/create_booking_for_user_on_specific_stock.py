from flask import current_app as app

from pcapi.connectors import redis
from pcapi.domain.booking.booking import Booking
from pcapi.domain.booking.booking_validator import check_offer_already_booked, check_quantity_is_valid
from pcapi.domain.stock.stock_validator import check_can_book_free_offer, check_stock_is_bookable
from pcapi.infrastructure.container import book_an_offer, stock_repository, user_repository, booking_repository
from pcapi.use_cases.book_an_offer import BookAnOffer, BookingInformation


def create_booking_for_user_on_specific_stock(user_id: int, stock_id: int,
                                              book_an_offer_impl: BookAnOffer = book_an_offer) -> None:
    booking_information = BookingInformation(
        stock_id=stock_id,
        user_id=user_id,
        quantity=1,
    )

    book_an_offer_impl.execute(booking_information)


def create_booking_for_user_on_specific_stock_bypassing_capping_limits(user_id: int, stock_id: int) -> None:
    booking_information = BookingInformation(
        stock_id=stock_id,
        user_id=user_id,
        quantity=1,
    )
    stock = stock_repository.find_stock_by_id(booking_information.stock_id)
    user = user_repository.find_beneficiary_by_user_id(booking_information.user_id)

    check_offer_already_booked(stock.offer, user.identifier)
    check_quantity_is_valid(booking_information.quantity, stock.offer.isDuo)
    check_can_book_free_offer(user, stock)
    check_stock_is_bookable(stock)

    quantity = booking_information.quantity
    amount = stock.price
    booking = Booking(beneficiary=user, stock=stock, amount=amount, quantity=quantity)

    booking_repository.save(booking)

    redis.add_offer_id(client=app.redis_client, offer_id=stock.offer.id)

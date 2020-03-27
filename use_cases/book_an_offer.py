from flask import current_app as app

from connectors import redis
from domain.booking import check_already_booked, OfferIsAlreadyBooked, check_existing_stock, StockIdDoesntExist, \
    check_quantity_is_valid, QuantityIsInvalid, StockIsNotBookable, check_stock_is_bookable, check_offer_already_booked, \
    ExpenseLimitHasBeenReached, check_expenses_limits
from domain.expenses import get_expenses
from domain.user_emails import send_booking_recap_emails, send_booking_confirmation_email_to_beneficiary
from models import Booking, Stock, User, Offer
from models.feature import FeatureToggle
from repository import booking_queries, repository, feature_queries
from use_cases.booking_information import BookingInformation
from use_cases.generic_response import Response
from utils.mailing import send_raw_email, MailServiceException
from utils.token import random_token
from validation.routes.users_authorizations import check_can_book_free_offer


def book_an_offer(booking_information: BookingInformation) -> Response:
    stock = Stock.query.get(booking_information.stock_id)
    user = User.query.get(booking_information.user_id)
    offer = Offer.query.get(stock.offerId)

    try:
        check_already_booked(stock, user)  # todo delete this one
        check_offer_already_booked(offer, user)
        check_existing_stock(stock)
        check_quantity_is_valid(booking_information.quantity, stock)
    except OfferIsAlreadyBooked as error:
        return Failure(error)
    except StockIdDoesntExist as error:
        return Failure(error)
    except QuantityIsInvalid as error:
        return Failure(error)

    check_can_book_free_offer(stock, user)

    try:
        check_stock_is_bookable(stock)
    except StockIsNotBookable as error:
        return Failure(error)

    booking = _create_booking_with_booking_information(booking_information, stock)

    bookings = booking_queries.find_active_bookings_by_user_id(booking_information.user_id)

    expenses = get_expenses(bookings)
    try:
        check_expenses_limits(expenses, booking)
    except ExpenseLimitHasBeenReached as error:
        return Failure(error)
    repository.save(booking)

    if feature_queries.is_active(FeatureToggle.SYNCHRONIZE_ALGOLIA):
        redis.add_offer_id(client=app.redis_client, offer_id=stock.offerId)

    try:
        send_booking_recap_emails(booking, send_raw_email)
    except MailServiceException as error:
        app.logger.error('Mail service failure', error)

    try:
        send_booking_confirmation_email_to_beneficiary(booking, send_raw_email)
    except MailServiceException as error:
        app.logger.error('Mail service failure', error)

    return Success(booking=booking)


def _create_booking_with_booking_information(booking_information, stock):
    booking = Booking()
    booking.stockId = booking_information.stock_id
    booking.userId = booking_information.user_id
    booking.quantity = booking_information.quantity
    booking.recommendationId = booking_information.recommendation_id
    booking.amount = stock.price
    booking.token = random_token()
    return booking


class Success(Response):
    def __init__(self, booking):
        super().__init__()
        self.booking = booking


class Failure(Response):
    def __init__(self, error):
        super().__init__()
        self.error_message = error

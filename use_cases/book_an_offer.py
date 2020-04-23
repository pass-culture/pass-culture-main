from flask import current_app as app

from domain.booking.booking_validator import check_offer_already_booked, check_quantity_is_valid
from domain.expenses import get_expenses
from domain.services.notification.notification_service import NotificationService
from domain.stock.stock_repository import StockRepository
from domain.stock.stock_validator import check_stock_is_bookable, check_expenses_limits, check_can_book_free_offer
from domain.user.user_repository import UserRepository
from domain.user_emails import send_booking_confirmation_email_to_beneficiary
from models import Booking
from repository import booking_queries, repository
from utils.mailing import send_raw_email, MailServiceException
from utils.token import random_token


class BookingInformation(object):
    def __init__(self, stock_id: int, user_id: int, quantity: int, recommendation_id: int = None):
        self.stock_id = stock_id
        self.user_id = user_id
        self.quantity = quantity
        self.recommendation_id = recommendation_id


class BookAnOffer:
    def __init__(self, stock_repository: StockRepository,
                 user_repository: UserRepository,
                 notification_service: NotificationService):
        self.stock_repository = stock_repository
        self.user_repository = user_repository
        self.notification_service = notification_service

    def execute(self, booking_information: BookingInformation) -> Booking:
        stock = self.stock_repository.find_stock_by_id(booking_information.stock_id)
        user = self.user_repository.find_user_by_id(booking_information.user_id)

        check_offer_already_booked(stock.offer, user.identifier)
        check_quantity_is_valid(booking_information.quantity, stock.offer.isDuo)
        check_can_book_free_offer(user, stock)
        check_stock_is_bookable(stock)

        booking = self._create_booking_with_booking_information(booking_information, stock)
        bookings = booking_queries.find_active_bookings_by_user_id(booking_information.user_id)
        expenses = get_expenses(bookings)
        check_expenses_limits(expenses, booking)

        repository.save(booking)

        self.notification_service.send_booking_recap_emails(booking)
        self.notification_service.send_booking_confirmation_email_to_beneficiary(booking)

        return booking

    def _create_booking_with_booking_information(self, booking_information, stock) -> Booking:
        booking = Booking()
        booking.stockId = booking_information.stock_id
        booking.userId = booking_information.user_id
        booking.quantity = booking_information.quantity
        booking.recommendationId = booking_information.recommendation_id
        booking.amount = stock.price
        booking.token = random_token()
        return booking

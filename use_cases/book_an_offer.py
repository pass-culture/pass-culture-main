from domain.booking.booking import Booking
from domain.booking.booking_repository import BookingRepository
from domain.booking.booking_validator import check_offer_already_booked, check_quantity_is_valid
from domain.expenses import get_expenses
from domain.services.notification.notification_service import NotificationService
from domain.stock.stock import Stock
from domain.stock.stock_repository import StockRepository
from domain.stock.stock_validator import check_stock_is_bookable, check_expenses_limits, check_can_book_free_offer
from domain.beneficiary.beneficiary import Beneficiary
from domain.beneficiary.beneficiary_repository import BeneficiaryRepository


class BookingInformation(object):
    def __init__(self, stock_id: int, user_id: int, quantity: int, recommendation_id: int = None):
        self.stock_id = stock_id
        self.user_id = user_id
        self.quantity = quantity
        self.recommendation_id = recommendation_id


class BookAnOffer:
    def __init__(self,
                 booking_repository: BookingRepository,
                 stock_repository: StockRepository,
                 user_repository: BeneficiaryRepository,
                 notification_service: NotificationService):
        self.booking_repository = booking_repository
        self.stock_repository = stock_repository
        self.user_repository = user_repository
        self.notification_service = notification_service

    def execute(self, booking_information: BookingInformation) -> Booking:
        stock = self.stock_repository.find_stock_by_id(booking_information.stock_id)
        user = self.user_repository.find_beneficiary_by_user_id(booking_information.user_id)

        check_offer_already_booked(stock.offer, user.identifier)
        check_quantity_is_valid(booking_information.quantity, stock.offer.isDuo)
        check_can_book_free_offer(user, stock)
        check_stock_is_bookable(stock)

        booking = self._create_booking_with_booking_information(booking_information, stock, user)
        bookings = self.booking_repository.find_active_bookings_by_user_id(booking_information.user_id)

        expenses = get_expenses(bookings)
        check_expenses_limits(expenses, booking)

        booking_saved = self.booking_repository.save(booking)

        self.notification_service.send_booking_recap(booking_saved)
        self.notification_service.send_booking_confirmation_to_beneficiary(booking_saved)

        return booking_saved

    def _create_booking_with_booking_information(
            self,
            booking_information: BookingInformation,
            stock: Stock,
            user: Beneficiary) -> Booking:
        quantity = booking_information.quantity
        recommendation_id = booking_information.recommendation_id
        amount = stock.price
        booking = Booking(beneficiary=user, stock=stock, amount=amount, quantity=quantity, recommendation_id=recommendation_id)
        return booking

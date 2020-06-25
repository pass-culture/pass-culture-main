from infrastructure.repository.beneficiary.beneficiary_sql_repository import BeneficiarySQLRepository
from infrastructure.repository.booking.booking_sql_repository import BookingSQLRepository
from infrastructure.repository.stock.stock_sql_repository import StockSQLRepository
from infrastructure.services.notification.mailjet_notification_service import MailjetNotificationService
from use_cases.book_an_offer import BookAnOffer, BookingInformation

booking_repository = BookingSQLRepository()
user_repository = BeneficiarySQLRepository()
stock_repository = StockSQLRepository()
notification_service = MailjetNotificationService()

book_an_offer_impl = BookAnOffer(
    booking_repository=booking_repository,
    user_repository=user_repository,
    stock_repository=stock_repository,
    notification_service=notification_service)


def create_booking_for_user_on_specific_stock(user_id: int, stock_id: int,
                                              book_an_offer: BookAnOffer = book_an_offer_impl) -> None:
    booking_information = BookingInformation(
        stock_id=stock_id,
        user_id=user_id,
        quantity=1,
    )

    book_an_offer.execute(booking_information)

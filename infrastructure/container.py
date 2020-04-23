from infrastructure.services.notification.mailjet_service import MailjetService
from repository.booking.booking_sql_repository import BookingSQLRepository
from repository.stock.stock_sql_repository import StockSQLRepository
from repository.user.user_sql_repository import UserSQLRepository
from use_cases.book_an_offer import BookAnOffer

# Repositories
booking_repository = BookingSQLRepository()
user_repository = UserSQLRepository()
stock_repository = StockSQLRepository()
notification_service = MailjetService()

# Usecases
book_an_offer = BookAnOffer(booking_repository=booking_repository,
                            user_repository=user_repository,
                            stock_repository=stock_repository,
                            notification_service=notification_service)

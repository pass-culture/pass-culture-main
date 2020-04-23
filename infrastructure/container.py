from infrastructure.services.notification.mailjet_service import MailjetService
from repository.stock.stock_sql_repository import StockSQLRepository
from repository.user.user_sql_repository import UserSQLRepository
from use_cases.book_an_offer import BookAnOffer

# Repositories
stock_repository = StockSQLRepository()
user_repository = UserSQLRepository()
notification_service = MailjetService()

# Usecases
book_an_offer = BookAnOffer(stock_repository=stock_repository,
                            user_repository=user_repository,
                            notification_service=notification_service)

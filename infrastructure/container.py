from infrastructure.services.email.mail_jet_email_service import MailJetEmailService
from repository.stock.stock_sql_repository import StockSQLRepository
from repository.user.user_sql_repository import UserSQLRepository
from use_cases.book_an_offer import BookAnOffer

# Repositories
stock_repository = StockSQLRepository()
user_repository = UserSQLRepository()
email_service = MailJetEmailService()

# Usecases
book_an_offer = BookAnOffer(stock_repository=stock_repository,
                            user_repository=user_repository,
                            email_service=email_service)

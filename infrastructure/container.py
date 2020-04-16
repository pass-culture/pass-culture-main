from repository.stock.stock_sql_repository import StockSQLRepository
from use_cases.book_an_offer import BookAnOffer

# Repostories
stock_repository = StockSQLRepository()

# Usecases
book_an_offer = BookAnOffer(stock_repository)

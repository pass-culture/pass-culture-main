from domain.stock.stock import Stock
from domain.stock.stock_exceptions import StockDoesntExist
from domain.stock.stock_repository import StockRepository
from models import StockSQLEntity
from models.db import db
from repository.stock import stock_domain_adapter


class StockSQLRepository(StockRepository):
    def find_stock_by_id(self, stock_id: int) -> Stock:
        stock_sql_entity = db.session.query(StockSQLEntity).get(stock_id)

        if stock_sql_entity is None:
            raise StockDoesntExist()

        return stock_domain_adapter.to_domain(stock_sql_entity)

from pcapi.domain.stock.stock import Stock
from pcapi.domain.stock.stock_exceptions import StockDoesntExist
from pcapi.domain.stock.stock_repository import StockRepository
from pcapi.infrastructure.repository.stock import stock_domain_converter
from pcapi.models import StockSQLEntity
from pcapi.models.db import db


class StockSQLRepository(StockRepository):
    def find_stock_by_id(self, stock_id: int) -> Stock:
        stock_sql_entity = db.session.query(StockSQLEntity).get(stock_id)

        if stock_sql_entity is None:
            raise StockDoesntExist()

        return stock_domain_converter.to_domain(stock_sql_entity)

from domain.stock.stock_exceptions import StockDoesntExist
from domain.stock.stock import Stock
from domain.stock.stock_repository import StockRepository
from models import StockSQLEntity
from models.db import db


class StockSQLRepository(StockRepository):
    def find_stock_by_id(self, stock_id: int) -> Stock:
        stock_sql_entity = db.session.query(StockSQLEntity).get(stock_id)

        if stock_sql_entity is None:
            raise StockDoesntExist()

        stock = Stock(
            beginning_datetime=stock_sql_entity.beginningDatetime,
            booking_limit_datetime=stock_sql_entity.bookingLimitDatetime,
            identifier=stock_sql_entity.id,
            offer=stock_sql_entity.offer,
            price=stock_sql_entity.price,
            quantity=stock_sql_entity.quantity,
            is_soft_deleted=stock_sql_entity.isSoftDeleted,
            bookings=stock_sql_entity.bookings
        )
        return stock

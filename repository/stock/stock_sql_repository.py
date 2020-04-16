from domain.booking import StockDoesntExist
from domain.stock.stock import Stock
from domain.stock.stock_repository import StockRepository
from models import StockSQLEntity
from models.db import db


class StockSQLRepository(StockRepository):
    def find_stock_by_id(self, stock_id: int) -> Stock:
        stock_model = db.session.query(StockSQLEntity).get(stock_id)

        if stock_model is None:
            raise StockDoesntExist()

        stock = Stock(
            beginning_datetime=stock_model.beginningDatetime,
            booking_limit_datetime=stock_model.bookingLimitDatetime,
            identifier=stock_model.id,
            offer=stock_model.offer,
            price=stock_model.price,
            quantity=stock_model.quantity,
            is_soft_deleted=stock_model.isSoftDeleted,
            bookings=stock_model.bookings
        )
        return stock

from pcapi.domain.stock.stock import Stock
from pcapi.models import StockSQLEntity


def to_domain(stock_sql_entity: StockSQLEntity) -> Stock:
    return Stock(
        beginning_datetime=stock_sql_entity.beginningDatetime,
        booking_limit_datetime=stock_sql_entity.bookingLimitDatetime,
        identifier=stock_sql_entity.id,
        offer=stock_sql_entity.offer,
        price=stock_sql_entity.price,
        quantity=stock_sql_entity.quantity,
        is_soft_deleted=stock_sql_entity.isSoftDeleted,
        bookings=stock_sql_entity.bookings,
    )

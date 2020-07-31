from domain.beneficiary_bookings.stock import Stock
from models import StockSQLEntity


def to_domain(stock_sql_entity: StockSQLEntity) -> Stock:
    return Stock(
        beginningDatetime=stock_sql_entity.beginningDatetime,
        bookingLimitDatetime=stock_sql_entity.bookingLimitDatetime,
        id=stock_sql_entity.id,
        offerId=stock_sql_entity.offerId,
        price=stock_sql_entity.price,
        quantity=stock_sql_entity.quantity,
        dateCreated=stock_sql_entity.dateCreated,
        dateModified=stock_sql_entity.dateModified,
    )

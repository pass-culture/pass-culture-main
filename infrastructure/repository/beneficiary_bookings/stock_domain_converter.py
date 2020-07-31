from domain.beneficiary_bookings.stock import Stock


def to_domain(stock_sql_entity_view: object) -> Stock:
    return Stock(
        beginningDatetime=stock_sql_entity_view.beginningDatetime,
        bookingLimitDatetime=stock_sql_entity_view.bookingLimitDatetime,
        id=stock_sql_entity_view.id,
        offerId=stock_sql_entity_view.offerId,
        price=stock_sql_entity_view.price,
        quantity=stock_sql_entity_view.quantity,
        dateCreated=stock_sql_entity_view.dateCreated,
        dateModified=stock_sql_entity_view.dateModified,
        isSoftDeleted=stock_sql_entity_view.isSoftDeleted,
        isOfferActive=stock_sql_entity_view.isActive,
    )

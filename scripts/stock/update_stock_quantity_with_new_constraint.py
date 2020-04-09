from typing import List

from flask import Flask
from sqlalchemy import func
from sqlalchemy.orm import aliased

from connectors import redis
from models import StockSQLEntity, Booking
from repository import repository


def update_stock_quantity_for_negative_remaining_quantity(application: Flask) -> None:
    stocks = _get_stocks_with_negative_remaining_quantity()
    for stock in stocks:
        current_quantity = stock.quantity
        remaining_quantity_before_new_constraint = _get_old_remaining_quantity(stock)
        _update_stock_quantity(stock, remaining_quantity_before_new_constraint, application)
        new_quantity = stock.quantity
        print(f"Update on stock[{stock.id}], {current_quantity} => {new_quantity}")


def _get_stocks_with_negative_remaining_quantity() -> List[Stock]:
    stock_alias = aliased(Stock)
    booking_subquery = Booking.query \
        .filter(Booking.stockId == stock_alias.id) \
        .filter(Booking.isCancelled == False) \
        .with_entities(func.sum(Booking.quantity).label('remainingQuantity'),
                       Booking.stockId.label('stockId')) \
        .group_by(Booking.stockId) \
        .subquery()

    stocks = Stock.query \
        .join(booking_subquery) \
        .filter(Stock.id == booking_subquery.c.stockId) \
        .filter(Stock.hasBeenMigrated == None) \
        .filter(booking_subquery.c.remainingQuantity > Stock.quantity) \
        .all()

    return stocks


def update_stock_quantity_with_new_constraint(application: Flask, page_size=100) -> None:
    print("[UPDATE STOCK QUANTITY] Beginning of script")
    page = 0
    has_stocks_to_check = True

    while has_stocks_to_check:
        stocks_to_check = _get_stocks_to_check(page, page_size)

        for stock_to_check in stocks_to_check:
            remaining_quantity_before_new_constraint = _get_old_remaining_quantity(stock_to_check)
            if remaining_quantity_before_new_constraint != stock_to_check.remainingQuantity:
                _update_stock_quantity(stock_to_check, remaining_quantity_before_new_constraint, application)

        print(f"[UPDATE STOCK QUANTITY] Updated page {page} stocks")

        if len(stocks_to_check) < page_size:
            has_stocks_to_check = False
        page += 1

    print(f"[UPDATE STOCK QUANTITY] {(page + 1) * page_size} stocks checked")
    print("[UPDATE STOCK QUANTITY] End of script")


def _get_old_remaining_quantity(stock: StockSQLEntity) -> int:
    old_bookings_quantity = 0
    for booking in stock.bookings:
        if (not booking.isCancelled and not booking.isUsed) \
                or (booking.isUsed and booking.dateUsed is not None
                    and booking.dateUsed > stock.dateModified):
            old_bookings_quantity += booking.quantity
    return stock.quantity - old_bookings_quantity


def _get_stocks_to_check(page: int = 0, page_size: int = 100) -> List[StockSQLEntity]:
    return StockSQLEntity.query \
        .join(Booking) \
        .filter(StockSQLEntity.quantity != None) \
        .filter(StockSQLEntity.isSoftDeleted == False) \
        .filter(StockSQLEntity.hasBeenMigrated == None) \
        .order_by(StockSQLEntity.id) \
        .group_by(StockSQLEntity.id) \
        .offset(page * page_size) \
        .limit(page_size) \
        .all()


def _update_stock_quantity(stock_to_check: StockSQLEntity, remaining_quantity_before_new_constraint: int, application):
    remaining_quantity_before_new_constraint = remaining_quantity_before_new_constraint \
        if remaining_quantity_before_new_constraint > 0 else 0
    stock_to_check.quantity = remaining_quantity_before_new_constraint + stock_to_check.bookingsQuantity
    stock_to_check.hasBeenMigrated = True
    repository.save(stock_to_check)
    redis.add_offer_id(client=application.redis_client, offer_id=stock_to_check.offerId)

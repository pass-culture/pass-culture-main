from typing import List

from models import Stock, Booking
from repository import repository


def update_stock_available_with_new_constraint(page_size: int = 100):
    print("[UPDATE STOCK AVAILABLE] Beginning of script")
    page = 0
    has_stocks_to_check = True

    while has_stocks_to_check:
        stocks_to_check = _get_stocks_to_check(page, page_size)

        for stock_to_check in stocks_to_check:
            remaining_quantity_before_new_constraint = _get_old_remaining_quantity(stock_to_check)
            if remaining_quantity_before_new_constraint != stock_to_check.remainingQuantity:
                _update_stock_quantity(stock_to_check, remaining_quantity_before_new_constraint)

        print(f"[UPDATE STOCK AVAILABLE] Updated page {page} stocks")

        if len(stocks_to_check) < page_size:
            has_stocks_to_check = False
        page += 1

    print(f"[UPDATE STOCK AVAILABLE] {(page + 1) * page_size} stocks checked")
    print("[UPDATE STOCK AVAILABLE] End of script")


def _get_old_remaining_quantity(stock: Stock) -> int:
    old_bookings_quantity = 0
    for booking in stock.bookings:
        if (not booking.isCancelled and not booking.isUsed) \
                or (booking.isUsed and booking.dateUsed > stock.dateModified):
            old_bookings_quantity += booking.quantity
    return stock.available - old_bookings_quantity


def _get_stocks_to_check(page: int = 0, page_size: int = 100) -> List[Stock]:
    return Stock.query \
        .join(Booking) \
        .filter(Stock.available != None) \
        .filter(Stock.isSoftDeleted == False) \
        .filter(Stock.hasBeenMigrated == None) \
        .order_by(Stock.id) \
        .offset(page * page_size) \
        .limit(page_size) \
        .all()


def _update_stock_quantity(stock_to_check: Stock, remaining_quantity_before_new_constraint: int):
    stock_to_check.available = remaining_quantity_before_new_constraint + stock_to_check.bookingsQuantity
    stock_to_check.hasBeenMigrated = True
    repository.save(stock_to_check)


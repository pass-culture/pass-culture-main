import pcapi.core.bookings.api as bookings_api
from pcapi.repository import repository
from pcapi.models import Booking
from pcapi.models import Stock

def soft_delete_stock(stock_id):
    stock = Stock.query.filter(Stock.id == stock_id).first()
    bookings = _get_bookings_for_stock(stock_id)
    can_soft_delete = _check_bookings(bookings)

    if can_soft_delete:
        print(f"Soft-deleting stock {stock} and cancelling {len(bookings)} bookings...")
        for booking in bookings:
            bookings_api.cancel_booking_by_offerer(booking)
            print(f"Cancelled {booking}")
        print(f"Soft-deleted {stock}")
        stock.isSoftDeleted = True
        repository.save(stock)
        print("Done")

def _get_bookings_for_stock(stock_id):
    return (
        Booking.query
            .filter(Booking.isCancelled.is_(False))
            .filter(Booking.stockId == stock_id)
            .all()
    )

def _check_bookings(bookings):
    if not bookings:
        print("OK: Stock has no bookings")
        return True
    stock_can_be_deleted = True
    for booking in bookings:
        if booking.isUsed:
            print("KO: f{booking} is used")
            stock_can_be_deleted = False
        if booking.payments:
            print("KO: f{booking} has payments")
            stock_can_be_deleted = False
    return stock_can_be_deleted


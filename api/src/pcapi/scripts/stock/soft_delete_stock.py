import pcapi.core.bookings.api as bookings_api
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingStatus
import pcapi.core.finance.repository as finance_repository
from pcapi.core.offers.models import Stock
from pcapi.repository import repository


def soft_delete_stock(stock_id):
    stock = Stock.query.get(stock_id)
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
    return Booking.query.filter(Booking.status != BookingStatus.CANCELLED).filter(Booking.stockId == stock_id).all()


def _check_bookings(bookings):
    if not bookings:
        print("OK: Stock has no bookings")
        return True
    stock_can_be_deleted = True
    for booking in bookings:
        if booking.status is BookingStatus.USED:
            print("KO: f{booking} is used")
            stock_can_be_deleted = False
        if finance_repository.has_reimbursement(booking):
            print("KO: f{booking} has payments")
            stock_can_be_deleted = False
    return stock_can_be_deleted

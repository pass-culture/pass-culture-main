from datetime import timedelta
from repository import repository, booking_queries


def correct_unused_bookings_after_limit_end_time() -> None:
    bookings_to_process = booking_queries.find_not_used_and_not_cancelled_bookings_associated_to_outdated_stock()

    stocksToUpdate = []
    for booking in bookings_to_process:
        if booking.stock not in stocksToUpdate:
            stocksToUpdate.append(booking.stock)

    stocks_id_errors = []
    for stock in stocksToUpdate:
        bookings_associated_to_stock = list(filter(lambda booking: booking.stockId == stock.id, bookings_to_process))
        stock.available = len(bookings_associated_to_stock)
        try:
            repository.save(stock)
        except Exception:
            stocks_id_errors.append('something went wrong saving stock with id : ' + stock.id)

    bookins_id_errors = []
    for booking in bookings_to_process:
        booking.isUsed = True
        booking.dateUsed = (booking.stock.endDatetime + timedelta(hours=48))
        try:
            repository.save(booking)
        except Exception:
            bookins_id_errors.append('something went wrong saving booking with id : ' + booking.id)


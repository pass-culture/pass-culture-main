from datetime import timedelta

from models import ApiErrors
from repository import repository, booking_queries
from utils.logger import logger


def validate_bookings_associated_to_outdated_stocks() -> None:
    bookings_to_process = booking_queries.find_not_used_and_not_cancelled_bookings_associated_to_outdated_stock()

    stocks_to_update = []
    for booking in bookings_to_process:
        if booking.stock not in stocks_to_update:
            stocks_to_update.append(booking.stock)

    stocks_id_errors = []
    for stock in stocks_to_update:
        bookings_associated_to_stock = stock.bookings
        stock.available = len(bookings_associated_to_stock)
        try:
            repository.save(stock)
        except ApiErrors:
            stocks_id_errors.append(stock.id)

    bookings_id_errors = []
    for booking in bookings_to_process:
        booking.isUsed = True
        booking.dateUsed = (booking.stock.endDatetime + timedelta(hours=48))
        try:
            repository.save(booking)
        except ApiErrors:
            bookings_id_errors.append(booking.id)

    logger.error(f'something went wrong saving stock with ids :  {stocks_id_errors}')
    logger.error(f'something went wrong saving booking with ids : {bookings_id_errors}')

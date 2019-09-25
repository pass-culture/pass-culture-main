import csv
from datetime import timedelta
from io import StringIO
from typing import List, Iterator

from models.stock import Stock
from models.booking import Booking

BOOKING_CANCELLATION_DELAY = timedelta(hours=72)


def generate_bookings_details_csv(bookings: List[Booking]) -> str:
    output = StringIO()
    csv_lines = [booking.as_csv_row() for booking in bookings]
    writer = csv.writer(output, dialect=csv.excel, delimiter=";")
    writer.writerow(Booking.CSV_HEADER)
    writer.writerows(csv_lines)
    return output.getvalue()


def filter_bookings_to_compute_remaining_stock(stock: Stock) -> Iterator:
    return filter(lambda b: not b.isCancelled
                            and not b.isUsed
                            or (b.isUsed
                                and b.dateUsed
                                and b.dateUsed >= stock.dateModified),
                  stock.bookings)

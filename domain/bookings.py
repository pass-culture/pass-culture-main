from models.booking import Booking

import csv
from io import StringIO
from typing import List


def generate_offer_bookings_details_csv(Booking):
    return generate_bookings_details_csv(Booking)


def generate_bookings_details_csv(bookings: List[Booking]) -> str:
    output = StringIO()
    csv_lines = [booking.as_csv_row() for booking in bookings]
    writer = csv.writer(output, dialect=csv.excel, delimiter=";")
    writer.writerow(Booking.CSV_HEADER)
    writer.writerows(csv_lines)
    return output.getvalue()

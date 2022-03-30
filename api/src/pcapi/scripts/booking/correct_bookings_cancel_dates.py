import csv
import logging

from pcapi.core.bookings.models import Booking
from pcapi.models import db
from pcapi.repository import repository


logger = logging.getLogger(__name__)


BATCH_SIZE = 100


def run(csv_file_path: str) -> None:
    logger.info("[CORRECT BOOKINGS CANCEL_DATE] START")
    logger.info("[CORRECT BOOKINGS CANCEL_DATE] STEP 1 - Read CSV file")
    with open(csv_file_path, encoding="utf-8") as csv_file:
        csv_rows = list(csv.reader(csv_file))

    csv_rows_iterable = csv_rows[1:]
    batches = [csv_rows_iterable[index : index + BATCH_SIZE] for index in range(0, len(csv_rows_iterable), BATCH_SIZE)]

    for batch in batches:
        try:
            booking_to_update_list = []
            for row in batch:
                booking_id, cancellation_date = row[0], row[1]
                booking_to_update = Booking.query.get(booking_id)
                booking_to_update.cancellationDate = cancellation_date
                booking_to_update_list.append(booking_to_update)

            db.session.execute("ALTER TABLE booking DISABLE TRIGGER stock_update_cancellation_date;")
            repository.save(*booking_to_update_list)
        finally:
            db.session.execute("ALTER TABLE booking ENABLE TRIGGER stock_update_cancellation_date;")

    logger.info("[CORRECT BOOKINGS CANCEL_DATE] END")

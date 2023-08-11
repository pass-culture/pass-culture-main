# fmt: off
from pcapi.flask_app import app


app.app_context().push()
# fmt: on

import logging
import sys
import time
import typing as t
from unittest import mock

import pcapi.core.bookings.api as bookings_api
import pcapi.core.bookings.models as bookings_models
from pcapi.scripts.script_utils import get_eta
from pcapi.scripts.script_utils import log_remote_to_local_cmd


logger = logging.getLogger(__name__)

LOG_EVERY_N_LINES = 100

OUT_EMAIL_WITH_BOOKING_FILE_PATH = "/tmp/OUT_emails_with_booking.csv"


def process_offers(lines: t.Iterable[str], first_line_to_process: int) -> list[str]:
    elapsed_per_batch = []
    start_time = time.perf_counter()
    total_lines = len(list(lines))
    emails = []
    for i, line in enumerate(lines, start=1):
        if i < first_line_to_process:
            continue
        offer_id = int(line)
        bookings = (
            bookings_models.Booking.query.filter_by(
                status=bookings_models.BookingStatus.CONFIRMED,
            )
            .join(bookings_models.Booking.stock)
            .filter_by(offerId=offer_id)
        )
        cancelled_ids = []
        for booking in bookings:
            try:
                process_booking(booking)
            except Exception:  # pylint: disable=broad-exception-caught
                bookings_api.logger.exception(
                    "Could not cancel booking for rejected offer",
                    extra={
                        "booking": booking.id,
                        "offer": offer_id,
                    },
                )
                print(f"ERR: error while cancelling booking {booking.id} for offer {offer_id}")
            else:
                emails.append(booking.user.email)
                cancelled_ids.append(booking.id)
        if cancelled_ids:
            logger.info(
                "Cancelled bookings for rejected offer",
                extra={
                    "bookings": cancelled_ids,
                    "offer": offer_id,
                },
            )

        if i % LOG_EVERY_N_LINES == 0:
            elapsed_per_batch.append(int(time.perf_counter() - start_time))
            eta = get_eta(total_lines, i, elapsed_per_batch, LOG_EVERY_N_LINES)
            print(f"  => OK: {i} | eta = {eta}")
            start_time = time.perf_counter()

    return emails


def process_booking(booking: bookings_models.Booking) -> None:
    with mock.patch.multiple(
        "pcapi.core.bookings.api",
        update_external_user=mock.DEFAULT,
        update_external_pro=mock.DEFAULT,
    ):
        with mock.patch("pcapi.core.search.async_index_offer_ids"):
            with mock.patch("pcapi.analytics.amplitude.events.track_cancel_booking_event"):
                bookings_api._cancel_booking(
                    booking,
                    reason=bookings_models.BookingCancellationReasons.FRAUD,
                )


def main() -> None:
    offer_csv_path = sys.argv[1]
    logger.info(
        "[mass cancel bookings] Reading offers csv extract %s",
        offer_csv_path,
    )

    try:
        first_line_to_process = int(sys.argv[2])
    except IndexError:
        first_line_to_process = 1
    with open(offer_csv_path, encoding="utf-8") as fp:
        emails = process_offers(fp.readlines(), first_line_to_process)

        output_files: list[str] = []

        with open(OUT_EMAIL_WITH_BOOKING_FILE_PATH, "w+", encoding="utf-8") as email_with_booking_csv:
            emails = list(set(emails))
            email_with_booking_csv.write("\n".join(map(str, emails)))
            logger.info("%s emails with booking written in %s", len(emails), OUT_EMAIL_WITH_BOOKING_FILE_PATH)
            output_files.append(OUT_EMAIL_WITH_BOOKING_FILE_PATH)

        log_remote_to_local_cmd(output_files)


if __name__ == "__main__":
    start = time.time()
    main()
    logger.info("Total duration: %s seconds", time.time() - start)

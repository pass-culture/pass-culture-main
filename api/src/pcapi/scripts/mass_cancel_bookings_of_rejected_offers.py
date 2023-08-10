# fmt: off
from pcapi.flask_app import app; app.app_context().push()
# fmt: on

import sys
import typing as t
from unittest import mock

import pcapi.core.bookings.api as bookings_api
import pcapi.core.bookings.models as bookings_models


LOG_EVERY_N_LINES = 100


def process_offers(lines: t.Iterable[str], first_line_to_process: int) -> None:
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
            except Exception:
                bookings_api.logger.exception(
                    "Could not cancel booking for rejected offer",
                    extra={
                        "booking": booking.id,
                        "offer": offer_id,
                    },
                )
                print(f"ERR: error while cancelling booking {booking.id} for offer {offer_id}")
            else:
                cancelled_ids.append(booking.id)
        if cancelled_ids:
            bookings_api.logger.info(
                "Cancelled bookings for rejected offer",
                extra={
                    "bookings": cancelled_ids,
                    "offer": offer_id,
                },
            )

        if i % LOG_EVERY_N_LINES == 0:
            print(f"Processed line {i}")


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


def main():
    offer_csv_path = sys.argv[1]
    try:
        first_line_to_process = int(sys.argv[2])
    except IndexError:
        first_line_to_process = 1
    with open(offer_csv_path) as fp:
        process_offers(fp.readlines(), first_line_to_process)


if __name__ == "__main__":
    main()

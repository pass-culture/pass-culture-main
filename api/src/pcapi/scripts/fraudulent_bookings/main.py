"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=prd \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=pc-44591-fraudulent-bookings \
  -f NAMESPACE=fraudulent_bookings \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import csv
import logging
import os
import typing

import sqlalchemy.orm as sa_orm

from pcapi.core.bookings import models as bookings_models
from pcapi.models import db


logger = logging.getLogger(__name__)


def _read_csv_file(filename: str) -> typing.Iterator[dict[str, str]]:
    namespace_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(namespace_dir, filename), "r", encoding="utf-8") as csv_file:
        csv_rows = csv.DictReader(csv_file, delimiter=",")
        yield from csv_rows


def main(author_id: int) -> None:
    rows = _read_csv_file("bookings.csv")
    for row in rows:
        booking_id = int(row["ID résa"])
        booking = (
            db.session.query(bookings_models.Booking)
            .filter_by(id=booking_id)
            .options(sa_orm.joinedload(bookings_models.Booking.fraudulentBookingTag))
            .one_or_none()
        )
        if booking:
            if booking.fraudulentBookingTag:
                logger.warning(
                    "Booking is already fraudulent", extra={"booking_id": booking.id, "venue_id": booking.venueId}
                )
            else:
                logger.info("Mark booking as fraudulent", extra={"booking_id": booking.id, "venue_id": booking.venueId})
                fraudulent_booking_tag = bookings_models.FraudulentBookingTag(
                    bookingId=booking.id, venueId=booking.venueId, authorId=author_id
                )
                db.session.add(fraudulent_booking_tag)
                db.session.flush()
        else:
            logger.warning("Booking not found", extra={"booking_id": booking_id})


if __name__ == "__main__":
    from pcapi.app import app

    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--author-id", type=int, required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    main(args.author_id)

    if args.apply:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()

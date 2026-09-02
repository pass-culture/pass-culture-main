"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-43486-mark-some-bookings-as-reimbursed \
  -f NAMESPACE=mark_as_reimbursed \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

from pcapi.core.bookings import models as bookings_models
from pcapi.models import db


logger = logging.getLogger(__name__)


def main(booking_ids: list[int]) -> None:
    bookings = db.session.query(bookings_models.Booking).where(bookings_models.Booking.id.in_(booking_ids)).all()
    """for booking in bookings:
        booking.status = bookings_models.BookingStatus.REIMBURSED
        db.session.add(booking)"""
    stock = bookings[0].stock
    stock.quantity = 0
    stock.dnBookedQuantity = 0
    db.session.add(stock)


if __name__ == "__main__":
    from pcapi.app import app

    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--booking-ids", type=int, nargs="+", required=True)
    args = parser.parse_args()

    main(args.booking_ids)

    if args.apply:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()

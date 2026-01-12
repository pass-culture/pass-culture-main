"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml \
  -f ENVIRONMENT=testing \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-39731-send-booking-cancellation-mail \
  -f NAMESPACE=send_booking_cancelled_mail \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

from sqlalchemy import select

import pcapi.core.mails.transactional as transactional_mails
from pcapi.app import app
from pcapi.core.bookings.models import Booking
from pcapi.models import db


logger = logging.getLogger(__name__)


def main(not_dry: bool) -> None:
    booking_ids = [
        65365906,
        65372427,
        65365931,
        65372543,
        65372442,
        65372457,
        65363719,
        65235160,
        65372355,
        65320311,
        65362893,
        65331172,
        65371927,
        65363074,
    ]
    bookings = db.session.scalars(select(Booking).where(Booking.id.in_(booking_ids))).all()
    for booking in bookings:
        transactional_mails.send_booking_cancellation_emails_to_user_and_offerer(booking, booking.cancellationReason)


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    main(not_dry=args.not_dry)

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()

"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml \
  -f ENVIRONMENT=testing \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=BSR-fix-manual-actions-in-BO \
  -f NAMESPACE=cancel_validated_incident \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

import pcapi.core.bookings.models as bookings_models
import pcapi.core.finance.models as finance_models
from pcapi.app import app
from pcapi.models import db


logger = logging.getLogger(__name__)


def main(booking_id: int) -> None:
    booking = db.session.query(bookings_models.Booking).filter(bookings_models.Booking.id == booking_id).one()
    booking.status = bookings_models.BookingStatus.REIMBURSED
    booking.dateUsed = booking.pricings[0].valueDate

    finance_event_to_cancel = (
        db.session.query(finance_models.FinanceEvent)
        .filter(
            finance_models.FinanceEvent.bookingId == booking_id,
            finance_models.FinanceEvent.status == finance_models.FinanceEventStatus.READY,
        )
        .one()
    )
    finance_event_to_cancel.status = finance_models.FinanceEventStatus.CANCELLED

    finance_incident = booking.incidents[0].incident
    finance_incident.status = finance_models.IncidentStatus.CANCELLED


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    parser.add_argument("--booking-id", type=int, required=True)
    args = parser.parse_args()

    main(booking_id=args.booking_id)

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()

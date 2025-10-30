"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml   -f ENVIRONMENT=testing   -f BRANCH_NAME=PC-38599-fix-booking-stuck-on-soft-deleted-venue   -f NAMESPACE=destuck_old_booking   -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

from pcapi.app import app
from pcapi.core.finance import models as finance_models
from pcapi.core.finance.api import add_event
from pcapi.models import db


logger = logging.getLogger(__name__)


def main(booking_id: int) -> None:
    finance_event = (
        db.session.query(finance_models.FinanceEvent).filter(finance_models.FinanceEvent.bookingId == booking_id).one()
    )
    finance_event.status = finance_models.FinanceEventStatus.NOT_TO_BE_PRICED
    db.session.add(finance_event)
    db.session.flush()

    add_event(finance_models.FinanceEventMotive.BOOKING_USED, finance_event.booking)


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

"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-42743-edit-cancellation-limit-date \
  -f NAMESPACE=edit_cancellation_date \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

import sqlalchemy as sa

from pcapi.core.bookings import models as bookings_models
from pcapi.models import db
from pcapi.utils import date as date_utils


logger = logging.getLogger(__name__)


def main(stock_id: int) -> None:
    db.session.execute(
        sa.update(bookings_models.Booking)
        .where(
            bookings_models.Booking.status == bookings_models.BookingStatus.CONFIRMED,
            bookings_models.Booking.stockId == stock_id,
        )
        .values(
            cancellationLimitDate=date_utils.get_naive_utc_now(),
        ),
        execution_options={"synchronize_session": False},
    )


if __name__ == "__main__":
    from pcapi.app import app

    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--stock-id", type=int, required=True)
    args = parser.parse_args()

    main(args.stock_id)

    if args.apply:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()

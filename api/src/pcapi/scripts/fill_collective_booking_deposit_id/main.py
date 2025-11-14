"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml \
  -f ENVIRONMENT=testing \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-38730-eac-fill-educational-deposit-id-collective-booking \
  -f NAMESPACE=fill_collective_booking_deposit_id \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

from pcapi.app import app
from pcapi.core.educational import models
from pcapi.models import db


logger = logging.getLogger(__name__)


def main() -> None:
    # all collective bookings that have been confirmed must be linked to a deposit
    bookings_query = db.session.query(models.CollectiveBooking).filter(
        models.CollectiveBooking.educationalDepositId.is_(None),
        models.CollectiveBooking.confirmationDate.is_not(None),
    )

    logger.info("Found %s bookings to process", bookings_query.count())

    deposit_id_by_year_id_institution_id = {}
    for deposit in db.session.query(models.EducationalDeposit):
        key = (deposit.educationalYearId, deposit.educationalInstitutionId)
        if key in deposit_id_by_year_id_institution_id:
            logger.warning("Found multiple deposits for year and institution %s", key)
            raise ValueError

        deposit_id_by_year_id_institution_id[key] = deposit.id

    for booking in bookings_query.yield_per(1000):
        booking_deposit_id = deposit_id_by_year_id_institution_id.get(
            (booking.educationalYearId, booking.educationalInstitutionId)
        )

        if booking_deposit_id is None:
            logger.warning("No deposit found for booking %s", booking.id)
            continue

        booking.educationalDepositId = booking_deposit_id


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    main()

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()

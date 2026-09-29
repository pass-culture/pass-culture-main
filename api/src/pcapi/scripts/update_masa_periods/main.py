"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=master \
  -f NAMESPACE=update_masa_periods \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import datetime
import logging

from pcapi.core.educational import models
from pcapi.models import db
from pcapi.utils.db import make_timerange


logger = logging.getLogger(__name__)


def main() -> None:
    first_period_date_time = datetime.datetime(2026, 9, 15)
    second_period_date_time = datetime.datetime(2027, 1, 15)

    # fetch the second period deposits (01/2027 -> 08/2027) and delete them
    second_period_deposits = (
        db.session.query(models.EducationalDeposit)
        .filter(
            models.EducationalDeposit.ministry == models.Ministry.AGRICULTURE,
            models.EducationalDeposit.period.op("@>")(second_period_date_time),
        )
        .all()
    )

    second_period_end = second_period_deposits[0].period.upper

    total_amount = sum(deposit.amount for deposit in second_period_deposits)
    logger.info("Found %s deposits with total amount %s for second period", len(second_period_deposits), total_amount)

    deposit_ids = [deposit.id for deposit in second_period_deposits]
    db.session.query(models.EducationalDeposit).filter(models.EducationalDeposit.id.in_(deposit_ids)).delete()
    db.session.flush()

    # fetch the first period deposits (09/2026 -> 12/2026) and set the period to the full school year
    first_period_deposits = (
        db.session.query(models.EducationalDeposit)
        .filter(
            models.EducationalDeposit.ministry == models.Ministry.AGRICULTURE,
            models.EducationalDeposit.period.op("@>")(first_period_date_time),
        )
        .all()
    )

    first_period_start = first_period_deposits[0].period.lower

    total_amount = sum(deposit.amount for deposit in first_period_deposits)
    logger.info("Found %s deposits with total amount %s for first period", len(first_period_deposits), total_amount)

    time_range = make_timerange(first_period_start, second_period_end)
    logger.info("Setting deposits period to %s", time_range)

    deposit_ids = [deposit.id for deposit in first_period_deposits]
    db.session.query(models.EducationalDeposit).filter(models.EducationalDeposit.id.in_(deposit_ids)).update(
        {models.EducationalDeposit.period: time_range},
        synchronize_session=False,
    )


if __name__ == "__main__":
    from pcapi.app import app

    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    main()

    if args.apply:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()

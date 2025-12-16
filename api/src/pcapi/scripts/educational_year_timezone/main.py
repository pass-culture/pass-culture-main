"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml \
  -f ENVIRONMENT=testing \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-39105-eac-back-annee-scolaire-et-periodes-en-timezone-paris \
  -f NAMESPACE=educational_year_timezone \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import datetime
import logging
from functools import cache

import pytz

from pcapi.app import app
from pcapi.core.educational import models
from pcapi.models import db
from pcapi.utils import db as db_utils


logger = logging.getLogger(__name__)

PARIS_TZ = pytz.timezone("Europe/Paris")


def main() -> None:
    """
    The values we currently store for EducationalYear.beginningDate and EducationalYear.expirationDate
    are considered UTC, but on the Adage side the timezone is actually Europe/Paris
    We need to update the EducationalDeposit.period column as well because it is inferred from the educational year

    We need to keep the same date and time but change the timezone to Europe/Paris
    This will shift the datetime value by -2 hours in september and -1 hour in january
    """

    years = db.session.query(models.EducationalYear)

    for year in years:
        _process_year(year)

    _process_deposit_periods()


def _process_year(year: models.EducationalYear) -> None:
    logger.info(
        "Current year data",
        extra={
            "year": year.displayed_year,
            "start": year.beginningDate.isoformat(),
            "end": year.expirationDate.isoformat(),
        },
    )
    year.beginningDate = PARIS_TZ.localize(year.beginningDate)
    year.expirationDate = PARIS_TZ.localize(year.expirationDate)
    logger.info(
        "After update year data",
        extra={
            "year": year.displayed_year,
            "start": year.beginningDate.isoformat(),
            "end": year.expirationDate.isoformat(),
        },
    )

    db.session.flush()


def _process_deposit_periods() -> None:
    deposits = db.session.query(models.EducationalDeposit).yield_per(1000)
    for deposit in deposits:
        assert deposit.period is not None
        lower = deposit.period.lower
        upper = deposit.period.upper

        deposit.period = db_utils.make_timerange(_get_localized_datetime(lower), _get_localized_datetime(upper))

    db.session.flush()


@cache
def _get_localized_datetime(date_time: datetime.datetime) -> datetime.datetime:
    # this is called on deposit period bounds
    # number of different values is low (max. 4 per educational year)
    # but we call it for each deposit so we use a cache
    return PARIS_TZ.localize(date_time)


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

"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml \
  -f ENVIRONMENT=testing \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-39021-update-period-deposit \
  -f NAMESPACE=update_educational_deposit_period \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import datetime
import logging

from psycopg2.extras import DateTimeRange

from pcapi.app import app
from pcapi.core.educational import models
from pcapi.core.educational import utils
from pcapi.models import db
from pcapi.utils import db as db_utils


logger = logging.getLogger(__name__)

# MeN, MER, AGRI -> two periods per educational year
MINISTRY_TWO_PERIODS = {models.Ministry.EDUCATION_NATIONALE, models.Ministry.MER, models.Ministry.AGRICULTURE}
# ARMEES (and MeG) -> period = educational year
MINISTRY_ONE_PERIOD = {models.Ministry.ARMEES}


def _get_period_by_ministry(ministry: models.Ministry, year: models.EducationalYear) -> DateTimeRange:
    if ministry in MINISTRY_TWO_PERIODS:
        return utils.get_educational_year_first_period(year)

    if ministry in MINISTRY_ONE_PERIOD:
        return db_utils.make_timerange(year.beginningDate, year.expirationDate)

    raise ValueError("Invalid ministry")


def main() -> None:
    period_start = datetime.datetime(year=2025, month=9, day=1)
    current_year = (
        db.session.query(models.EducationalYear).filter(models.EducationalYear.beginningDate == period_start).one()
    )

    current_year_meg_institutions = (
        db.session.query(models.EducationalInstitution.id)
        .join(models.EducationalInstitution.programAssociations)
        .join(models.EducationalInstitutionProgramAssociation.program)
        .filter(
            models.EducationalInstitutionProgramAssociation.timespan.op("@>")(period_start),
            models.EducationalInstitutionProgram.name == models.PROGRAM_MARSEILLE_EN_GRAND,
        )
    )
    meg_institutions_ids = set(id for (id,) in current_year_meg_institutions)

    deposits = (
        db.session.query(models.EducationalDeposit)
        .filter(models.EducationalDeposit.educationalYearId == current_year.adageId)
        .yield_per(1000)
    )

    for deposit in deposits:
        is_meg = deposit.educationalInstitutionId in meg_institutions_ids

        if is_meg:
            deposit.period = db_utils.make_timerange(current_year.beginningDate, current_year.expirationDate)
        else:
            deposit.period = _get_period_by_ministry(ministry=deposit.ministry, year=current_year)

    db.session.flush()


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

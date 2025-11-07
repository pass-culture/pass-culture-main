"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml \
  -f ENVIRONMENT=testing \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-38702-script-fill-period-educational-deposit \
  -f NAMESPACE=fill_educational_deposit_period \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import datetime
import logging

from sqlalchemy import orm as sa_orm

from pcapi.app import app
from pcapi.core.educational import models
from pcapi.models import db
from pcapi.utils import db as db_utils


logger = logging.getLogger(__name__)


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

    # period_end is the start of the next period because the bounds of DateTimeRange are "[)"
    period_end = datetime.datetime(year=2026, month=1, day=1)

    deposits = (
        db.session.query(models.EducationalDeposit)
        .options(sa_orm.joinedload(models.EducationalDeposit.educationalYear))
        .yield_per(1000)
    )

    for deposit in deposits:
        is_past = deposit.educationalYearId != current_year.adageId
        is_men = deposit.ministry == models.Ministry.EDUCATION_NATIONALE
        is_meg = deposit.educationalInstitutionId in meg_institutions_ids
        if is_past or not is_men or is_meg:
            # past year, non-MeN or MeG -> period is equal to educational year
            deposit.period = db_utils.make_timerange(
                deposit.educationalYear.beginningDate, deposit.educationalYear.expirationDate
            )
        else:
            # current year, MeN and not MeG -> period is equal to [start of educational year, end of calendar year]
            deposit.period = db_utils.make_timerange(period_start, period_end)

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

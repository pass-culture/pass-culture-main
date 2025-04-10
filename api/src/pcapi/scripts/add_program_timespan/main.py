"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/PC-35607-eac-program-timespan-meg/api/src/pcapi/scripts/add_program_timespan/main.py

"""

import argparse
import datetime
import logging

from pcapi.app import app
from pcapi.core.educational import constants as educational_constants
from pcapi.core.educational import models
from pcapi.models import db
from pcapi.utils import db as db_utils


logger = logging.getLogger(__name__)

INSTITUTION_IDS_IN = ["0131208T", "0131563D", "0131644S", "0131856X", "0132287R", "0132429V", "0130538P", "0130899G"]
INSTITUTION_IDS_OUT = ["0130868Y", "0130942D", "0130795U", "0130648J", "0132184D", "0130927M", "0130879K", "0130838R"]

END_DATE = datetime.datetime(2024, 12, 15)
START_DATE = datetime.datetime(2024, 12, 15)


def update_institutions_timespan(
    institution_ids: list[str],
    program: models.EducationalInstitutionProgram,
    start_date: datetime.datetime,
    end_date: datetime.datetime | None,
) -> None:
    """Update the timespan for a list of institutions."""
    for institution_id in institution_ids:
        institution = (
            db.session.query(models.EducationalInstitution)
            .filter(models.EducationalInstitution.institutionId == institution_id)
            .one()
        )

        association = (
            db.session.query(models.EducationalInstitutionProgramAssociation)
            .filter(
                models.EducationalInstitutionProgramAssociation.institution == institution,
                models.EducationalInstitutionProgramAssociation.program == program,
            )
            .one()
        )

        association.timespan = db_utils.make_timerange(start_date, end_date)
        db.session.add(association)
    db.session.flush()


def main(not_dry: bool) -> None:
    """Main function to update program timespans for institutions."""
    meg_program = (
        db.session.query(models.EducationalInstitutionProgram)
        .filter(models.EducationalInstitutionProgram.name == models.PROGRAM_MARSEILLE_EN_GRAND)
        .one()
    )

    # Update institutions that are joining the program
    update_institutions_timespan(INSTITUTION_IDS_IN, meg_program, START_DATE, None)

    # Update institutions that are leaving the program
    update_institutions_timespan(INSTITUTION_IDS_OUT, meg_program, educational_constants.MEG_BEGINNING_DATE, END_DATE)


if __name__ == "__main__":
    logger.info("Starting script")

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

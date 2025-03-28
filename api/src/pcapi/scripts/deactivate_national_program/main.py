"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/PC-34824-deactivate-national-program-olympiades-culturelles/api/src/pcapi/scripts/deactivate_national_program/main.py

"""

import argparse
import logging

from pcapi.app import app
from pcapi.core.educational import models as educational_models
from pcapi.models import db


logger = logging.getLogger(__name__)

PROGRAM_NAME = "Olympiade culturelle de PARIS 2024"


def main() -> None:
    program: educational_models.NationalProgram = (
        db.session.query(educational_models.NationalProgram)
        .filter(educational_models.NationalProgram.name == PROGRAM_NAME)
        .one()
    )
    program.isActive = False
    logger.info("Program found, isActive set to False")
    db.session.add(program)
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

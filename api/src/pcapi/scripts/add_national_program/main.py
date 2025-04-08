"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/PC-35572-new-national-program/api/src/pcapi/scripts/add_national_program/main.py

"""

import argparse
import logging

from pcapi.app import app
from pcapi.core.educational import models
from pcapi.models import db


logger = logging.getLogger(__name__)

PROGRAM_NAME = "PRADO (plan national de la DILCRAH)"


def main() -> None:
    all_domains = db.session.query(models.EducationalDomain).all()
    program = models.NationalProgram(name=PROGRAM_NAME, domains=all_domains)

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

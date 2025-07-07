"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/pc-36202-remove-undefined-credits/api/src/pcapi/scripts/remove_undefined_credits/main.py

"""

import argparse
import logging

import sqlalchemy as sa

from pcapi.app import app
from pcapi.core.offers.models import Mediation
from pcapi.models import db


logger = logging.getLogger(__name__)


def delete_undefined_credits() -> None:
    db.session.execute(
        sa.update(Mediation).where(Mediation.credit == "undefined").values(credit=None),
        execution_options={"synchronize_session": False},
    )


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    delete_undefined_credits()

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()

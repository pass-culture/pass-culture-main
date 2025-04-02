"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions): 

https://github.com/pass-culture/pass-culture-main/blob/ogeber/pc-35452-script-isopentopublicfalse/api/src/pcapi/scripts/rectify_open_to_public_false/main.py

"""

import argparse
import logging

from pcapi.app import app
from pcapi.core.offerers.models import Venue
from pcapi.models import db


logger = logging.getLogger(__name__)


def main() -> None:
    venues_to_update = (
        db.session.query(Venue)
        .filter(Venue.isPermanent == False, Venue.isOpenToPublic == True)
        .update(dict(isOpenToPublic=False))
    )
    logger.info("Venues to update : %d", venues_to_update)


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

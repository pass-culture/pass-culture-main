"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/bdalbianco/PC-37584_update_empty_venue_publicName/api/src/pcapi/scripts/venue/main.py

"""

import argparse
import logging

import sqlalchemy as sa

from pcapi.app import app
from pcapi.core.offerers import models as offerer_models
from pcapi.models import db


logger = logging.getLogger(__name__)


def main(not_dry: bool) -> None:
    venues = (
        db.session.query(offerer_models.Venue)
        .filter(sa.or_(offerer_models.Venue.publicName == None, offerer_models.Venue.publicName == ""))
        .options(sa.orm.load_only(offerer_models.Venue.publicName, offerer_models.Venue.name))
        .update({"publicName": offerer_models.Venue.name}, synchronize_session=False)
    )
    logger.info(f"Updated {venues} venues publicName")
    pass


if __name__ == "__main__":
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

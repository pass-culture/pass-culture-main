"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/pcharlet/pc-36870-script-update-venue-public-name/api/src/pcapi/scripts/update_venue_public_name/main.py

"""

import argparse
import logging
import re

from sqlalchemy import func

from pcapi.app import app
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db


logger = logging.getLogger(__name__)


def main() -> None:
    venues_to_update_1 = db.session.query(offerers_models.Venue).filter(
        func.lower(offerers_models.Venue.publicName).like("%(lieu administratif)%")
    )
    insensitive_1 = re.compile(re.escape("(lieu administratif)"), re.IGNORECASE)
    for venue in venues_to_update_1.all():
        venue.publicName = insensitive_1.sub("", venue.publicName).strip()
        logger.info("Update publicName for venue %d", venue.id)
        db.session.add(venue)

    venues_to_update_2 = db.session.query(offerers_models.Venue).filter(
        func.lower(offerers_models.Venue.publicName).like("%/ lieu administratif%")
    )
    insensitive_2 = re.compile(re.escape("/ lieu administratif"), re.IGNORECASE)
    for venue in venues_to_update_2.all():
        venue.publicName = insensitive_2.sub("", venue.publicName).strip()
        logger.info("Update publicName for venue %d", venue.id)
        db.session.add(venue)

    venues_to_update_3 = db.session.query(offerers_models.Venue).filter(
        func.lower(offerers_models.Venue.publicName).like("% - lieu administratif%")
    )
    insensitive_3 = re.compile(re.escape(" - lieu administratif"), re.IGNORECASE)
    for venue in venues_to_update_3.all():
        venue.publicName = insensitive_3.sub("", venue.publicName).strip()
        logger.info("Update publicName for venue %d", venue.id)
        db.session.add(venue)

    venues_to_update_4 = db.session.query(offerers_models.Venue).filter(
        func.lower(offerers_models.Venue.publicName).like("%-lieu administratif%")
    )
    insensitive_4 = re.compile(re.escape("-lieu administratif"), re.IGNORECASE)
    for venue in venues_to_update_4.all():
        venue.publicName = insensitive_4.sub("", venue.publicName).strip()
        logger.info("Update publicName for venue %d", venue.id)
        db.session.add(venue)


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

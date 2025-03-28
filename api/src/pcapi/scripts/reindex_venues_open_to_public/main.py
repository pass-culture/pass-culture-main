"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions): 

https://github.com/pass-culture/pass-culture-main/blob/ogeber/pc-35418-script-to-reindex-isOpenToPublic-venues/api/src/pcapi/scripts/reindex_venues_open_to_public/main.py

"""

import argparse
import logging

from pcapi.app import app
from pcapi.core import search
from pcapi.core.offerers.models import Venue
from pcapi.models import db


logger = logging.getLogger(__name__)


def get_venues_open_to_public() -> list[Venue]:
    return db.session.query(Venue).filter(Venue.isOpenToPublic.is_(True)).all()


def get_venues_not_open_to_public() -> list[Venue]:
    return db.session.query(Venue).filter(Venue.isOpenToPublic.is_(False)).all()


def main(not_dry: bool) -> None:
    venues_open_to_public = get_venues_open_to_public()
    venue_open_to_public_ids = [venue.id for venue in venues_open_to_public]
    venues_not_open_to_public = get_venues_not_open_to_public()
    venue_not_open_to_public_ids = [venue.id for venue in venues_not_open_to_public]
    if not_dry:
        search.unindex_venue_ids(venue_not_open_to_public_ids)
        search.reindex_venue_ids(venue_open_to_public_ids)
    else:
        logger.info("Reindex %d venues", len(venue_open_to_public_ids))


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

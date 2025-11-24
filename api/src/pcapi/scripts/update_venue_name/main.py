"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml \
  -f ENVIRONMENT=testing \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=pcharlet/pc-38853-script-rename-venue \
  -f NAMESPACE=update_venue_name \
  -f SCRIPT_ARGUMENTS="";

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
    search_and_replacement = [
        ("%lieu administratif-%", "lieu administratif-"),
        ("%lieu administratif -%", "lieu administratif -"),
        ("%lieu administratif-%", "lieu administratif-"),
        ("%- lieu administratif%", "- lieu administratif"),
        ("%-lieu administratif%", "-lieu administratif"),
        ("%(lieu administratif)%", "(lieu administratif)"),
        ("%/ lieu administratif%", "/ lieu administratif"),
        ("%lieu administratif%", "lieu administratif"),
    ]
    for search, part_to_remove in search_and_replacement:
        venues_to_update = db.session.query(offerers_models.Venue).filter(
            func.lower(offerers_models.Venue.name).like(search)
        )
        case_insensitive_part_to_remove = re.compile(re.escape(part_to_remove), re.IGNORECASE)
        for venue in venues_to_update.all():
            venue.name = case_insensitive_part_to_remove.sub("", venue.name).strip()
            logger.info("Update name for venue %d", venue.id)
            db.session.add(venue)
    for search, part_to_remove in search_and_replacement:
        venues_to_update = db.session.query(offerers_models.Venue).filter(
            func.lower(offerers_models.Venue.publicName).like(search)
        )
        case_insensitive_part_to_remove = re.compile(re.escape(part_to_remove), re.IGNORECASE)
        for venue in venues_to_update.all():
            venue.publicName = case_insensitive_part_to_remove.sub("", venue.publicName).strip()
            logger.info("Update publicName for venue %d", venue.id)
            db.session.add(venue)


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    main()

    if args.not_dry:
        db.session.commit()
        logger.info("Finished")
    else:
        db.session.rollback()
        logger.info("Finished dry run, rollback")

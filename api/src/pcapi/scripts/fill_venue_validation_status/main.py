"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-41265/script_fill_venue_validation_status \
  -f NAMESPACE=fill_venue_validation_status \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

import sqlalchemy.orm as sa_orm

from pcapi.app import app
from pcapi.core.offerers import models
from pcapi.models import db
from pcapi.utils.chunks import get_chunks


logger = logging.getLogger(__name__)


def main(apply: bool = False) -> None:
    query = (
        db.session.query(models.Venue)
        .filter(models.Venue.validationStatus == None)
        .with_entities(models.Venue.id)
        .yield_per(10_000)
    )

    venue_ids = {row[0] for row in query}

    for ids in get_chunks(venue_ids, chunk_size=100):
        venues = (
            db.session.query(models.Venue)
            .filter(models.Venue.id.in_(ids))
            .options(sa_orm.joinedload(models.Venue.managingOfferer).load_only(models.Offerer.validationStatus))
        )

        for venue in venues:
            venue.validationStatus = venue.managingOfferer.validationStatus
            db.session.add(venue)

        if apply:
            logger.info("script: fill venue validation status, updating venues...", extra={"venues": ids})
            db.session.commit()
        else:
            logger.info("script: fill venue validation status, rollback", extra={"venues": ids})
            db.session.rollback()


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    main(args.apply)

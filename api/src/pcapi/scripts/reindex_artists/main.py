"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=master \
  -f NAMESPACE=reindex_artists \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

import sqlalchemy as sa

from pcapi.core import search
from pcapi.core.artist import models as artists_models
from pcapi.models import db


logger = logging.getLogger(__name__)

BATCH_SIZE = 1000


def main(apply: bool) -> None:
    total = db.session.execute(sa.select(sa.func.count()).select_from(artists_models.Artist)).scalar()
    logger.info("Found %d artists to reindex", total)

    if not apply:
        logger.info("Dry run mode enabled, no indexation request sent")
        return

    offset = 0
    reindexed = 0
    while True:
        artist_ids = (
            db.session.execute(
                sa.select(artists_models.Artist.id).order_by(artists_models.Artist.id).offset(offset).limit(BATCH_SIZE)
            )
            .scalars()
            .all()
        )
        if not artist_ids:
            break
        search.reindex_artist_ids(artist_ids)
        reindexed += len(artist_ids)
        logger.info("Reindexed %d/%d artists", reindexed, total)
        offset += BATCH_SIZE

    logger.info("Finished reindexing %d artists", reindexed)


if __name__ == "__main__":
    from pcapi.app import app

    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    main(apply=args.apply)

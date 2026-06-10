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
import itertools
import logging

from pcapi.core import search
from pcapi.core.artist import models as artists_models
from pcapi.models import db


logger = logging.getLogger(__name__)

BATCH_SIZE = 1000


def main(apply: bool) -> None:
    total = db.session.query(artists_models.Artist).count()
    logger.info("Found %d artists to reindex", total)

    query = db.session.query(artists_models.Artist.id).yield_per(BATCH_SIZE)
    reindexed = 0
    for batch in itertools.batched(query, BATCH_SIZE):
        artist_ids = [artist.id for artist in batch]
        if apply:
            search.reindex_artist_ids(artist_ids)
        reindexed += len(artist_ids)
        logger.info("Reindexed (or not) %d/%d artists", reindexed, total)

    logger.info("Finished reindexing (or not)  %d artists", reindexed)


if __name__ == "__main__":
    from pcapi.app import app

    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    main(apply=args.apply)

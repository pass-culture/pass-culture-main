"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=master \
  -f NAMESPACE=reindex_all_artists \
  -f SCRIPT_ARGUMENTS="";

"""

import logging
import math

import sqlalchemy as sa

from pcapi.core import search
from pcapi.core.artist import models as artist_models
from pcapi.models import db
from pcapi.utils.chunks import get_chunks


logger = logging.getLogger(__name__)


def main() -> None:
    logger.info("Unindexing all artists")
    search.unindex_all_artists()
    artist_ids = db.session.scalars(sa.select(artist_models.Artist.id)).all()
    chunks_count = math.ceil(len(artist_ids) / 100)
    logger.info("Reindexing %s artists", len(artist_ids))
    for i, chunk in enumerate(get_chunks(artist_ids, 100), 1):
        logger.info("Reindexing chunk %s of %s", i, chunks_count)
        search.reindex_artist_ids(chunk)


if __name__ == "__main__":
    from pcapi.app import app

    app.app_context().push()

    main()

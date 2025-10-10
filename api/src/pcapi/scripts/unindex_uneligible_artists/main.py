"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/master/api/src/pcapi/scripts/unindex_uneligible_artists/main.py

"""

import argparse
import itertools
import logging
import time

from pcapi.app import app
from pcapi.core.artist.models import Artist
from pcapi.core.search import reindex_artist_ids
from pcapi.models import db


logger = logging.getLogger(__name__)


def main(batch_size: int) -> None:
    nb_artists_reindexed = 0
    nb_of_artists = db.session.query(Artist).count()
    logger.info("%d artists to reindex", nb_of_artists)

    start_time = time.time()
    artist_ids = db.session.query(Artist.id).order_by(Artist.id).yield_per(batch_size)
    for batch in itertools.batched(artist_ids, batch_size):
        artist_ids = [artist_id for (artist_id,) in batch]
        reindex_artist_ids(artist_ids)

        nb_artists_reindexed += len(batch)
        elapsed_time = time.time() - start_time
        logger.info(
            "%d/%d (%.2f%%) artists reindexed in %.2fs. Last artist indexed is %s",
            nb_artists_reindexed,
            nb_of_artists,
            nb_artists_reindexed * 100 / nb_of_artists,
            elapsed_time,
            artist_ids[-1],
        )


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-size", type=int, default=10)
    args = parser.parse_args()

    main(batch_size=args.batch_size)

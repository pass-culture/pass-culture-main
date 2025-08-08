"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/pc-36606-script-for-artist-indexation/api/src/pcapi/scripts/index_all_artists/main.py

"""

import argparse
import logging
import time
import typing

import sqlalchemy as sa

from pcapi.app import app
from pcapi.core.artist.models import Artist
from pcapi.core.search import index_artist_ids
from pcapi.models import db
from pcapi.utils.chunks import get_chunks


logger = logging.getLogger(__name__)


def index_all_artists(batch_size: int) -> None:
    start_time = time.time()
    processed_artists = 0
    number_of_artists = get_number_of_artists()
    artists = get_artist_batches(batch_size)
    for artists_batch in artists:
        index_artist_ids(artists_batch)

        processed_artists += len(artists_batch)
        ellapsed_time = time.time() - start_time
        logger.info(
            "Reindexed %d artists (%d / %d, %.2f%%). Ellapsed time: %.2fs",
            len(artists_batch),
            processed_artists,
            number_of_artists,
            processed_artists * 100 / number_of_artists,
            ellapsed_time,
        )


def get_artist_batches(batch_size: int) -> typing.Generator[list[str], None, None]:
    return get_chunks(db.session.execute(sa.select(Artist.id)).scalars().yield_per(batch_size), chunk_size=batch_size)


def get_number_of_artists() -> int:
    return db.session.execute(sa.select(sa.func.count()).select_from(Artist)).scalar()


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-size", type=int, default=1_000)

    args = parser.parse_args()

    index_all_artists(batch_size=args.batch_size)

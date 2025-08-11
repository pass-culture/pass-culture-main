"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/pc-35905-truncate-artist-tables/api/src/pcapi/scripts/truncate_artist_tables/main.py

"""

import logging

from pcapi.app import app
from pcapi.core.artist.commands import import_all_artist_aliases
from pcapi.core.artist.commands import import_all_artist_product_links
from pcapi.core.artist.commands import import_all_artists
from pcapi.models import db
from pcapi.utils.repository import transaction


logger = logging.getLogger(__name__)


def truncate_artist_tables() -> None:
    with transaction():
        db.session.execute("TRUNCATE TABLE artist_product_link")

    logger.info("ArtistProductLink table truncated")

    with transaction():
        db.session.execute("TRUNCATE TABLE artist_alias")

    logger.info("ArtistAlias table truncated")

    with transaction():
        db.session.execute("DELETE FROM artist")

    logger.info("Artist table truncated")


def import_all_artists_data() -> None:
    import_all_artists()
    import_all_artist_product_links()
    import_all_artist_aliases()


if __name__ == "__main__":
    with app.app_context():
        truncate_artist_tables()
        import_all_artists_data()
        logger.info("All artists data imported")

import argparse
import logging

from pcapi.core.artist import models as artists_models
from pcapi.flask_app import app
from pcapi.models import db


logger = logging.getLogger(__name__)


def fill_artist_is_blacklisted_field(do_update: bool) -> None:
    artists = db.session.query(artists_models.Artist).filter_by(is_blacklisted=None).yield_per(1000)
    for artist in artists:
        logger.info("Processing artist: %s", artist.name)
        artist.is_blacklisted = False

    if do_update:
        db.session.commit()
        logger.info("Artist is_blacklisted field updated successfully.")
    else:
        db.session.rollback()
        logger.info("Dry run: no changes made to the database.")


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser(description="Fill artist is_blacklisted field script")
    parser.add_argument("--not-dry", action="store_true", help="set to really process (dry-run by default)")
    args = parser.parse_args()

    fill_artist_is_blacklisted_field(do_update=args.not_dry)

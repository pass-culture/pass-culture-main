"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/pc-36613-remove-artist-jul-the-illustrator/api/src/pcapi/scripts/remove_bad_artist/main.py

"""

import argparse
import logging

import sqlalchemy as sa

from pcapi.app import app
from pcapi.core.artist.models import Artist
from pcapi.core.artist.models import ArtistProductLink
from pcapi.core.categories.subcategories import LIVRE_PAPIER
from pcapi.core.offers.models import Product
from pcapi.models import db


logger = logging.getLogger(__name__)


def main(artist_id: str, not_dry: bool) -> None:
    artist = db.session.execute(sa.select(Artist).where(Artist.id == artist_id)).one_or_none()
    if not artist:
        logger.info("Artist not found for id %s. Returning.", artist_id)

    db.session.execute(
        sa.update(Artist)
        .where(Artist.id == artist_id)
        .values(
            image="https://commons.wikimedia.org/wiki/Special:FilePath/JUL%20-%20Julien%20Mari%202018.jpg",
            description="rappeur, chanteur et auteur-compositeur-interprète français",
        )
    )
    link_ids = db.session.execute(
        sa.select(ArtistProductLink.id)
        .join(Product)
        .where(ArtistProductLink.artist_id == artist_id, Product.subcategoryId == LIVRE_PAPIER.id)
    ).scalars()
    db.session.execute(
        sa.delete(ArtistProductLink).where(ArtistProductLink.id.in_(link_ids)),
        execution_options={"synchronize_session": False},
    )


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    parser.add_argument("--artist-id", type=str)
    args = parser.parse_args()

    main(artist_id=args.artist_id, not_dry=args.not_dry)

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()

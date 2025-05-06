"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/pc-35997-script-to-delete-specific-artist/api/src/pcapi/scripts/remove_bad_artist/main.py

"""

import argparse
import logging

import sqlalchemy as sa

from pcapi.app import app
from pcapi.core import search
from pcapi.core.artist.models import Artist
from pcapi.core.artist.models import ArtistAlias
from pcapi.core.artist.models import ArtistProductLink
from pcapi.core.offers.models import Offer
from pcapi.models import db
from pcapi.repository import transaction
from pcapi.utils.chunks import get_chunks


logger = logging.getLogger(__name__)


def delete_artist_related_data(artist_id: str) -> None:
    with transaction():
        db.session.query(ArtistProductLink).filter(ArtistProductLink.artist_id == artist_id).delete()

    logger.info("Deleted related artist product links")
    with transaction():
        db.session.query(ArtistAlias).filter(ArtistAlias.artist_id == artist_id).delete()

    logger.info("Deleted related artist aliases")
    with transaction():
        db.session.query(Artist).filter(Artist.id == artist_id).delete()

    logger.info("Deleted related artists")


def reindex_related_offer_ids(product_ids: list[int], not_dry: bool) -> int:
    query = sa.select(Offer.id).where(Offer.productId.in_(product_ids))
    offer_ids = db.session.execute(query).scalars().yield_per(1000)
    total_offers_reindexed = 0
    for offer_ids_batch in get_chunks(offer_ids, chunk_size=1000):
        if not_dry:
            search.reindex_offer_ids(offer_ids_batch)

        total_offers_reindexed += len(offer_ids_batch)
    return total_offers_reindexed


def main(artist_id: str, batch_size: int, not_dry: bool) -> None:
    query = sa.select(ArtistProductLink.product_id).distinct().where(ArtistProductLink.artist_id == artist_id)
    product_ids = db.session.execute(query).scalars().all()
    logger.info("Found %d products for artist %s", len(product_ids), artist_id)

    if not_dry:
        delete_artist_related_data(artist_id)
    else:
        logger.info("Dry run: would delete artist %s related data", artist_id)

    start = 0
    total_offers_reindexed = 0
    while start < len(product_ids):
        product_ids_batch = product_ids[start : start + batch_size]
        batch_offers_reindexed = reindex_related_offer_ids(product_ids_batch, not_dry)
        logger.info(
            "Reindexed %d offers related to %d product ids (%d / %d)",
            batch_offers_reindexed,
            len(product_ids_batch),
            start + len(product_ids_batch),
            len(product_ids),
        )
        start += batch_size
        total_offers_reindexed += batch_offers_reindexed

    logger.info("Total offers reindexed: %d", total_offers_reindexed)


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    parser.add_argument("--batch-size", type=int, default=1_000)
    parser.add_argument("--artist-id", type=str, default="a2df9f4b-6445-4767-840d-f7fc7ab7344a")

    args = parser.parse_args()

    artist_id = args.artist_id
    batch_size = args.batch_size
    not_dry = args.not_dry

    main(artist_id, batch_size, not_dry=args.not_dry)

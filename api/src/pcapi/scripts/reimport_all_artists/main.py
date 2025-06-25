"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/pc-36695-reimport-all-artists-and-reindex/api/src/pcapi/scripts/reimport_all_artists/main.py

"""

import argparse
import logging
import time
from typing import Generator

import sqlalchemy as sa
from sqlalchemy import distinct
from sqlalchemy import func

from pcapi.app import app
from pcapi.core import search
from pcapi.core.artist.commands import import_all_artist_aliases
from pcapi.core.artist.commands import import_all_artist_product_links
from pcapi.core.artist.commands import import_all_artists
from pcapi.core.artist.models import ArtistProductLink
from pcapi.core.offers.models import Offer
from pcapi.models import db
from pcapi.repository import transaction
from pcapi.utils.chunks import get_chunks


logger = logging.getLogger(__name__)


def truncate_artist_tables():
    with transaction():
        db.session.execute("DELETE FROM artist_product_link")

    logger.info("ArtistProductLink table truncated")

    with transaction():
        db.session.execute("DELETE FROM artist_alias")

    logger.info("ArtistAlias table truncated")

    with transaction():
        db.session.execute("DELETE FROM artist")

    logger.info("Artist table truncated")


def import_all_artists_data():
    start_time = time.time()
    import_all_artists()
    import_time = time.time() - start_time
    logger.info("Artists imported in %.2fs", import_time)

    start_time = time.time()
    import_all_artist_product_links()
    import_time = time.time() - start_time
    logger.info("Artist product links imported in %.2fs", import_time)

    start_time = time.time()
    import_all_artist_aliases()
    import_time = time.time() - start_time
    logger.info("Artist aliases imported in %.2fs", import_time)


def _get_query_as_scalar_batches(query: sa.sql.expression.Select, batch_size: int) -> Generator[list[int], None, None]:
    return get_chunks(db.session.execute(query).scalars().yield_per(batch_size), chunk_size=batch_size)


def reindex_related_offers(product_ids: list[int], not_dry: bool) -> int:
    total_offers_reindexed = 0
    query = sa.select(Offer.id).where(Offer.productId.in_(product_ids))
    offer_ids = _get_query_as_scalar_batches(query, batch_size=1000)
    for offer_ids_batch in offer_ids:
        if not_dry:
            search.reindex_offer_ids(offer_ids_batch)

        total_offers_reindexed += len(offer_ids_batch)
    return total_offers_reindexed


def get_number_of_products() -> int:
    return db.session.execute(
        sa.select(func.count(distinct(ArtistProductLink.product_id))).select_from(ArtistProductLink)
    ).scalar()


def reindex_artist_product_offers(batch_size: int, not_dry: bool) -> None:
    start_time = time.time()
    total_offers_reindexed = 0
    processed_products = 0
    number_of_products = get_number_of_products()
    query = sa.select(ArtistProductLink.product_id).distinct().order_by(ArtistProductLink.product_id)
    product_ids = _get_query_as_scalar_batches(query, batch_size)
    for product_ids_batch in product_ids:
        batch_offers_reindexed = reindex_related_offers(product_ids_batch, not_dry)
        processed_products += len(product_ids_batch)
        total_offers_reindexed += batch_offers_reindexed
        ellapsed_time = time.time() - start_time
        logger.info(
            "Reindexed %d offers related to %d products (%d / %d, %.2f%%). Ellapsed time: %.2fs",
            batch_offers_reindexed,
            len(product_ids_batch),
            min(processed_products, number_of_products),
            number_of_products,
            min(processed_products, number_of_products) * 100 / number_of_products,
            ellapsed_time,
        )

    logger.info("Total offers reindexed: %d", total_offers_reindexed)


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    parser.add_argument("--batch-size", type=int, default=1_000)

    args = parser.parse_args()

    truncate_artist_tables()
    import_all_artists_data()
    reindex_artist_product_offers(batch_size=args.batch_size, not_dry=args.not_dry)

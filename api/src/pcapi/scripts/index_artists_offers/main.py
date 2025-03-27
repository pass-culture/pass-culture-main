"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/pc-35323-reindex-offers-for-artists/api/src/pcapi/scripts/index_artists_offers/main.py

"""

import argparse
import logging
import time

from sqlalchemy.sql.expression import func

from pcapi.app import app
from pcapi.core.artist.models import ArtistProductLink
from pcapi.core.offers.models import Offer
from pcapi.core.search import reindex_offer_ids
from pcapi.models import db
from pcapi.utils.chunks import get_chunks


logger = logging.getLogger(__name__)


def reindex_artist_related_offers(
    min_id: int, max_id: int | None, batch_size: int, indexation_batch_size: int, not_dry: bool = False
) -> None:
    max_id = max_id or db.session.query(func.max(ArtistProductLink.id)).scalar() + 1
    total = 0
    current_min_id = min_id
    start_time = time.time()
    while current_min_id < max_id:
        batch_end = min(current_min_id + batch_size, max_id)
        query = (
            db.session.query(ArtistProductLink)
            .join(Offer, ArtistProductLink.product_id == Offer.productId)
            .filter(current_min_id <= ArtistProductLink.id, ArtistProductLink.id < batch_end)
            .with_entities(Offer.id)
            .yield_per(indexation_batch_size)
        )
        batch_total = 0
        for offer_ids_chunk in get_chunks(query, chunk_size=indexation_batch_size):
            logger.info("Reindexing %d offers", len(offer_ids_chunk))
            if not_dry:
                reindex_offer_ids([offer_id for (offer_id,) in offer_ids_chunk])
            batch_total += len(offer_ids_chunk)

        total += batch_total

        logger.info(
            "Indexed %d offers linked to artist_product_links from %d to %d (%.2f%%). Ellapsed time: %.2fs. Total offers indexed: %d",
            batch_total,
            current_min_id,
            batch_end,
            (batch_end - min_id) * 100 / (max_id - min_id),
            time.time() - start_time,
            total,
        )
        current_min_id = batch_end


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    parser.add_argument("--batch-size", type=int, default=100)
    parser.add_argument("--indexation-batch-size", type=int, default=1_000)
    parser.add_argument("--min-id", type=int, default=0)
    parser.add_argument("--max-id", type=int)
    args = parser.parse_args()

    reindex_artist_related_offers(args.min_id, args.max_id, args.batch_size, args.indexation_batch_size, args.not_dry)

    logger.info("Finished")

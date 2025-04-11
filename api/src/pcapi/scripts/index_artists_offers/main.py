"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions): 

https://github.com/pass-culture/pass-culture-main/blob/pc-35323-reindex-offers-for-artists/api/src/pcapi/scripts/index_artists_offers/main.py

"""

import argparse
import logging

from sqlalchemy.sql.expression import func

from pcapi.app import app
from pcapi.core.artist.models import ArtistProductLink
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Product
from pcapi.core.search import IndexationReason
from pcapi.core.search import async_index_offer_ids
from pcapi.models import db

logger = logging.getLogger(__name__)


def main(batch_size: int = 10_000, not_dry: bool = False) -> None:
    max_id = db.session.query(func.max(ArtistProductLink.id)).scalar()
    total = 0
    min_id = 0
    while min_id <= max_id:
        query = (
            db.session.query(ArtistProductLink)
            .join(Product, ArtistProductLink.product_id == Product.id)
            .join(Product.offers)
            .filter(min_id <= ArtistProductLink.id, ArtistProductLink.id < min_id + batch_size)
            .with_entities(Offer.id)
        )
        offer_ids = [offer_id for offer_id, in query]
        if not_dry:
            async_index_offer_ids(offer_ids, IndexationReason.OFFER_MANUAL_REINDEXATION)

        total += len(offer_ids)
        logger.info("Added to queue %d", total)

        min_id += batch_size


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    parser.add_argument("--batch-size", type=int, default=10_000)
    args = parser.parse_args()

    main(batch_size=args.batch_size, not_dry=args.not_dry)

    logger.info("Finished")

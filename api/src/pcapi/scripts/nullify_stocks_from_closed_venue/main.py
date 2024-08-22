"""Nullify a venue's stocks' idAtProviders

This script should only be used when two venue have swapped their SIRET
number resulting in some inconsistencies during the stocks sync.

Setting the old venue's stocks' idAtProviders to null should avoid some
mismatch (and therefore some errors).

Use carefully.
"""

import logging
import sys

from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.models import db
from pcapi.utils.chunks import get_chunks


logger = logging.getLogger(__name__)


def run(venue_id: int) -> None:
    query = Stock.query.join(Offer).filter(Offer.venueId == venue_id).with_entities(Stock.id)
    stock_ids = [row[0] for row in query.yield_per(5_000)]

    logger.info("Starting stocks update for venue #%s, total: %d", venue_id, len(stock_ids))

    for idx, ids in enumerate(get_chunks(stock_ids, 1_000), start=1):
        update_mapping = [
            {"id": stock_id, "idAtProviders": None, "isActive": False, "lastProviderId": None}
            for stock_id in ids
        ]

        db.session.bulk_update_mappings(Stock, update_mapping)
        db.session.commit()

        logger.info("[venue #%d][%d] %d stocks updated", venue_id, idx, len(ids))
        logger.info("[venue #%d][%d] stocks update details: %s", venue_id, idx, ids)

    logger.info("venue #%d update... done.", venue_id)


if __name__ == "__main__":
    try:
        run(int(sys.argv[1]))
    except (TypeError, ValueError) as exc:
        logger.info("Failed to start update script, because: %s", str(exc))
        sys.exit(-1)

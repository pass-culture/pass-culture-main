import argparse
import logging

from pcapi.app import app
from pcapi.core import search


logger = logging.getLogger(__name__)


VENUE_IDS = [13010, 17440]


def reindex_offers(venue_ids: list[int]) -> None:
    search.async_index_offers_of_venue_ids(
        venue_ids,
        reason=search.IndexationReason.OFFER_REINDEXATION,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--venue-ids", nargs="+", type=int, required=True)
    args = parser.parse_args()
    with app.app_context():
        reindex_offers(args.venue_ids)

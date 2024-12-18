import logging

from pcapi.app import app
from pcapi.core import search


logger = logging.getLogger(__name__)


VENUE_IDS = [9731]


def reindex_offers() -> None:
    search.async_index_offers_of_venue_ids(
        VENUE_IDS,
        reason=search.IndexationReason.OFFER_REINDEXATION,
    )


with app.app_context():
    reindex_offers()

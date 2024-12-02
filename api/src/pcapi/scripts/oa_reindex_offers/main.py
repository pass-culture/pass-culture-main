import logging

from pcapi.app import app
from pcapi.core import search


logger = logging.getLogger(__name__)


VENUE_ID = 121454


def reindex_offers() -> None:
    search.async_index_offers_of_venue_ids(
        [VENUE_ID],
        reason=search.IndexationReason.OFFER_REINDEXATION,
    )


with app.app_context():
    reindex_offers()

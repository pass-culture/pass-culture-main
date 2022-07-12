import logging

from pcapi.core import search
from pcapi.core.offerers import api as offerers_api
from pcapi.repository import offer_queries
from pcapi.utils.chunks import get_chunks


logger = logging.getLogger(__name__)


def batch_indexing_offers_in_algolia_from_database(
    ending_page: int = None, limit: int = 10000, starting_page: int = 0
) -> None:
    page = starting_page
    while True:
        if ending_page and ending_page == page:
            break

        offer_ids = offer_queries.get_paginated_active_offer_ids(limit=limit, page=page)
        if not offer_ids:
            break
        search.reindex_offer_ids(offer_ids)
        logger.info("[ALGOLIA] Processed %d offers from page %d", len(offer_ids), page)
        page += 1


def batch_indexing_venues_in_algolia_from_database(algolia_batch_size: int, max_venues: int | None) -> None:
    venues = offerers_api.get_eligible_for_search_venues(max_venues)
    for page, venue_chunk in enumerate(get_chunks(venues, algolia_batch_size), start=1):  # type: ignore [var-annotated]
        venue_ids = [venue.id for venue in venue_chunk]
        search.reindex_venue_ids(venue_ids)
        logger.info("[ALGOLIA] Processed %d venues from page %d", len(venue_ids), page)

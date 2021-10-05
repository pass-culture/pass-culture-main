import logging

from pcapi import settings
from pcapi.core import search
from pcapi.models import Offer
from pcapi.models import Venue


logger = logging.getLogger(__name__)


def create_industrial_search_indexed_objects() -> None:
    if settings.ALGOLIA_TRIGGER_INDEXATION:
        logger.info("create_industrial_algolia_objects")
        offer_ids = [offer_id for offer_id, in Offer.query.with_entities(Offer.id)]
        search.unindex_all_offers()
        search.reindex_offer_ids(offer_ids)

        venue_ids = [venue_id for venue_id, in Venue.query.with_entities(Venue.id)]
        search.unindex_all_venues()
        search.reindex_venue_ids(venue_ids)

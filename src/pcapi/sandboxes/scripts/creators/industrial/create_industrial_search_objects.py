import logging

from sqlalchemy import orm

from pcapi import settings
from pcapi.core import search
from pcapi.models import Offer
from pcapi.models import Venue


logger = logging.getLogger(__name__)


def create_industrial_search_indexed_objects() -> None:
    if settings.ALGOLIA_TRIGGER_INDEXATION:
        logger.info("create_industrial_algolia_objects")
        offer_ids = Offer.query.options(orm.load_only(Offer.id)).all()
        search.unindex_all_offers()
        search.reindex_offer_ids(offer_ids)

        venue_ids = Venue.query.options(orm.load_only(Venue.id)).all()
        search.unindex_all_venues()
        search.reindex_venue_ids(venue_ids)

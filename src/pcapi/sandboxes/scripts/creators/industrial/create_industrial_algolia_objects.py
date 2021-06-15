import logging

from pcapi import settings
from pcapi.core import search
from pcapi.models import Offer


logger = logging.getLogger(__name__)


def create_industrial_algolia_indexed_objects() -> None:
    if settings.ALGOLIA_TRIGGER_INDEXATION:
        logger.info("create_industrial_algolia_objects")
        offer_ids = Offer.query.with_entities(Offer.id).all()
        search.unindex_all_offers()
        search.reindex_offer_ids(offer_ids)

import logging

from pcapi import settings
from pcapi.core import search
from pcapi.core.educational import models as educational_models
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.models import Offer


logger = logging.getLogger(__name__)


def create_data_search_indexed_objects() -> None:
    if settings.ALGOLIA_TRIGGER_INDEXATION:
        logger.info("create_data_algolia_objects")
        offer_ids = [offer_id for offer_id, in Offer.query.with_entities(Offer.id)]
        search.unindex_all_offers()
        search.reindex_offer_ids(offer_ids)

        venue_ids = [venue_id for venue_id, in Venue.query.with_entities(Venue.id)]
        search.unindex_all_venues()
        search.reindex_venue_ids(venue_ids)

        search.unindex_all_collective_offer_templates()

        collective_offer_template_ids = [
            collective_offer_template_id
            for collective_offer_template_id, in educational_models.CollectiveOfferTemplate.query.with_entities(
                educational_models.CollectiveOfferTemplate.id
            )
        ]
        search.async_index_collective_offer_template_ids(
            collective_offer_template_ids,
            reason=search.IndexationReason.OFFER_CREATION,
        )

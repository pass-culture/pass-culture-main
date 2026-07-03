import logging

import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.models import Offer
from pcapi.models.offer_mixin import OfferStatus
from pcapi.sandboxes.scripts.utils.helpers import log_func_duration


logger = logging.getLogger(__name__)


@log_func_duration
def create_industrial_headline_offers(offers_by_name: dict[str, Offer]) -> None:
    logger.info("create_industrial_headline_offers")

    headlined_venue_ids: set[int] = set()

    headline_offers_by_name = {}
    for offer_name, offer in offers_by_name.items():
        if offer.status == OfferStatus.ACTIVE and offer.venue.id not in headlined_venue_ids and offer.hasActiveImage:
            headline_offers_by_name[offer_name] = offers_factories.HeadlineOfferFactory.create(
                offer=offer, venue=offer.venue, without_mediation=True
            )
            headlined_venue_ids.add(offer.venue.id)

    logger.info("created %d headline offers", len(headline_offers_by_name))

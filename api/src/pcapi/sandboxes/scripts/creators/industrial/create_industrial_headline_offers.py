import logging

import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.models import Offer
from pcapi.models.offer_mixin import OfferStatus
from pcapi.sandboxes.scripts.utils.helpers import log_func_duration


logger = logging.getLogger(__name__)

HEADLINE_OFFER_LIMIT_PER_OFFERER = 1


@log_func_duration
def create_industrial_headline_offers(offers_by_name: dict[str, Offer]) -> None:
    logger.info("create_industrial_headline_offers")

    headline_offer_limit_per_offerer = {}
    offerers = {offer.venue.managingOfferer.name: offer.venue.managingOfferer for offer in offers_by_name.values()}
    for offerer_name in offerers.keys():
        headline_offer_limit_per_offerer[offerer_name] = HEADLINE_OFFER_LIMIT_PER_OFFERER

    headline_offers_by_name = {}
    for offer_name, offer in offers_by_name.items():
        offerer_name = offer.venue.managingOfferer.name
        if (
            headline_offer_limit_per_offerer[offerer_name]
            and offer.status == OfferStatus.ACTIVE
            and not offer.venue.has_headline_offer
        ):
            headline_offers_by_name[offer_name] = offers_factories.HeadlineOfferFactory.create(
                offer=offer, venue=offer.venue, without_mediation=True
            )

            headline_offer_limit_per_offerer[offerer_name] = (
                headline_offer_limit_per_offerer[offerer_name] - 1
                if headline_offer_limit_per_offerer[offerer_name] > 0
                else headline_offer_limit_per_offerer[offerer_name]
            )

    logger.info("created %d headline offers", len(headline_offers_by_name))

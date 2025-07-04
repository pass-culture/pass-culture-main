import logging

import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.factories as offers_factories
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.sandboxes.scripts.utils.helpers import log_func_duration


logger = logging.getLogger(__name__)


@log_func_duration
def create_industrial_draft_offers(offerers_by_name: dict[str, offerers_models.Offerer]) -> None:
    logger.info("create_industrial_individual_draft_offers")
    index = 0
    for offerer in offerers_by_name.values():
        venues = [venue for venue in offerer.managedVenues if not venue.isVirtual]
        if not venues:
            continue
        venue = venues[0]

        offers_factories.OfferFactory.create(
            venue=venue, name="Mon offre brouillon", validation=OfferValidationStatus.DRAFT
        )

        draft_with_stocks = offers_factories.OfferFactory.create(
            venue=venue, name="Mon offre brouillon avec stock", validation=OfferValidationStatus.DRAFT
        )
        offers_factories.StockFactory.create(offer=draft_with_stocks)
        index += 2
    db.session.commit()
    logger.info("created %d draft offers", index)

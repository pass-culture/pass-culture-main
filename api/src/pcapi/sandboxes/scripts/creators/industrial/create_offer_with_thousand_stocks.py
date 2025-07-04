import datetime
import logging

from pcapi.core.categories import subcategories
from pcapi.core.offerers.factories import VenueFactory
from pcapi.core.offerers.models import Offerer
from pcapi.core.offers.factories import EventOfferFactory
from pcapi.core.offers.factories import EventStockFactory
from pcapi.core.offers.factories import PriceCategoryFactory
from pcapi.sandboxes.scripts.utils.helpers import log_func_duration


logger = logging.getLogger(__name__)


@log_func_duration
def create_offer_with_thousand_stocks(offerer: Offerer) -> None:
    venue = VenueFactory.create(
        name="Lieu avec offre pleine de stocks",
        managingOfferer=offerer,
    )

    offer_event = EventOfferFactory.create(
        name="1000 stocks",
        venue=venue,
        subcategoryId=subcategories.SEANCE_CINE.id,
    )
    price_category = PriceCategoryFactory.create(offer=offer_event)
    for i in range(0, 1000):
        EventStockFactory.create(
            offer=offer_event,
            quantity=1,
            beginningDatetime=datetime.datetime.utcnow().replace(second=0, microsecond=0)
            - datetime.timedelta(days=100)
            + datetime.timedelta(days=i),
            priceCategory=price_category,
        )

    logger.info("create_offer with 1000 stocks")

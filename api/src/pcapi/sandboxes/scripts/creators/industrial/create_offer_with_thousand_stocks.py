import datetime
import logging

from pcapi.core.categories import subcategories
from pcapi.core.offerers.factories import UserOffererFactory
from pcapi.core.offerers.factories import VenueFactory
from pcapi.core.offerers.factories import VirtualVenueFactory
from pcapi.core.offers.factories import EventOfferFactory
from pcapi.core.offers.factories import EventStockFactory
from pcapi.core.offers.factories import PriceCategoryFactory


logger = logging.getLogger(__name__)


def create_offer_with_thousand_stocks() -> None:
    user_offerer = UserOffererFactory(offerer__name="Offerer avec offre pleine de stocks")
    venue = VenueFactory(
        name="Lieu avec offre pleine de stocks",
        managingOfferer=user_offerer.offerer,
    )
    # offerers have always a virtual venue so we have to create one to match reality
    VirtualVenueFactory(name="Lieu virtuel avec offre pleine de stocks", managingOfferer=user_offerer.offerer)
    offer_event = EventOfferFactory(
        name="1000 stocks",
        venue=venue,
        subcategoryId=subcategories.SEANCE_CINE.id,
    )
    price_category = PriceCategoryFactory(offer=offer_event)
    for i in range(0, 1000):
        EventStockFactory(
            offer=offer_event,
            quantity=1,
            beginningDatetime=datetime.datetime.utcnow().replace(second=0, microsecond=0)
            - datetime.timedelta(days=100)
            + datetime.timedelta(days=i),
            priceCategory=price_category,
        )

    logger.info("create_offer with 1000 stocks")

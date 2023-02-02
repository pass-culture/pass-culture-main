import logging

from pcapi.core.categories import subcategories
from pcapi.core.offerers.factories import UserOffererFactory
from pcapi.core.offerers.factories import VenueFactory
from pcapi.core.offerers.factories import VirtualVenueFactory
from pcapi.core.offers.factories import EventOfferFactory
from pcapi.core.offers.factories import EventStockFactory
from pcapi.core.offers.factories import PriceCategoryFactory


logger = logging.getLogger(__name__)


def create_offers_with_price_categories() -> None:
    user_offerer = UserOffererFactory(offerer__name="Offerer avec tarif")
    venue = VenueFactory(
        name="Lieu avec tarif",
        managingOfferer=user_offerer.offerer,
    )
    # offerers have always a virtual venue so we have to create one to match reality
    VirtualVenueFactory(name="Lieu virtuel avec tarif", managingOfferer=user_offerer.offerer)

    offer_event = EventOfferFactory(
        name="Offre à tarifs",
        venue=venue,
        subcategoryId=subcategories.SEANCE_CINE.id,
    )
    price_gold = PriceCategoryFactory(
        offer=offer_event, priceCategoryLabel__label="OR", price=66.6, priceCategoryLabel__venue=venue
    )
    price_silver = PriceCategoryFactory(
        offer=offer_event, priceCategoryLabel__label="ARGENT", price=42, priceCategoryLabel__venue=venue
    )
    price_bronze = PriceCategoryFactory(
        offer=offer_event, priceCategoryLabel__label="BRONZE", price=13, priceCategoryLabel__venue=venue
    )
    price_free = PriceCategoryFactory(
        offer=offer_event, priceCategoryLabel__label="GRATUIT", price=0, priceCategoryLabel__venue=venue
    )

    EventStockFactory(offer=offer_event, priceCategory=price_gold)
    EventStockFactory(offer=offer_event, priceCategory=price_silver)
    EventStockFactory(offer=offer_event, priceCategory=price_bronze)
    EventStockFactory(offer=offer_event, priceCategory=price_free)
    logger.info("create_offers with price categories")

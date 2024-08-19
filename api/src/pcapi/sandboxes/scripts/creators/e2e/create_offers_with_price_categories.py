import logging

from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.offerers.factories import VenueFactory
from pcapi.core.offerers.models import Offerer
from pcapi.core.offers.factories import EventOfferFactory
from pcapi.core.offers.factories import EventStockFactory
from pcapi.core.offers.factories import PriceCategoryFactory


logger = logging.getLogger(__name__)


def create_offers_with_price_categories(offerer: Offerer) -> None:
    venue = VenueFactory(
        name="Lieu avec tarif",
        managingOfferer=offerer,
    )

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

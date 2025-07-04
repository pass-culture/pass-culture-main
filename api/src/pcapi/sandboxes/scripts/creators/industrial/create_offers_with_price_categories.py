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
def create_offers_with_price_categories(offerer: Offerer) -> None:
    venue = VenueFactory.create(
        name="Lieu avec tarif",
        managingOfferer=offerer,
    )

    offer_event = EventOfferFactory.create(
        name="Offre à tarifs",
        venue=venue,
        subcategoryId=subcategories.SEANCE_CINE.id,
    )
    price_gold = PriceCategoryFactory.create(
        offer=offer_event, priceCategoryLabel__label="OR", price=66.6, priceCategoryLabel__venue=venue
    )
    price_silver = PriceCategoryFactory.create(
        offer=offer_event, priceCategoryLabel__label="ARGENT", price=42, priceCategoryLabel__venue=venue
    )
    price_bronze = PriceCategoryFactory.create(
        offer=offer_event, priceCategoryLabel__label="BRONZE", price=13, priceCategoryLabel__venue=venue
    )
    price_free = PriceCategoryFactory.create(
        offer=offer_event, priceCategoryLabel__label="GRATUIT", price=0, priceCategoryLabel__venue=venue
    )

    EventStockFactory.create(offer=offer_event, priceCategory=price_gold, price=price_gold.price)
    EventStockFactory.create(offer=offer_event, priceCategory=price_silver, price=price_silver.price)
    EventStockFactory.create(offer=offer_event, priceCategory=price_bronze, price=price_bronze.price)
    EventStockFactory.create(offer=offer_event, priceCategory=price_free, price=price_free.price)
    logger.info("create_offers with price categories")

import datetime
import logging
import random

from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.offers import factories as offers_factories


logger = logging.getLogger(__name__)


def _create_future_offer(isActive: bool, publicationDate: datetime.datetime) -> None:
    offer = offers_factories.OfferFactory(isActive=isActive, subcategoryId=subcategories.FESTIVAL_MUSIQUE.id)
    offers_factories.EventStockFactory(
        offer=offer, beginningDatetime=publicationDate + datetime.timedelta(days=random.randint(0, 10)), price=2.4
    )

    offers_factories.FutureOfferFactory(offer=offer, publicationDate=publicationDate)


def create_future_offers() -> None:
    # Create future Offer not active
    publication_date = datetime.datetime.utcnow() + datetime.timedelta(days=30)
    _create_future_offer(isActive=False, publicationDate=publication_date)
    # Create future Offer activated
    _create_future_offer(isActive=True, publicationDate=publication_date)

    # Create future Offer in the past
    publication_date = datetime.datetime.utcnow() + datetime.timedelta(days=-30)
    _create_future_offer(isActive=True, publicationDate=publication_date)
    # Create future Offer in the past not activated ...
    _create_future_offer(isActive=False, publicationDate=publication_date)

    logger.info("create_future_offers")

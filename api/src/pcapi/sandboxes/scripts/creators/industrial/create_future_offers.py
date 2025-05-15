import datetime
import logging

import pcapi.core.offers.factories as offer_factories
from pcapi.core.categories import subcategories
from pcapi.core.categories.models import Subcategory


logger = logging.getLogger(__name__)


def _create_future_offer_factory(
    is_active: bool,
    publication_date: datetime.datetime,
    subcategory: Subcategory = subcategories.FESTIVAL_MUSIQUE,
    name: str = "Offre Coming Soon",
    description: str | None = None,
) -> None:
    offer = offer_factories.OfferFactory.create(
        isActive=is_active, isDuo=True, subcategoryId=subcategory.id, name=name, description=description
    )
    offer_factories.EventStockFactory.create(
        offer=offer, beginningDatetime=publication_date - datetime.timedelta(days=1), price=12.25
    )

    offer_factories.FutureOfferFactory.create(offer=offer, publicationDate=publication_date)


def create_future_offers() -> None:
    # Create future Offers not active, i.e. proper coming soon offers
    for i in range(5):
        publication_date = datetime.datetime.utcnow() + datetime.timedelta(days=(i + 1) * 5)
        _create_future_offer_factory(
            is_active=False,
            publication_date=publication_date,
            name=f"Offre Coming Soon - planifiée n°{i + 1}",
            description="Une offre coming soon pour tester la planification",
        )

    # Create future Offer activated, i.e offer manually activated before planned publication_date
    _create_future_offer_factory(
        is_active=True,
        publication_date=publication_date,
        subcategory=subcategories.EVENEMENT_CINE,
        name="Offre Coming Soon - activée manuellement",
        description="Une offre coming soon pour tester l'activation manuelle",
    )

    # Create future Offer in the past, i.e. regular offer
    publication_date = datetime.datetime.utcnow() + datetime.timedelta(days=-30)
    _create_future_offer_factory(
        is_active=True,
        publication_date=publication_date,
        subcategory=subcategories.CONCERT,
        name="Offre Coming Soon - activée automatiquement",
        description="Une offre coming soon pour tester l'activation automatique",
    )

    # Create future Offer in the past not activated, i.e. stale offer
    _create_future_offer_factory(
        is_active=False,
        publication_date=publication_date,
        subcategory=subcategories.FESTIVAL_CINE,
        name="Offre Coming Soon - non activée",
    )

    logger.info("create_future_offers")

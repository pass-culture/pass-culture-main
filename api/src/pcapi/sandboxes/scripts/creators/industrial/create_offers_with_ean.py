import logging

from pcapi.core.categories import subcategories
from pcapi.core.criteria import factories as criteria_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.models.offer_mixin import OfferValidationStatus


logger = logging.getLogger(__name__)


def create_offers_with_ean() -> None:
    ean_criteria = criteria_factories.CriterionFactory(name="Livre avec EAN")
    odd_criteria = criteria_factories.CriterionFactory(name="Librairie impaire")
    even_criteria = criteria_factories.CriterionFactory(name="Librairie paire")

    products = [
        offers_factories.ThingProductFactory(
            name=f"Livre {i} avec EAN",
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            extraData={"ean": f"9780000000{i:03}"},
        )
        for i in range(1, 5)
    ]

    user_offerer = offerers_factories.UserOffererFactory(
        user__firstName="Super", user__lastName="Libraire", offerer__name="Réseau de librairies"
    )

    for i in range(1, 11):
        venue = offerers_factories.VenueFactory(name=f"Librairie {i}", managingOfferer=user_offerer.offerer)

        for j, product in enumerate(products):
            offer_thing = offers_factories.ThingOfferFactory(
                name=product.name,
                venue=venue,
                product=product,
                subcategoryId=product.subcategoryId,
                extraData=product.extraData,
                isActive=(i % 3 > 0),
                validation=OfferValidationStatus.PENDING if i % 6 == 0 else OfferValidationStatus.APPROVED,
                criteria=[ean_criteria, even_criteria] if i % 2 == 0 else [ean_criteria, odd_criteria],
            )
            offers_factories.ThingStockFactory(offer=offer_thing, quantity=10, price=5 + j)

    logger.info("create_offers_with_ean")

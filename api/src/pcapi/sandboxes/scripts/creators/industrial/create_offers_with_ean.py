import logging

from pcapi.core.categories import subcategories
from pcapi.core.criteria import factories as criteria_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.providers import factories as providers_factories
from pcapi.models.offer_mixin import OfferValidationStatus


logger = logging.getLogger(__name__)


def create_offers_with_ean() -> None:
    ean_criteria = criteria_factories.CriterionFactory.create(name="Livre avec EAN")
    odd_criteria = criteria_factories.CriterionFactory.create(name="Librairie impaire")
    even_criteria = criteria_factories.CriterionFactory.create(name="Librairie paire")
    products = [offers_models.Product.query.filter(offers_models.Product.name == "multiple thumbs").one()]
    provider = providers_factories.PublicApiProviderFactory.create(name="BookProvider")
    for i in range(1, 5):
        ean = f"9780000000{i:03}"
        products.append(
            offers_factories.ThingProductFactory.create(
                name=f"Livre {i} avec EAN",
                idAtProviders=ean,
                subcategoryId=subcategories.LIVRE_PAPIER.id,
                lastProviderId=provider.id,
                ean=f"9780000000{i:03}",
            )
        )

    user_offerer = offerers_factories.UserOffererFactory.create(
        user__firstName="Super",
        user__lastName="Libraire",
        offerer__name="Réseau de librairies",
        user__email="retention_structures@example.com",
    )

    for i in range(1, 11):
        venue = offerers_factories.VenueFactory.create(
            name=f"Librairie {i}",
            managingOfferer=user_offerer.offerer,
            venueTypeCode=offerers_models.VenueTypeCode.BOOKSTORE,
        )

        for j, product in enumerate(products):
            offer_thing = offers_factories.ThingOfferFactory.create(
                name=product.name,
                venue=venue,
                product=product,
                subcategoryId=product.subcategoryId,
                extraData=product.extraData,
                isActive=(i % 3 > 0),
                validation=OfferValidationStatus.PENDING if i % 6 == 0 else OfferValidationStatus.APPROVED,
                criteria=[ean_criteria, even_criteria] if i % 2 == 0 else [ean_criteria, odd_criteria],
            )
            offers_factories.ThingStockFactory.create(offer=offer_thing, quantity=10, price=5 + j)

    logger.info("create_offers_with_ean")

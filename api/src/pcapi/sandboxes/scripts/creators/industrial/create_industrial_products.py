import logging
import random

import pcapi.core.offers.factories as offers_factories
from pcapi.core.providers import factories as providers_factories
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.sandboxes.scripts.utils.helpers import log_func_duration


logger = logging.getLogger(__name__)


@log_func_duration
def create_industrial_products() -> None:
    logger.info("create_industrial_products")

    ean = "9791041410736"
    book_provider = providers_factories.PublicApiProviderFactory.create(name="BookProvider")
    product = offers_factories.ProductFactory.create(id=1000, ean=ean, lastProvider=book_provider)
    for _ in range(10):
        offers_factories.OfferFactory.create_batch(
            random.randint(150, 300), product=product, validation=random.choice(list(OfferValidationStatus))
        )
        offers_factories.OfferFactory.create_batch(
            random.randint(50, 100), ean=ean, validation=random.choice(list(OfferValidationStatus))
        )

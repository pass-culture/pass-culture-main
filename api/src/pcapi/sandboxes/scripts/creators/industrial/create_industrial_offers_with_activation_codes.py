from datetime import datetime
import logging

from pcapi.core.offerers.factories import VirtualVenueFactory
from pcapi.core.offers.factories import StockWithActivationCodesFactory


logger = logging.getLogger(__name__)


def create_industrial_offers_with_activation_codes():  # type: ignore [no-untyped-def]
    logger.info("create_industrial_offers_with_activation_codes")

    venue = VirtualVenueFactory()

    StockWithActivationCodesFactory.create_batch(
        5, offer__venue=venue, activationCodes__expirationDate=datetime(2030, 2, 5, 0, 0, 0)
    )

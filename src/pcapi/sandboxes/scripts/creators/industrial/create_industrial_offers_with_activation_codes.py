from datetime import datetime
import logging

from pcapi.core.offers.factories import StockWithActivationCodesFactory
from pcapi.core.offers.factories import VirtualVenueFactory
from pcapi.core.users.models import User
from pcapi.model_creators.generic_creators import create_booking
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.model_creators.specific_creators import create_stock_with_thing_offer
from pcapi.models import ThingType
from pcapi.repository import repository


logger = logging.getLogger(__name__)


def create_industrial_offers_with_activation_codes():
    logger.info("create_industrial_offers_with_activation_codes")

    venue = VirtualVenueFactory()

    stocks = StockWithActivationCodesFactory.create_batch(
        5, offer__venue=venue, activationCodes__expirationDate=datetime(2030, 2, 5, 0, 0, 0)
    )

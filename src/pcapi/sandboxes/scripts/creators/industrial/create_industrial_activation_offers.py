import logging

from pcapi.core.categories import subcategories
from pcapi.core.users.models import User
from pcapi.model_creators.generic_creators import create_booking
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.model_creators.specific_creators import create_stock_with_thing_offer
from pcapi.repository import repository


logger = logging.getLogger(__name__)


def create_industrial_activation_offers():
    logger.info("create_industrial_activation_offers")

    activated_user = User.query.filter_by(isBeneficiary=True).first()
    offerer = create_offerer()
    venue = create_venue(offerer, is_virtual=True, siret=None)
    offer = create_offer_with_thing_product(venue, thing_subcategory_id=subcategories.ACTIVATION_THING.id)
    stock = create_stock_with_thing_offer(offerer, venue, offer=offer, price=0, quantity=10000)

    booking = create_booking(user=activated_user, stock=stock, offerer=offerer, venue=venue, token="ACTIVA")

    repository.save(booking)
    logger.info("created 1 activation offer")

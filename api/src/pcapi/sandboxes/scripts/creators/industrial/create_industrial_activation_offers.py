from decimal import Decimal
import logging

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.categories import subcategories
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.users.models import User
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.model_creators.specific_creators import create_stock_with_thing_offer


logger = logging.getLogger(__name__)


def create_industrial_activation_offers() -> None:
    logger.info("create_industrial_activation_offers")

    activated_user = User.query.filter_by(has_beneficiary_role=True).first()
    offerer = offerers_factories.OffererFactory()
    venue = offerers_factories.VirtualVenueFactory(managingOfferer=offerer)
    offer = create_offer_with_thing_product(venue, thing_subcategory_id=subcategories.ACTIVATION_THING.id)
    stock = create_stock_with_thing_offer(offerer, venue, offer=offer, price=Decimal(0), quantity=10000)

    bookings_factories.IndividualBookingFactory(
        individualBooking__user=activated_user,
        user=activated_user,
        stock=stock,
        token="ACTIVA",
    )

    logger.info("created 1 activation offer")

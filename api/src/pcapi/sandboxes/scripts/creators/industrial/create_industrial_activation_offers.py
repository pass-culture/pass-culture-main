from decimal import Decimal
import logging

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.categories import subcategories
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.models as users_models
from pcapi.core.users.models import User


logger = logging.getLogger(__name__)


def create_industrial_activation_offers() -> None:
    logger.info("create_industrial_activation_offers")

    activated_user = User.query.filter_by(has_beneficiary_role=True).first()
    offerer = offerers_factories.OffererFactory()
    venue = offerers_factories.VirtualVenueFactory(managingOfferer=offerer)

    _create_activation_item_offer(activated_user, offerer, venue, subcategories.ACTIVATION_THING.id, "ACTTHG")
    _create_activation_item_offer(activated_user, offerer, venue, subcategories.ACTIVATION_EVENT.id, "ACTEVT")

    logger.info("created 2 activation offers")


def _create_activation_item_offer(
    user: users_models.User,
    offerer: offerers_models.Offerer,
    venue: offerers_models.Venue,
    subcategory: str,
    token: str,
) -> None:
    offer = offers_factories.OfferFactory(
        venue=venue,
        product__subcategoryId=subcategory,
    )
    stock = offers_factories.StockFactory(
        offer=offer,
        price=Decimal(0),
        quantity=10000,
    )

    bookings_factories.BookingFactory(
        user=user,
        stock=stock,
        token=token,
    )

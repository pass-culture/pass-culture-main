import datetime
import logging

from pcapi.core.bookings.factories import IndividualBookingFactory
from pcapi.core.categories import subcategories
from pcapi.core.offerers.factories import UserOffererFactory
from pcapi.core.offerers.factories import VenueFactory
from pcapi.core.offerers.factories import VirtualVenueFactory
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.factories import EventOfferFactory
from pcapi.core.offers.factories import EventStockFactory
from pcapi.core.offers.factories import ThingOfferFactory
from pcapi.core.offers.factories import ThingStockFactory
from pcapi.core.users.factories import BeneficiaryGrant18Factory
from pcapi.core.users.models import User


logger = logging.getLogger(__name__)


def create_specific_offers() -> None:
    user_offerer = UserOffererFactory(offerer__name="Offerer avec offres spécifiques")
    venue = VenueFactory(
        name="Lieu avec offres spécifiques",
        managingOfferer=user_offerer.offerer,
    )
    # offerers have always a virtual venue so we have to create one to match reality
    VirtualVenueFactory(
        name="Lieu virtuel avec offres spécifiques", managingOfferer=user_offerer.offerer, isVirtual=True
    )
    user_bene = BeneficiaryGrant18Factory(email="jeune-has-specific-offers-external-bookings@example.com")

    create_offers_fully_booked(user_bene, venue)
    create_offers_expired(venue)
    logger.info("create_offers")


def create_offers_fully_booked(user_bene: User, venue: Venue) -> None:
    offer_event = EventOfferFactory(
        name="Séance ciné complétement réservée",
        venue=venue,
        subcategoryId=subcategories.SEANCE_CINE.id,
    )
    stock_event = EventStockFactory(offer=offer_event, quantity=1)
    IndividualBookingFactory(quantity=1, stock=stock_event, user=user_bene, individualBooking__user=user_bene)

    offer_thing = ThingOfferFactory(
        name=" Livre complétement réservé",
        venue=venue,
        subcategoryId=subcategories.LIVRE_PAPIER.id,
    )
    stock_thing = ThingStockFactory(offer=offer_thing, quantity=1)
    IndividualBookingFactory(quantity=1, stock=stock_thing, user=user_bene, individualBooking__user=user_bene)

    offer_with_past_stock = EventOfferFactory(
        name="Séance ciné avec 1 stock passé complétement réservé",
        venue=venue,
        subcategoryId=subcategories.SEANCE_CINE.id,
    )
    EventStockFactory(offer=offer_with_past_stock)
    stock_past = EventStockFactory(
        offer=offer_with_past_stock,
        beginningDatetime=datetime.datetime.utcnow().replace(second=0, microsecond=0) - datetime.timedelta(days=5),
        quantity=1,
    )
    IndividualBookingFactory(quantity=1, stock=stock_past, user=user_bene, individualBooking__user=user_bene)
    logger.info("create_offers_fully_booked")


def create_offers_expired(venue: Venue) -> None:
    offer_event = EventOfferFactory(
        name="Séance ciné expirée",
        venue=venue,
        subcategoryId=subcategories.SEANCE_CINE.id,
    )
    EventStockFactory(
        offer=offer_event,
        quantity=1,
        beginningDatetime=datetime.datetime.utcnow().replace(second=0, microsecond=0) - datetime.timedelta(days=5),
    )

    logger.info("create_offers_expired")

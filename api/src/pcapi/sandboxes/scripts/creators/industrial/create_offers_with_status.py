import datetime
import logging

from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.categories import subcategories
from pcapi.core.offerers.factories import VenueFactory
from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.factories import EventOfferFactory
from pcapi.core.offers.factories import EventStockFactory
from pcapi.core.offers.factories import PriceCategoryFactory
from pcapi.core.offers.factories import ThingOfferFactory
from pcapi.core.offers.factories import ThingStockFactory
from pcapi.core.users.factories import BeneficiaryGrant18Factory
from pcapi.core.users.models import User
from pcapi.models.offer_mixin import OfferValidationStatus


logger = logging.getLogger(__name__)


def create_offers_with_status(offerer: Offerer) -> None:
    venue = VenueFactory(
        name="Lieu avec offres spécifiques",
        managingOfferer=offerer,
    )
    user_bene = BeneficiaryGrant18Factory(email="jeune-has-specific-offers-external-bookings@example.com")

    create_offers_fully_booked(user_bene, venue)
    create_offers_expired(venue)
    create_offers_pending_and_refused(venue)
    logger.info("create_offers with status")


def create_offers_fully_booked(user_bene: User, venue: Venue) -> None:
    for i in range(9):
        offer_event = EventOfferFactory(
            name=f"Ciné complétement réservé {i}",
            venue=venue,
            subcategoryId=subcategories.SEANCE_CINE.id,
        )
        stock_event = EventStockFactory(offer=offer_event, quantity=1)
        BookingFactory(quantity=1, stock=stock_event, user=user_bene)

        offer_thing = ThingOfferFactory(
            name=f"Livre complétement réservé {i}",
            venue=venue,
            subcategoryId=subcategories.LIVRE_PAPIER.id,
        )
        stock_thing = ThingStockFactory(offer=offer_thing, quantity=1)
        BookingFactory(quantity=1, stock=stock_thing, user=user_bene)

        offer_with_past_stock = EventOfferFactory(
            name=f"Ciné avec 1 stock passé complétement réservé {i}",
            venue=venue,
            subcategoryId=subcategories.SEANCE_CINE.id,
        )
        price_category = PriceCategoryFactory(offer=offer_with_past_stock)
        EventStockFactory(offer=offer_with_past_stock, priceCategory=price_category)
        stock_past = EventStockFactory(
            offer=offer_with_past_stock,
            beginningDatetime=datetime.datetime.utcnow().replace(second=0, microsecond=0) - datetime.timedelta(days=5),
            quantity=1,
            priceCategory=price_category,
        )
        BookingFactory(quantity=1, stock=stock_past, user=user_bene)

    logger.info("create_offers_fully_booked")


def create_offers_expired(venue: Venue) -> None:
    for i in range(0, 10):
        offer_event = EventOfferFactory(
            name=f"Ciné expiré {i}",
            venue=venue,
            subcategoryId=subcategories.SEANCE_CINE.id,
        )
        EventStockFactory(
            offer=offer_event,
            quantity=1,
            beginningDatetime=datetime.datetime.utcnow().replace(second=0, microsecond=0) - datetime.timedelta(days=5),
        )
    logger.info("create_offers_expired")


def create_offers_pending_and_refused(venue: Venue) -> None:
    for i in range(0, 10):
        offer_event = EventOfferFactory(
            name=f"Ciné en attente de validation {i}",
            venue=venue,
            subcategoryId=subcategories.SEANCE_CINE.id,
            validation=OfferValidationStatus.PENDING,
        )
        EventStockFactory(
            offer=offer_event,
        )

        offer_event = EventOfferFactory(
            name=f"Ciné rejeté {i}",
            venue=venue,
            subcategoryId=subcategories.SEANCE_CINE.id,
            validation=OfferValidationStatus.REJECTED,
        )
        EventStockFactory(offer=offer_event)

    logger.info("create_offers_pending_refused")

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
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.sandboxes.scripts.utils.helpers import log_func_duration


logger = logging.getLogger(__name__)


@log_func_duration
def create_offers_with_status(offerer: Offerer) -> None:
    venue = VenueFactory.create(
        name="Lieu avec offres spécifiques",
        managingOfferer=offerer,
    )
    user_bene = BeneficiaryGrant18Factory.create(email="jeune-has-specific-offers-external-bookings@example.com")
    user_bene.deposit.amount = 300
    db.session.add(user_bene)
    db.session.commit()

    create_offers_fully_booked(user_bene, venue)
    create_offers_expired(venue)
    create_offers_pending_and_refused(venue)
    logger.info("create_offers with status")


def create_offers_fully_booked(user_bene: User, venue: Venue) -> None:
    for i in range(9):
        offer_event = EventOfferFactory.create(
            name=f"Ciné complétement réservé {i}",
            venue=venue,
            subcategoryId=subcategories.SEANCE_CINE.id,
        )
        stock_event = EventStockFactory.create(offer=offer_event, quantity=1)
        BookingFactory.create(quantity=1, stock=stock_event, user=user_bene)

        offer_thing = ThingOfferFactory.create(
            name=f"Livre complétement réservé {i}",
            venue=venue,
            subcategoryId=subcategories.LIVRE_PAPIER.id,
        )
        stock_thing = ThingStockFactory.create(offer=offer_thing, quantity=1)
        BookingFactory.create(quantity=1, stock=stock_thing, user=user_bene)

        offer_with_past_stock = EventOfferFactory.create(
            name=f"Ciné avec 1 stock passé complétement réservé {i}",
            venue=venue,
            subcategoryId=subcategories.SEANCE_CINE.id,
        )
        price_category = PriceCategoryFactory.create(offer=offer_with_past_stock)
        EventStockFactory.create(offer=offer_with_past_stock, priceCategory=price_category)
        stock_past = EventStockFactory.create(
            offer=offer_with_past_stock,
            beginningDatetime=datetime.datetime.utcnow().replace(second=0, microsecond=0) - datetime.timedelta(days=5),
            quantity=1,
            priceCategory=price_category,
        )
        BookingFactory.create(quantity=1, stock=stock_past, user=user_bene)

    logger.info("create_offers_fully_booked")


def create_offers_expired(venue: Venue) -> None:
    for i in range(0, 10):
        offer_event = EventOfferFactory.create(
            name=f"Ciné expiré {i}",
            venue=venue,
            subcategoryId=subcategories.SEANCE_CINE.id,
        )
        EventStockFactory.create(
            offer=offer_event,
            quantity=1,
            beginningDatetime=datetime.datetime.utcnow().replace(second=0, microsecond=0) - datetime.timedelta(days=5),
        )
    logger.info("create_offers_expired")


def create_offers_pending_and_refused(venue: Venue) -> None:
    for i in range(0, 10):
        offer_event = EventOfferFactory.create(
            name=f"Ciné en attente de validation {i}",
            venue=venue,
            subcategoryId=subcategories.SEANCE_CINE.id,
            validation=OfferValidationStatus.PENDING,
        )
        EventStockFactory.create(
            offer=offer_event,
        )

        offer_event = EventOfferFactory.create(
            name=f"Ciné rejeté {i}",
            venue=venue,
            subcategoryId=subcategories.SEANCE_CINE.id,
            validation=OfferValidationStatus.REJECTED,
        )
        EventStockFactory.create(offer=offer_event)

    logger.info("create_offers_pending_refused")

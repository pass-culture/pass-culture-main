import logging

from pcapi.core.booking_providers.factories import ExternalBookingFactory
from pcapi.core.booking_providers.factories import VenueBookingProviderFactory
from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.categories import subcategories
from pcapi.core.offerers.factories import UserOffererFactory
from pcapi.core.offerers.factories import VenueFactory
from pcapi.core.offers.factories import EventOfferFactory
from pcapi.core.offers.factories import EventStockFactory
from pcapi.core.users.factories import BeneficiaryGrant18Factory


logger = logging.getLogger(__name__)


def create_offerer_with_booking_provider() -> None:
    logger.info("create_offerer_with_booking_provider")

    user_offerer = UserOffererFactory(user__email="pro-with-venue-booking-provider@example.com")
    venue = VenueFactory(name="Cinéma synchro avec booking provider", managingOfferer=user_offerer.offerer)
    offer_solo = EventOfferFactory(name="Séance ciné solo", venue=venue, subcategoryId=subcategories.SEANCE_CINE.id)
    stock_solo = EventStockFactory(offer=offer_solo)
    offer_duo = EventOfferFactory(name="Séance ciné duo", venue=venue, subcategoryId=subcategories.SEANCE_CINE.id)
    stock_duo = EventStockFactory(offer=offer_duo)

    VenueBookingProviderFactory(venue=venue)

    user_bene = BeneficiaryGrant18Factory(email="jeune-has-external-bookings@example.com")

    booking_solo = BookingFactory(quantity=1, stock=stock_solo, user=user_bene)
    ExternalBookingFactory(booking=booking_solo)
    booking_duo = BookingFactory(quantity=2, stock=stock_duo, user=user_bene)
    ExternalBookingFactory(booking=booking_duo, seat="A_1")
    ExternalBookingFactory(booking=booking_duo, seat="A_2")
    logger.info("created 3 externalBookings")

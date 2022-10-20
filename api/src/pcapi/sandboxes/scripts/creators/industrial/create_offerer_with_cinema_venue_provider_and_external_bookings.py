import logging

from pcapi.core.bookings.factories import IndividualBookingFactory
from pcapi.core.categories import subcategories
from pcapi.core.external_bookings.factories import ExternalBookingFactory
from pcapi.core.offerers.factories import VenueFactory
from pcapi.core.offers.factories import EventOfferFactory
from pcapi.core.offers.factories import EventStockFactory
import pcapi.core.providers.factories as providers_factories
from pcapi.core.providers.repository import get_provider_by_local_class
from pcapi.core.users.factories import BeneficiaryGrant18Factory


logger = logging.getLogger(__name__)


def create_offerer_with_cinema_venue_provider_and_external_bookings() -> None:
    logger.info("create_offerer_with_cinema_venue_provider_and_external_bookings")

    cds_provider = get_provider_by_local_class("CDSStocks")
    venue = VenueFactory(
        name="Cinéma synchro avec ciné office", managingOfferer__name="Structure du lieu synchro Ciné Office"
    )
    providers_factories.AllocineTheaterFactory(siret=venue.siret)
    offer_solo = EventOfferFactory(
        name="Séance ciné solo", venue=venue, subcategoryId=subcategories.SEANCE_CINE.id, lastProviderId=cds_provider.id
    )
    stock_solo = EventStockFactory(offer=offer_solo)
    offer_duo = EventOfferFactory(
        name="Séance ciné duo", venue=venue, subcategoryId=subcategories.SEANCE_CINE.id, lastProviderId=cds_provider.id
    )
    stock_duo = EventStockFactory(offer=offer_duo)

    cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(
        venue=venue, provider=cds_provider, idAtProvider="cdsdemorc1"
    )
    providers_factories.CDSCinemaDetailsFactory(cinemaProviderPivot=cinema_provider_pivot, accountId="cdsdemorc1")
    providers_factories.VenueProviderFactory(venue=venue, provider=cds_provider, venueIdAtOfferProvider="cdsdemorc1")

    user_bene = BeneficiaryGrant18Factory(email="jeune-has-external-bookings@example.com")

    booking_solo = IndividualBookingFactory(
        quantity=1, stock=stock_solo, user=user_bene, individualBooking__user=user_bene
    )
    ExternalBookingFactory(booking=booking_solo)
    booking_duo = IndividualBookingFactory(
        quantity=2, stock=stock_duo, user=user_bene, individualBooking__user=user_bene
    )
    ExternalBookingFactory(booking=booking_duo, seat="A_1")
    ExternalBookingFactory(booking=booking_duo, seat="A_2")
    logger.info("created 3 externalBookings")

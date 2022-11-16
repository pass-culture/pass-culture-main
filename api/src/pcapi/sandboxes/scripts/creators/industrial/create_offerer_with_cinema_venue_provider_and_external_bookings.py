import logging

from pcapi.core.bookings.factories import IndividualBookingFactory
from pcapi.core.categories import subcategories
from pcapi.core.external_bookings.factories import ExternalBookingFactory
from pcapi.core.offerers.factories import VenueFactory
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.factories import EventOfferFactory
from pcapi.core.offers.factories import EventStockFactory
import pcapi.core.providers.factories as providers_factories
from pcapi.core.providers.models import Provider
from pcapi.core.providers.repository import get_provider_by_local_class
from pcapi.core.users.factories import BeneficiaryGrant18Factory


logger = logging.getLogger(__name__)


def create_industrial_cinema_external_bookings() -> None:
    logger.info("create_industrial_cinema_external_bookings")
    create_offerer_with_cds_venue_provider_and_external_bookings()
    create_offerer_with_boost_venue_provider_and_external_bookings()


def _create_cine_offers(provider_name: str, provider: Provider) -> Venue:
    venue = VenueFactory(name=f"Cinéma - {provider_name}", managingOfferer__name=f"Structure du cinéma {provider_name}")
    offer_solo = EventOfferFactory(
        name=f"Séance ciné solo ({provider_name})",
        venue=venue,
        subcategoryId=subcategories.SEANCE_CINE.id,
        lastProvider=provider,
    )
    stock_solo = EventStockFactory(offer=offer_solo)
    offer_duo = EventOfferFactory(
        name=f"Séance ciné duo ({provider_name})",
        venue=venue,
        subcategoryId=subcategories.SEANCE_CINE.id,
        lastProvider=provider,
    )
    stock_duo = EventStockFactory(offer=offer_duo)
    user_bene = BeneficiaryGrant18Factory(email=f"jeune-has-{provider_name}-external-bookings@example.com")
    booking_solo = IndividualBookingFactory(
        quantity=1, stock=stock_solo, user=user_bene, individualBooking__user=user_bene
    )
    ExternalBookingFactory(booking=booking_solo)
    booking_duo = IndividualBookingFactory(
        quantity=2, stock=stock_duo, user=user_bene, individualBooking__user=user_bene
    )
    ExternalBookingFactory(booking=booking_duo, seat="A_1")
    ExternalBookingFactory(booking=booking_duo, seat="A_2")
    return venue


def create_offerer_with_cds_venue_provider_and_external_bookings() -> None:
    logger.info("create_offerer_with_cds_venue_provider_and_external_bookings")
    cds_provider = get_provider_by_local_class("CDSStocks")
    provider_name = "CDS"
    venue = _create_cine_offers(provider_name, cds_provider)
    cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(
        venue=venue, provider=cds_provider, idAtProvider="cdsdemorc1"
    )
    providers_factories.CDSCinemaDetailsFactory(cinemaProviderPivot=cinema_provider_pivot, accountId="cdsdemorc1")
    providers_factories.VenueProviderFactory(venue=venue, provider=cds_provider, venueIdAtOfferProvider="cdsdemorc1")
    logger.info("created 3 ExternalBookings for Ciné Office-synced offers")


def create_offerer_with_boost_venue_provider_and_external_bookings() -> None:
    logger.info("create_offerer_with_boost_venue_provider_and_external_bookings")
    boost_provider = get_provider_by_local_class("BoostStocks")
    provider_name = "Boost"
    venue = _create_cine_offers(provider_name, boost_provider)
    cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(
        venue=venue, provider=boost_provider, idAtProvider="passculture"
    )
    providers_factories.BoostCinemaDetailsFactory(cinemaProviderPivot=cinema_provider_pivot)
    providers_factories.VenueProviderFactory(venue=venue, provider=boost_provider)
    logger.info("created 3 ExternalBookings for Boost-synced offers")

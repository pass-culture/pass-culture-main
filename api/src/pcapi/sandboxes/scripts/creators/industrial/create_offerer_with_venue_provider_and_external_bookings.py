import datetime
import logging

import factory

from pcapi.core.bookings.factories import IndividualBookingFactory
from pcapi.core.categories import subcategories
from pcapi.core.external_bookings.factories import ExternalBookingFactory
from pcapi.core.offerers.factories import UserOffererFactory
from pcapi.core.offerers.factories import VenueFactory
from pcapi.core.offerers.factories import VirtualVenueFactory
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.factories import CinemaStockProviderFactory
from pcapi.core.offers.factories import EventOfferFactory
from pcapi.core.offers.factories import ThingStockFactory
import pcapi.core.providers.factories as providers_factories
from pcapi.core.providers.models import Provider
from pcapi.core.providers.repository import get_provider_by_local_class
from pcapi.core.users.factories import BeneficiaryGrant18Factory


logger = logging.getLogger(__name__)


def create_industrial_provider_external_bookings() -> None:
    logger.info("create_industrial_cinema_external_bookings")
    create_offerer_with_cds_venue_provider_and_external_bookings()
    create_offerer_with_boost_venue_provider_and_external_bookings()
    create_offerer_with_allocine_venue_provider_and_external_bookings()
    logger.info("create_industrial_titelive_external_bookings")
    create_offerer_with_titelive_venue_provider_and_external_bookings()


def _create_offers(provider_name: str, provider: Provider, provider_type: str = None) -> Venue:
    if provider_type != "book":
        cinema_user_offerer = UserOffererFactory(offerer__name=f"Structure du cinéma {provider_name}")
        venue = VenueFactory(
            name=f"Cinéma - {provider_name}",
            managingOfferer=cinema_user_offerer.offerer,
            lastProviderId=provider.id,
            idAtProviders=factory.Sequence("idAtProviders{}".format),
        )
        # offerers have always a virtual venue so we have to create one to match reality
        VirtualVenueFactory(
            name=f"Cinéma - {provider_name} Lieu Virtuel", managingOfferer=cinema_user_offerer.offerer, isVirtual=True
        )
    else:
        book_user_offerer = UserOffererFactory(offerer__name=f"Structure du Livre {provider_name}")
        venue = VenueFactory(
            name=f"Livre - {provider_name}",
            managingOfferer=book_user_offerer.offerer,
            lastProviderId=provider.id,
            idAtProviders=factory.Sequence("idAtProviders{}".format),
        )
        # offerers have always a virtual venue so we have to create one to match reality
        VirtualVenueFactory(
            name=f"Livre - {provider_name} Lieu Virtuel", managingOfferer=book_user_offerer.offerer, isVirtual=True
        )

    user_bene = BeneficiaryGrant18Factory(email=f"jeune-has-{provider_name}-external-bookings@example.com")
    if provider_type != "book":
        offer_solo = EventOfferFactory(
            name=f"Séance ciné solo ({provider_name})",
            venue=venue,
            subcategoryId=subcategories.SEANCE_CINE.id,
            lastProvider=provider,
        )
        stock_solo = CinemaStockProviderFactory(offer=offer_solo)
        offer_duo = EventOfferFactory(
            name=f"Séance ciné duo ({provider_name})",
            venue=venue,
            subcategoryId=subcategories.SEANCE_CINE.id,
            lastProvider=provider,
        )
        stock_duo = CinemaStockProviderFactory(offer=offer_duo)
        booking_duo = IndividualBookingFactory(
            quantity=2, stock=stock_duo, user=user_bene, individualBooking__user=user_bene
        )
        ExternalBookingFactory(booking=booking_duo, seat="A_1")
        ExternalBookingFactory(booking=booking_duo, seat="A_2")
    else:
        offer_solo = EventOfferFactory(
            name=f"Livre ({provider_name})",
            venue=venue,
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            lastProvider=provider,
        )
        stock_solo = ThingStockFactory(offer=offer_solo)

    # for allocine we want to be able to test that we can update stock with also a past stock
    if provider_type == "allocine":
        offer_with_past_stock = EventOfferFactory(
            name=f"Séance ciné with past stock ({provider_name})",
            venue=venue,
            subcategoryId=subcategories.SEANCE_CINE.id,
            lastProvider=provider,
        )
        CinemaStockProviderFactory(offer=offer_with_past_stock)
        CinemaStockProviderFactory(
            offer=offer_with_past_stock,
            beginningDatetime=datetime.datetime.utcnow().replace(second=0, microsecond=0) - datetime.timedelta(days=5),
        )
    booking_solo = IndividualBookingFactory(
        quantity=1, stock=stock_solo, user=user_bene, individualBooking__user=user_bene
    )
    ExternalBookingFactory(booking=booking_solo)
    return venue


def create_offerer_with_cds_venue_provider_and_external_bookings() -> None:
    logger.info("create_offerer_with_cds_venue_provider_and_external_bookings")
    cds_provider = get_provider_by_local_class("CDSStocks")
    provider_name = "CDS"
    venue = _create_offers(provider_name, cds_provider)
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
    venue = _create_offers(provider_name, boost_provider)
    cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(
        venue=venue, provider=boost_provider, idAtProvider="passculture"
    )
    providers_factories.BoostCinemaDetailsFactory(cinemaProviderPivot=cinema_provider_pivot)
    providers_factories.VenueProviderFactory(venue=venue, provider=boost_provider)
    logger.info("created 3 ExternalBookings for Boost-synced offers")


def create_offerer_with_allocine_venue_provider_and_external_bookings() -> None:
    logger.info("create_offerer_with_allocine_venue_provider_and_external_bookings")
    allocine_provider = get_provider_by_local_class("AllocineStocks")
    venue = _create_offers(allocine_provider.name, allocine_provider, provider_type="allocine")
    allocine_venue_provider = providers_factories.AllocineVenueProviderFactory(venue=venue, provider=allocine_provider)
    providers_factories.AllocineVenueProviderPriceRuleFactory(allocineVenueProvider=allocine_venue_provider)
    providers_factories.AllocinePivotFactory(venue=venue, internalId=allocine_venue_provider.internalId)
    logger.info("created 3 ExternalBookings for Boost-synced offers")


def create_offerer_with_titelive_venue_provider_and_external_bookings() -> None:
    logger.info("create_offerer_with_boost_venue_provider_and_external_bookings")
    provider = get_provider_by_local_class("TiteLiveThings")
    provider_name = "TiteLiveThings"
    venue = _create_offers(provider_name, provider, provider_type="book")
    providers_factories.VenueProviderFactory(venue=venue, provider=provider)
    logger.info("created 3 ExternalBookings for TiteLive-synced offers")

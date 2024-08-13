import datetime
import logging
import random

from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.external_bookings.factories import BookingFactory
from pcapi.core.external_bookings.factories import ExternalBookingFactory
from pcapi.core.offerers.factories import UserOffererFactory
from pcapi.core.offerers.factories import VenueFactory
from pcapi.core.offerers.factories import VirtualVenueFactory
from pcapi.core.offerers.models import Venue
from pcapi.core.offerers.models import VenueTypeCode
from pcapi.core.offers.factories import CinemaStockProviderFactory
from pcapi.core.offers.factories import EventOfferFactory
from pcapi.core.offers.factories import ThingOfferFactory
from pcapi.core.offers.factories import ThingStockFactory
import pcapi.core.providers.factories as providers_factories
from pcapi.core.providers.models import Provider
from pcapi.core.providers.repository import get_provider_by_local_class
from pcapi.core.users.factories import BeneficiaryGrant18Factory


logger = logging.getLogger(__name__)


def _cinema_stock_features(provider: Provider) -> list[str]:
    features = [random.choice(["VF", "VO"])]
    match provider.name:
        case "CDSStocks" | "BoostStocks":
            if random.choice([True, False]):
                features.append("3D")
        case "CGRStocks":
            features.append(random.choice(["3D", "ICE"]))
    return features


def create_industrial_provider_external_bookings() -> None:
    logger.info("create_industrial_provider_external_bookings")
    create_offerers_with_cinema_venue_providers_and_external_bookings()
    create_offerer_with_allocine_venue_provider_and_external_bookings()
    create_offerer_with_titelive_venue_provider_and_external_bookings()


def _create_offers(provider: Provider) -> Venue:
    provider_name = provider.name
    if provider_name != "TiteLiveThings":
        cinema_user_offerer = UserOffererFactory(
            offerer__name=f"Structure du cinéma {provider_name}", user__email="api@example.com"
        )
        venue = VenueFactory(
            name=f"Cinéma - {provider_name}",
            managingOfferer=cinema_user_offerer.offerer,
            venueTypeCode=VenueTypeCode.MOVIE,
        )
        # offerers have always a virtual venue so we have to create one to match reality
        VirtualVenueFactory(name=f"Cinéma - {provider_name} Lieu Virtuel", managingOfferer=cinema_user_offerer.offerer)
    else:
        book_user_offerer = UserOffererFactory(offerer__name=f"Structure du Livre {provider_name}")
        venue = VenueFactory(
            name=f"Livre - {provider_name}",
            managingOfferer=book_user_offerer.offerer,
            venueTypeCode=VenueTypeCode.BOOKSTORE,
        )
        # offerers have always a virtual venue so we have to create one to match reality
        VirtualVenueFactory(name=f"Livre - {provider_name} Lieu Virtuel", managingOfferer=book_user_offerer.offerer)

    user_bene = BeneficiaryGrant18Factory(email=f"jeune-has-{provider_name}-external-bookings@example.com")
    for i in range(9):
        if provider.isCinemaProvider or provider.isAllocine:
            offer_solo = EventOfferFactory(
                name=f"Ciné solo ({provider_name}) {i}",
                venue=venue,
                subcategoryId=subcategories.SEANCE_CINE.id,
                lastProvider=provider,
            )
            stock_solo = CinemaStockProviderFactory(offer=offer_solo)
            booking_solo = BookingFactory(quantity=1, stock=stock_solo, user=user_bene)
            if provider.isCinemaProvider:
                stock_solo.features = _cinema_stock_features(provider)
                ExternalBookingFactory(booking=booking_solo, seat="A_1")
            offer_duo = EventOfferFactory(
                name=f"Ciné duo ({provider_name}) {i}",
                venue=venue,
                subcategoryId=subcategories.SEANCE_CINE.id,
                lastProvider=provider,
            )
            stock_duo = CinemaStockProviderFactory(offer=offer_duo)
            booking_duo = BookingFactory(quantity=2, stock=stock_duo, user=user_bene)
            if provider.isCinemaProvider:
                stock_duo.features = _cinema_stock_features(provider)
                ExternalBookingFactory(booking=booking_duo, seat="A_1")
                ExternalBookingFactory(booking=booking_duo, seat="A_2")
        # for allocine we want to be able to test that we can update stock with also a past stock
        if provider.isAllocine:
            offer_with_past_stock = EventOfferFactory(
                name=f"Ciné avec stock passé ({provider_name}) {i}",
                venue=venue,
                subcategoryId=subcategories.SEANCE_CINE.id,
                lastProvider=provider,
            )
            CinemaStockProviderFactory(offer=offer_with_past_stock)
            CinemaStockProviderFactory(
                offer=offer_with_past_stock,
                beginningDatetime=datetime.datetime.utcnow().replace(second=0, microsecond=0)
                - datetime.timedelta(days=5),
            )
        if provider_name == "TiteLiveThings":
            offer_solo = ThingOfferFactory(
                name=f"Livre ({provider_name}) {i}",
                venue=venue,
                subcategoryId=subcategories.LIVRE_PAPIER.id,
                lastProvider=provider,
            )
            stock_solo = ThingStockFactory(offer=offer_solo)
            BookingFactory(quantity=1, stock=stock_solo, user=user_bene)
    return venue


def create_offerers_with_cinema_venue_providers_and_external_bookings() -> None:
    for local_class, cinema_details_factory in (
        ("CDSStocks", providers_factories.CDSCinemaDetailsFactory),
        ("BoostStocks", providers_factories.BoostCinemaDetailsFactory),
        ("CGRStocks", providers_factories.CGRCinemaDetailsFactory),
        ("EMSStocks", providers_factories.EMSCinemaDetailsFactory),
    ):
        cinema_provider = get_provider_by_local_class(local_class)
        venue = _create_offers(cinema_provider)
        cinema_id_at_provider = f"{local_class}Provider"
        cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(
            venue=venue, provider=cinema_provider, idAtProvider=cinema_id_at_provider
        )

        cinema_details_factory(cinemaProviderPivot=cinema_provider_pivot)
        providers_factories.VenueProviderFactory(
            venue=venue, provider=cinema_provider, venueIdAtOfferProvider=cinema_id_at_provider, isActive=False
        )
        logger.info("created 3 ExternalBookings for synced offers (%s)", local_class)


def create_offerer_with_allocine_venue_provider_and_external_bookings() -> None:
    logger.info("create_offerer_with_allocine_venue_provider")
    allocine_provider = get_provider_by_local_class("AllocineStocks")
    venue = _create_offers(allocine_provider)
    allocine_venue_provider = providers_factories.AllocineVenueProviderFactory(venue=venue, provider=allocine_provider)
    providers_factories.AllocinePivotFactory(venue=venue, internalId=allocine_venue_provider.internalId)
    logger.info("created Offerer with allocine venueProvider")


def create_offerer_with_titelive_venue_provider_and_external_bookings() -> None:
    logger.info("create_offerer_with_titelive_venue_provider")
    provider = get_provider_by_local_class("TiteLiveThings")
    venue = _create_offers(provider)
    providers_factories.VenueProviderFactory(venue=venue, provider=provider)
    logger.info("created Offerer with TiteLive-synced offers")

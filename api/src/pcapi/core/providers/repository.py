from operator import or_
from typing import Optional

from flask_sqlalchemy import BaseQuery

from pcapi.core.offerers.models import Venue
from pcapi.core.providers.constants import CINEMA_PROVIDER_NAMES
from pcapi.core.providers.models import AllocineTheater
from pcapi.core.providers.models import CinemaProviderPivot
from pcapi.core.providers.models import Provider
from pcapi.core.providers.models import VenueProvider


def get_venue_provider_by_id(venue_provider_id: int) -> VenueProvider:
    return VenueProvider.query.filter_by(id=venue_provider_id).one()


def get_venue_provider_list(venue_id: int) -> list[VenueProvider]:
    return VenueProvider.query.filter_by(venueId=venue_id).all()


def get_active_venue_providers_by_provider(provider_id: int) -> list[VenueProvider]:
    return VenueProvider.query.filter_by(providerId=provider_id, isActive=True).all()


def get_venue_provider_by_venue_and_provider_ids(venue_id: int, provider_id: int) -> VenueProvider:
    return VenueProvider.query.filter_by(venueId=venue_id, providerId=provider_id).one()


def get_provider_enabled_for_pro_by_id(provider_id: int) -> Optional[Provider]:
    return Provider.query.filter_by(id=provider_id, isActive=True, enabledForPro=True).one_or_none()


def get_provider_by_local_class(local_class: str) -> Provider:
    return Provider.query.filter_by(localClass=local_class).one_or_none()


def get_active_providers_query() -> BaseQuery:
    return Provider.query.filter_by(isActive=True).order_by(Provider.name)


def get_enabled_providers_for_pro() -> list[Provider]:
    return get_enabled_providers_for_pro_query().all()


def get_enabled_providers_for_pro_query() -> BaseQuery:
    return Provider.query.filter_by(isActive=True).filter_by(enabledForPro=True).order_by(Provider.name)


def get_providers_enabled_for_pro_excluding_specific_providers(providers_to_exclude: list[str]) -> list[Provider]:
    return (
        Provider.query.filter_by(isActive=True)
        .filter_by(enabledForPro=True)
        .filter(or_(Provider.localClass.notin_(providers_to_exclude), Provider.localClass.is_(None)))
        .order_by(Provider.name)
        .all()
    )


def get_allocine_theater(venue: Venue) -> AllocineTheater:
    return AllocineTheater.query.filter_by(siret=venue.siret).one_or_none()


def is_venue_known_by_allocine(venue: Venue) -> bool:
    allocine_theater = get_allocine_theater(venue)
    return allocine_theater is not None


def get_cinema_provider_pivot_for_venue(venue: Venue) -> Optional[CinemaProviderPivot]:
    return CinemaProviderPivot.query.filter_by(venue=venue).one_or_none()


def get_providers_to_exclude(venue: Venue) -> list[str]:
    from pcapi.local_providers import AllocineStocks

    cinema_provider_pivot = get_cinema_provider_pivot_for_venue(venue)
    cinema_provider_class = cinema_provider_pivot.provider.localClass if cinema_provider_pivot else ""
    providers_to_exclude = [
        provider_class for provider_class in CINEMA_PROVIDER_NAMES if provider_class != cinema_provider_class
    ]

    has_allocine_pivot = is_venue_known_by_allocine(venue)
    if not has_allocine_pivot:
        providers_to_exclude.append(AllocineStocks.__name__)

    return providers_to_exclude

from dataclasses import dataclass
from operator import or_
from typing import cast

from flask_sqlalchemy import BaseQuery

from pcapi.core.offerers.models import Venue
from pcapi.core.providers.constants import CINEMA_PROVIDER_NAMES
import pcapi.core.providers.exceptions as providers_exceptions
from pcapi.core.providers.models import AllocinePivot
from pcapi.core.providers.models import AllocineTheater
from pcapi.core.providers.models import CDSCinemaDetails
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


def get_provider_enabled_for_pro_by_id(provider_id: int) -> Provider | None:
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


def get_allocine_theater(venue: Venue) -> AllocineTheater | None:
    return AllocineTheater.query.filter_by(siret=venue.siret).one_or_none()


def get_allocine_pivot(venue: Venue) -> AllocinePivot | None:
    return AllocinePivot.query.filter_by(venue=venue).one_or_none()


def get_cinema_provider_pivot_for_venue(venue: Venue) -> CinemaProviderPivot | None:
    return CinemaProviderPivot.query.filter_by(venue=venue).one_or_none()


def get_providers_to_exclude(venue: Venue) -> list[str]:
    from pcapi.local_providers import AllocineStocks

    cinema_provider_pivot = get_cinema_provider_pivot_for_venue(venue)
    cinema_provider_class = cinema_provider_pivot.provider.localClass if cinema_provider_pivot else ""
    providers_to_exclude = [
        provider_class for provider_class in CINEMA_PROVIDER_NAMES if provider_class != cinema_provider_class
    ]

    try:
        AllocineVenue(venue)
    except providers_exceptions.UnknownVenueToAlloCine:
        providers_to_exclude.append(AllocineStocks.__name__)

    return providers_to_exclude


def get_cds_cinema_details(cinema_id: str) -> CDSCinemaDetails:
    cinema_details = (
        CDSCinemaDetails.query.join(CinemaProviderPivot).filter(CinemaProviderPivot.idAtProvider == cinema_id).one()
    )
    return cinema_details


# Each venue is known to allocine by its siret (AllocineTheater) or by its id (AllocinePivot).
# This class is used to handle this logic when a venue wants to sync with Allocine.
@dataclass
class AllocineVenue:
    def __init__(self, venue: Venue):
        self.venue = venue
        self.allocine_pivot = get_allocine_pivot(venue)
        if not self.has_pivot():
            self.allocine_theater = get_allocine_theater(venue)

        if not self.has_pivot() and not self.has_theater():
            raise providers_exceptions.UnknownVenueToAlloCine()

    allocine_pivot: AllocinePivot | None
    allocine_theater: AllocineTheater | None

    def has_pivot(self) -> bool:
        return self.allocine_pivot is not None

    def has_theater(self) -> bool:
        return self.allocine_theater is not None

    def get_pivot(self) -> AllocinePivot:
        if not self.has_pivot():
            raise providers_exceptions.NoAllocinePivot
        return cast(AllocinePivot, self.allocine_pivot)

    def get_theater(self) -> AllocineTheater:
        if self.has_pivot():
            self.allocine_theater = get_allocine_theater(self.venue)
        if not self.has_theater():
            raise providers_exceptions.NoAllocineTheater
        return cast(AllocineTheater, self.allocine_theater)

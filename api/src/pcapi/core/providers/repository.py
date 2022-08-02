from dataclasses import dataclass
import datetime
from typing import cast

from flask_sqlalchemy import BaseQuery

from pcapi.core.offerers.models import Venue

from . import constants
from . import exceptions
from . import models


def get_venue_provider_by_id(venue_provider_id: int) -> models.VenueProvider:
    return models.VenueProvider.query.filter_by(id=venue_provider_id).one()


def get_venue_provider_list(venue_id: int) -> list[models.VenueProvider]:
    return models.VenueProvider.query.filter_by(venueId=venue_id).all()


def get_active_venue_providers_by_provider(provider_id: int) -> list[models.VenueProvider]:
    return models.VenueProvider.query.filter_by(providerId=provider_id, isActive=True).all()


def get_venue_provider_by_venue_and_provider_ids(venue_id: int, provider_id: int) -> models.VenueProvider:
    return models.VenueProvider.query.filter_by(venueId=venue_id, providerId=provider_id).one()


def get_provider_enabled_for_pro_by_id(provider_id: int) -> models.Provider | None:
    return models.Provider.query.filter_by(id=provider_id, isActive=True, enabledForPro=True).one_or_none()


def get_provider_by_local_class(local_class: str) -> models.Provider:
    return models.Provider.query.filter_by(localClass=local_class).one_or_none()


def get_active_providers_query() -> BaseQuery:
    return models.Provider.query.filter_by(isActive=True).order_by(models.Provider.name)


def get_enabled_providers_for_pro() -> list[models.Provider]:
    return get_enabled_providers_for_pro_query().all()


def get_enabled_providers_for_pro_query() -> BaseQuery:
    return models.Provider.query.filter_by(isActive=True).filter_by(enabledForPro=True).order_by(models.Provider.name)


def get_providers_enabled_for_pro_excluding_specific_providers(
    providers_to_exclude: list[str],
) -> list[models.Provider]:
    return (
        models.Provider.query.filter_by(isActive=True, enabledForPro=True)
        .filter(models.Provider.localClass.notin_(providers_to_exclude) | models.Provider.localClass.is_(None))
        .order_by(models.Provider.name)
        .all()
    )


def get_allocine_theater(venue: Venue) -> models.AllocineTheater | None:
    return models.AllocineTheater.query.filter_by(siret=venue.siret).one_or_none()


def get_allocine_pivot(venue: Venue) -> models.AllocinePivot | None:
    return models.AllocinePivot.query.filter_by(venue=venue).one_or_none()


def get_cinema_provider_pivot_for_venue(venue: Venue) -> models.CinemaProviderPivot | None:
    return models.CinemaProviderPivot.query.filter_by(venue=venue).one_or_none()


def get_providers_to_exclude(venue: Venue) -> list[str]:
    from pcapi.local_providers import AllocineStocks

    cinema_provider_pivot = get_cinema_provider_pivot_for_venue(venue)
    cinema_provider_class = cinema_provider_pivot.provider.localClass if cinema_provider_pivot else ""
    providers_to_exclude = [
        provider_class for provider_class in constants.CINEMA_PROVIDER_NAMES if provider_class != cinema_provider_class
    ]

    try:
        AllocineVenue(venue)
    except exceptions.UnknownVenueToAlloCine:
        providers_to_exclude.append(AllocineStocks.__name__)

    return providers_to_exclude


def get_cds_cinema_details(cinema_id: str) -> models.CDSCinemaDetails:
    cinema_details = (
        models.CDSCinemaDetails.query.join(models.CinemaProviderPivot)
        .filter(models.CinemaProviderPivot.idAtProvider == cinema_id)
        .one()
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
            raise exceptions.UnknownVenueToAlloCine()

    allocine_pivot: models.AllocinePivot | None
    allocine_theater: models.AllocineTheater | None

    def has_pivot(self) -> bool:
        return self.allocine_pivot is not None

    def has_theater(self) -> bool:
        return self.allocine_theater is not None

    def get_pivot(self) -> models.AllocinePivot:
        if not self.has_pivot():
            raise exceptions.NoAllocinePivot
        return cast(models.AllocinePivot, self.allocine_pivot)

    def get_theater(self) -> models.AllocineTheater:
        if self.has_pivot():
            self.allocine_theater = get_allocine_theater(self.venue)
        if not self.has_theater():
            raise exceptions.NoAllocineTheater
        return cast(models.AllocineTheater, self.allocine_theater)


def find_latest_sync_part_end_event(provider: models.Provider) -> models.LocalProviderEvent:
    return (
        models.LocalProviderEvent.query.filter(
            models.LocalProviderEvent.provider == provider,
            models.LocalProviderEvent.type == models.LocalProviderEventType.SyncPartEnd,
            models.LocalProviderEvent.date > datetime.datetime.utcnow() - datetime.timedelta(days=25),
        )
        .order_by(models.LocalProviderEvent.date.desc())
        .first()
    )

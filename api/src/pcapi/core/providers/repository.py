from operator import or_
from typing import Optional

from sqlalchemy.orm import query

from pcapi.core.offerers.models import Venue
from pcapi.core.providers.models import AllocinePivot
from pcapi.core.providers.models import Provider
from pcapi.core.providers.models import VenueProvider


def get_venue_provider_list(venue_id: int) -> list[VenueProvider]:
    return VenueProvider.query.filter_by(venueId=venue_id).all()


def get_venue_provider_by_venue_and_provider_ids(venue_id: int, provider_id: int) -> VenueProvider:
    return VenueProvider.query.filter_by(venueId=venue_id, providerId=provider_id).one()


def get_provider_enabled_for_pro_by_id(provider_id: int) -> Optional[Provider]:
    return Provider.query.filter_by(id=provider_id, isActive=True, enabledForPro=True).one_or_none()


def get_provider_by_local_class(local_class: str) -> Provider:
    return Provider.query.filter_by(localClass=local_class).one_or_none()


def get_active_providers_query() -> query:
    return Provider.query.filter_by(isActive=True).order_by(Provider.name)


def get_enabled_providers_for_pro() -> list[Provider]:
    return get_enabled_providers_for_pro_query().all()


def get_enabled_providers_for_pro_query() -> query:
    return Provider.query.filter_by(isActive=True).filter_by(enabledForPro=True).order_by(Provider.name)


def get_providers_enabled_for_pro_excluding_specific_provider(allocine_local_class: str) -> list[Provider]:
    return (
        Provider.query.filter_by(isActive=True)
        .filter_by(enabledForPro=True)
        .filter(or_(Provider.localClass != allocine_local_class, Provider.localClass.is_(None)))
        .order_by(Provider.name)
        .all()
    )


def has_allocine_pivot_for_venue(venue: Venue) -> bool:
    allocine_link = AllocinePivot.query.filter_by(siret=venue.siret).one_or_none()
    return allocine_link is not None

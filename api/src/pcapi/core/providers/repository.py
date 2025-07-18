import datetime
from typing import Iterable
from typing import Sequence

import sqlalchemy.orm as sa_orm
from sqlalchemy import func
from sqlalchemy import or_

import pcapi.core.offers.models as offers_models
from pcapi.core.categories import subcategories
from pcapi.core.offerers.models import Venue
from pcapi.models import db

from . import constants
from . import models


def get_venue_provider_by_id(venue_provider_id: int) -> models.VenueProvider:
    return db.session.query(models.VenueProvider).filter_by(id=venue_provider_id).one()


def get_venue_provider_list(venue_id: int) -> list[models.VenueProvider]:
    return (
        db.session.query(models.VenueProvider)
        .filter_by(venueId=venue_id)
        .options(sa_orm.joinedload(models.VenueProvider.provider).joinedload(models.Provider.offererProvider))
        .all()
    )


def get_active_venue_providers_by_provider(provider_id: int) -> list[models.VenueProvider]:
    return db.session.query(models.VenueProvider).filter_by(providerId=provider_id, isActive=True).all()


def get_venue_provider_by_venue_and_provider_ids(venue_id: int, provider_id: int) -> models.VenueProvider | None:
    return db.session.query(models.VenueProvider).filter_by(venueId=venue_id, providerId=provider_id).one_or_none()


def get_provider_enabled_for_pro_by_id(provider_id: int | None) -> models.Provider | None:
    return db.session.query(models.Provider).filter_by(id=provider_id, isActive=True, enabledForPro=True).one_or_none()


def get_active_provider_by_id(provider_id: int) -> models.Provider | None:
    return db.session.query(models.Provider).filter_by(id=provider_id, isActive=True).one_or_none()


def get_provider_by_local_class(local_class: str) -> models.Provider:
    return db.session.query(models.Provider).filter_by(localClass=local_class).one_or_none()


def get_provider_by_name(name: str) -> models.Provider:
    return db.session.query(models.Provider).filter_by(name=name).one()


def get_available_providers(venue: Venue) -> sa_orm.Query:
    from pcapi.local_providers import AllocineStocks

    query = (
        db.session.query(models.Provider)
        .filter_by(isActive=True, enabledForPro=True)
        .options(sa_orm.joinedload(models.Provider.offererProvider))
    )

    local_classes_to_exclude = set(constants.CINEMA_PROVIDER_NAMES)
    if pivot := get_cinema_provider_pivot_for_venue(venue):
        if pivot.provider.localClass is not None:
            local_classes_to_exclude.remove(pivot.provider.localClass)

    if not get_allocine_pivot(venue) and not get_allocine_theater(venue):
        local_classes_to_exclude.add(AllocineStocks.__name__)

    if local_classes_to_exclude:
        query = query.filter(
            models.Provider.localClass.notin_(local_classes_to_exclude) | models.Provider.localClass.is_(None)
        )
    return query.order_by(models.Provider.name)


def get_allocine_theater(venue: Venue) -> models.AllocineTheater | None:
    return db.session.query(models.AllocineTheater).filter_by(siret=venue.siret).one_or_none()


def get_allocine_pivot(venue: Venue) -> models.AllocinePivot | None:
    return db.session.query(models.AllocinePivot).filter_by(venue=venue).one_or_none()


def get_cinema_provider_pivot_for_venue(venue: Venue) -> models.CinemaProviderPivot | None:
    return db.session.query(models.CinemaProviderPivot).filter_by(venue=venue).one_or_none()


def get_cds_cinema_details(cinema_id: str) -> models.CDSCinemaDetails:
    cinema_details = (
        db.session.query(models.CDSCinemaDetails)
        .join(models.CinemaProviderPivot)
        .join(models.CinemaProviderPivot.provider)
        .filter(models.CinemaProviderPivot.idAtProvider == cinema_id)
        .filter(models.Provider.localClass == "CDSStocks")
        .one()
    )
    return cinema_details


def get_cinema_venue_provider_query(venue_id: int) -> sa_orm.Query:
    return db.session.query(models.VenueProvider).filter(
        models.VenueProvider.venueId == venue_id,
        models.VenueProvider.isFromCinemaProvider,
    )


def get_boost_cinema_details(cinema_id: str) -> models.BoostCinemaDetails:
    cinema_details = (
        db.session.query(models.BoostCinemaDetails)
        .join(models.CinemaProviderPivot)
        .join(models.CinemaProviderPivot.provider)
        .filter(models.CinemaProviderPivot.idAtProvider == cinema_id)
        .filter(models.Provider.localClass == "BoostStocks")
        .one()
    )
    return cinema_details


def get_cgr_cinema_details(cinema_id: str) -> models.CGRCinemaDetails:
    cinema_details = (
        db.session.query(models.CGRCinemaDetails)
        .join(models.CinemaProviderPivot)
        .join(models.CinemaProviderPivot.provider)
        .filter(models.CinemaProviderPivot.idAtProvider == cinema_id)
        .filter(models.Provider.localClass == "CGRStocks")
        .one()
    )
    return cinema_details


def get_ems_cinema_details(cinema_id: str) -> models.EMSCinemaDetails:
    cinema_details = (
        db.session.query(models.EMSCinemaDetails)
        .join(models.CinemaProviderPivot)
        .join(models.CinemaProviderPivot.provider)
        .filter(models.CinemaProviderPivot.idAtProvider == cinema_id)
        .filter(models.Provider.localClass == "EMSStocks")
        .one()
    )
    return cinema_details


def bump_ems_sync_version(version: int, venues_provider_to_sync: Iterable[int]) -> None:
    """
    Storing the version point (timestamp) from which we are up to update
    """
    ids: list[Sequence[int]] = (
        db.session.query(models.EMSCinemaDetails)
        .join(models.CinemaProviderPivot)
        .join(models.VenueProvider, models.CinemaProviderPivot.providerId == models.VenueProvider.providerId)
        .filter(models.VenueProvider.id.in_(venues_provider_to_sync))
        .with_entities(models.EMSCinemaDetails.id)
        .all()
    )
    db.session.bulk_update_mappings(models.EMSCinemaDetails, [{"id": id, "lastVersion": version} for (id,) in ids])


def get_ems_oldest_sync_version() -> int:
    """
    Get the oldest sync version among all EMSCinemaDetails, for active VenueProviders.

    EMS use a versioned synchronization.
    It means we can pass a version number (actually a timestamp) in our call to their API and within the response
    we get all resources that have been added since that point.
    """
    version = (
        db.session.query(func.min(models.EMSCinemaDetails.lastVersion))
        .join(models.CinemaProviderPivot)
        .join(models.VenueProvider, models.CinemaProviderPivot.providerId == models.VenueProvider.providerId)
        .filter(models.VenueProvider.isActive)
        .scalar()
    )
    return version


def get_pivot_for_id_at_provider(id_at_provider: str, provider_id: int) -> models.CinemaProviderPivot | None:
    pivot = (
        db.session.query(models.CinemaProviderPivot)
        .filter(
            models.CinemaProviderPivot.idAtProvider == id_at_provider,
            models.CinemaProviderPivot.providerId == provider_id,
        )
        .one_or_none()
    )
    return pivot


def is_cinema_external_ticket_applicable(offer: offers_models.Offer) -> bool:
    return bool(
        offer.subcategory.id == subcategories.SEANCE_CINE.id
        and offer.lastProviderId
        and db.session.query(get_cinema_venue_provider_query(offer.venueId).exists()).scalar()
    )


def get_providers_venues(provider_id: int) -> sa_orm.Query:
    return (
        db.session.query(Venue)
        .join(models.VenueProvider)
        .outerjoin(models.VenueProvider.externalUrls)
        .options(sa_orm.contains_eager(Venue.venueProviders).contains_eager(models.VenueProvider.externalUrls))
        .filter(models.VenueProvider.providerId == provider_id)
    )


def _get_future_provider_events_requiring_a_ticketing_system_query(
    provider: models.Provider,
) -> sa_orm.Query:
    # base query
    events_query = (
        db.session.query(offers_models.Offer)
        .join(offers_models.Stock, offers_models.Offer.stocks)
        .join(Venue, offers_models.Offer.venue)
        .join(models.VenueProvider, Venue.venueProviders)
        .outerjoin(models.VenueProviderExternalUrls, models.VenueProvider.externalUrls)
    )

    # Events linked to the provider & requiring a ticketing system
    events_query = events_query.filter(
        offers_models.Offer.lastProvider == provider,
        offers_models.Offer.isEvent,
        offers_models.Offer.withdrawalType == offers_models.WithdrawalTypeEnum.IN_APP,
    )

    # Events with future stocks
    events_query = events_query.filter(
        offers_models.Stock.beginningDatetime >= datetime.datetime.utcnow(),
    )

    return events_query


def get_future_events_requiring_ticketing_system(
    provider: models.Provider,
    venue: models.Venue | None = None,
) -> list[offers_models.Offer]:
    # base query
    future_provider_events_with_ticketing_query = _get_future_provider_events_requiring_a_ticketing_system_query(
        provider
    )

    if venue:
        # Events linked to the provider and venue, requiring a ticketing system
        final_query = future_provider_events_with_ticketing_query.filter(
            offers_models.Offer.venue == venue,
        )
    else:
        # Events not linked to a Venue specific ticketing system
        final_query = future_provider_events_with_ticketing_query.filter(
            or_(
                Venue.venueProviders == None,
                models.VenueProviderExternalUrls.bookingExternalUrl == None,
            )
        )

    return final_query.all()

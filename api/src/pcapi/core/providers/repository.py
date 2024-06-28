import datetime
from typing import Iterable
from typing import Sequence

from flask_sqlalchemy import BaseQuery
from sqlalchemy import func
from sqlalchemy import or_
import sqlalchemy.orm as sqla_orm

from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.external_bookings import exceptions as external_bookings_exceptions
from pcapi.core.offerers.models import Venue
import pcapi.core.offers.models as offers_models
from pcapi.models import db

from . import constants
from . import models


def get_venue_provider_by_id(venue_provider_id: int) -> models.VenueProvider:
    return models.VenueProvider.query.filter_by(id=venue_provider_id).one()


def get_venue_provider_list(venue_id: int) -> list[models.VenueProvider]:
    return (
        models.VenueProvider.query.filter_by(venueId=venue_id)
        .options(sqla_orm.joinedload(models.VenueProvider.provider).joinedload(models.Provider.offererProvider))
        .all()
    )


def get_active_venue_providers_by_provider(provider_id: int) -> list[models.VenueProvider]:
    return models.VenueProvider.query.filter_by(providerId=provider_id, isActive=True).all()


def get_venue_provider_by_venue_and_provider_ids(venue_id: int, provider_id: int) -> models.VenueProvider:
    return models.VenueProvider.query.filter_by(venueId=venue_id, providerId=provider_id).one()


def get_provider_enabled_for_pro_by_id(provider_id: int) -> models.Provider | None:
    return models.Provider.query.filter_by(id=provider_id, isActive=True, enabledForPro=True).one_or_none()


def get_provider_by_local_class(local_class: str) -> models.Provider:
    return models.Provider.query.filter_by(localClass=local_class).one_or_none()


def get_provider_by_name(name: str) -> models.Provider:
    return models.Provider.query.filter_by(name=name).one()


def get_available_providers(venue: Venue) -> BaseQuery:
    from pcapi.local_providers import AllocineStocks

    query = models.Provider.query.filter_by(isActive=True, enabledForPro=True).options(
        sqla_orm.joinedload(models.Provider.offererProvider)
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
    return models.AllocineTheater.query.filter_by(siret=venue.siret).one_or_none()


def get_allocine_pivot(venue: Venue) -> models.AllocinePivot | None:
    return models.AllocinePivot.query.filter_by(venue=venue).one_or_none()


def get_cinema_provider_pivot_for_venue(venue: Venue) -> models.CinemaProviderPivot | None:
    return models.CinemaProviderPivot.query.filter_by(venue=venue).one_or_none()


def get_cds_cinema_details(cinema_id: str) -> models.CDSCinemaDetails:
    cinema_details = (
        models.CDSCinemaDetails.query.join(models.CinemaProviderPivot)
        .join(models.CinemaProviderPivot.provider)
        .filter(models.CinemaProviderPivot.idAtProvider == cinema_id)
        .filter(models.Provider.localClass == "CDSStocks")
        .one()
    )
    return cinema_details


def get_cinema_venue_provider_query(venue_id: int) -> BaseQuery:
    return models.VenueProvider.query.filter(
        models.VenueProvider.venueId == venue_id,
        models.VenueProvider.isFromCinemaProvider,
    )


def get_boost_cinema_details(cinema_id: str) -> models.BoostCinemaDetails:
    cinema_details = (
        models.BoostCinemaDetails.query.join(models.CinemaProviderPivot)
        .join(models.CinemaProviderPivot.provider)
        .filter(models.CinemaProviderPivot.idAtProvider == cinema_id)
        .filter(models.Provider.localClass == "BoostStocks")
        .one()
    )
    return cinema_details


def get_cgr_cinema_details(cinema_id: str) -> models.CGRCinemaDetails:
    cinema_details = (
        models.CGRCinemaDetails.query.join(models.CinemaProviderPivot)
        .join(models.CinemaProviderPivot.provider)
        .filter(models.CinemaProviderPivot.idAtProvider == cinema_id)
        .filter(models.Provider.localClass == "CGRStocks")
        .one()
    )
    return cinema_details


def get_ems_cinema_details(cinema_id: str) -> models.EMSCinemaDetails:
    cinema_details = (
        models.EMSCinemaDetails.query.join(models.CinemaProviderPivot)
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
        models.EMSCinemaDetails.query.join(models.CinemaProviderPivot)
        .join(models.VenueProvider, models.CinemaProviderPivot.providerId == models.VenueProvider.providerId)
        .filter(models.VenueProvider.id.in_(venues_provider_to_sync))
        .with_entities(models.EMSCinemaDetails.id)
        .all()
    )
    db.session.bulk_update_mappings(models.EMSCinemaDetails, [{"id": id, "lastVersion": version} for id, in ids])


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


def get_pivot_for_id_at_provider(id_at_provider: str, provider_id: int) -> models.CinemaProviderPivot | None:
    pivot = models.CinemaProviderPivot.query.filter(
        models.CinemaProviderPivot.idAtProvider == id_at_provider,
        models.CinemaProviderPivot.providerId == provider_id,
    ).one_or_none()
    return pivot


def is_cinema_external_ticket_applicable(offer: offers_models.Offer) -> bool:
    return bool(
        offer.subcategory.id == subcategories.SEANCE_CINE.id
        and offer.lastProviderId
        and db.session.query(get_cinema_venue_provider_query(offer.venueId).exists()).scalar()
    )


def is_event_external_ticket_applicable(offer: offers_models.Offer) -> bool:
    if offer.isEvent and offer.withdrawalType == offers_models.WithdrawalTypeEnum.IN_APP:
        if not (
            offer.lastProvider is not None
            and offer.lastProvider.isActive
            and offer.lastProvider.hasProviderEnableCharlie
        ):
            raise external_bookings_exceptions.ExternalBookingException(
                "Offer provider is inactive or not charlie enabled"
            )
        return True
    return False


def get_providers_venues(provider_id: int) -> BaseQuery:
    return Venue.query.join(models.VenueProvider).filter(models.VenueProvider.providerId == provider_id)


def get_future_events_requiring_provider_ticketing_system(
    provider: models.Provider,
) -> list[offers_models.Offer]:
    # base query
    events_query = (
        offers_models.Offer.query.join(offers_models.Stock, offers_models.Offer.stocks)
        .join(Venue, offers_models.Offer.venue)
        .join(models.VenueProvider, Venue.venueProviders)
        .outerjoin(models.VenueProviderExternalUrls, models.VenueProvider.externalUrls)
    )

    # Events linked to the the provider & requiring a ticketing system
    events_query = events_query.filter(
        offers_models.Offer.lastProvider == provider,
        offers_models.Offer.isEvent,
        offers_models.Offer.withdrawalType == offers_models.WithdrawalTypeEnum.IN_APP,
    )

    # Events with future stocks
    events_query = events_query.filter(
        offers_models.Stock.beginningDatetime >= datetime.datetime.utcnow(),
    )

    # Events not linked to a Venue specific ticketing system
    events_query = events_query.filter(
        or_(
            Venue.venueProviders == None,
            models.VenueProviderExternalUrls.bookingExternalUrl == None,
        )
    )

    return events_query.all()

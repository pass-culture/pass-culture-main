import enum
import functools
import logging
import typing

from pcapi.core import search
from pcapi.core.history import api as history_api
from pcapi.core.history import models as history_models
import pcapi.core.mails.transactional as transactional_mails
from pcapi.core.offerers import models as offerers_models
import pcapi.core.offers.models as offers_models
import pcapi.core.providers.constants as providers_constants
import pcapi.core.providers.exceptions as providers_exceptions
import pcapi.core.providers.models as providers_models
import pcapi.core.providers.repository as providers_repository
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.models.feature import FeatureToggle
from pcapi.repository import repository
from pcapi.repository.session_management import on_commit
from pcapi.routes.serialization.venue_provider_serialize import PostVenueProviderBody
from pcapi.workers.update_all_offers_active_status_job import update_all_collective_offers_active_status_job
from pcapi.workers.update_all_offers_active_status_job import update_venue_synchronized_offers_active_status_job

from . import validation


logger = logging.getLogger(__name__)


class T_UNCHANGED(enum.Enum):
    TOKEN = 0


UNCHANGED = T_UNCHANGED.TOKEN


def create_venue_provider(
    provider: providers_models.Provider,
    venue: offerers_models.Venue,
    current_user: users_models.User,
    payload: providers_models.VenueProviderCreationPayload = providers_models.VenueProviderCreationPayload(),
) -> providers_models.VenueProvider:
    if provider.localClass == "AllocineStocks":
        new_venue_provider = connect_venue_to_allocine(venue, provider.id, payload)
    elif provider.localClass in providers_constants.CINEMA_PROVIDER_NAMES:
        new_venue_provider = connect_venue_to_cinema_provider(venue, provider, payload)
    else:
        new_venue_provider = connect_venue_to_provider(venue, provider)

    if (
        provider.isActive
        and provider.enabledForPro
        and venue.venueTypeCode
        in (
            offerers_models.VenueTypeCode.BOOKSTORE,
            offerers_models.VenueTypeCode.MOVIE,
        )
        and not venue.isPermanent
        and not FeatureToggle.WIP_IS_OPEN_TO_PUBLIC.is_active()
    ):
        venue.isPermanent = True
        db.session.add(venue)
        on_commit(
            functools.partial(
                search.async_index_venue_ids, [venue.id], reason=search.IndexationReason.VENUE_PROVIDER_CREATION
            )
        )

    history_api.add_action(
        history_models.ActionType.SYNC_VENUE_TO_PROVIDER,
        author=current_user,
        venue=venue,
        provider_name=provider.name,
    )
    db.session.flush()

    logger.info(
        "La synchronisation d'offre a été activée",
        extra={"venue_id": venue.id, "provider_id": provider.id},
        technical_message_id="offer.sync.activated",
    )
    return new_venue_provider


def reset_stock_quantity(venue: offerers_models.Venue) -> None:
    """Reset all stock quantity with the number of non-cancelled bookings."""
    logger.info("Resetting all stock quantity for changed sync", extra={"venue": venue.id})
    stocks = db.session.query(offers_models.Stock).filter(
        offers_models.Stock.offerId == offers_models.Offer.id,
        offers_models.Offer.venue == venue,
        offers_models.Offer.idAtProvider.is_not(None),
    )
    stocks.update({"quantity": offers_models.Stock.dnBookedQuantity}, synchronize_session=False)
    db.session.commit()


def delete_venue_provider(
    venue_provider: providers_models.VenueProvider, author: users_models.User, send_email: bool = True
) -> None:
    on_commit(
        functools.partial(
            update_venue_synchronized_offers_active_status_job.delay,
            venue_provider.venueId,
            venue_provider.providerId,
            False,
        )
    )
    if send_email and venue_provider.venue.bookingEmail:
        transactional_mails.send_venue_provider_deleted_email(venue_provider.venue.bookingEmail)

    # Save data now: it won't be available after we have deleted the object.
    venue_id = venue_provider.venueId
    provider_id = venue_provider.provider.id
    history_api.add_action(
        history_models.ActionType.LINK_VENUE_PROVIDER_DELETED,
        author=author,
        venue=venue_provider.venue,
        provider_id=venue_provider.providerId,
        provider_name=venue_provider.provider.name,
    )
    db.session.delete(venue_provider)
    db.session.flush()
    logger.info(
        "Deleted VenueProvider for venue %d",
        venue_id,
        extra={"venue_id": venue_id, "provider_id": provider_id},
        technical_message_id="offer.sync.deleted",
    )


def activate_or_deactivate_venue_provider(
    venue_provider: providers_models.VenueProvider, set_active: bool, author: users_models.User, send_email: bool = True
) -> None:
    if venue_provider.isActive != set_active:
        history_api.add_action(
            history_models.ActionType.LINK_VENUE_PROVIDER_UPDATED,
            author=author,
            venue=venue_provider.venue,
            provider_id=venue_provider.providerId,
            provider_name=venue_provider.provider.name,
            modified_info={"isActive": {"old_info": venue_provider.isActive, "new_info": set_active}},
        )

        venue_provider.isActive = set_active
        if send_email and not venue_provider.isActive and venue_provider.venue.bookingEmail:
            transactional_mails.send_venue_provider_disabled_email(venue_provider.venue.bookingEmail)

        on_commit(
            functools.partial(
                update_venue_synchronized_offers_active_status_job.delay,
                venue_provider.venueId,
                venue_provider.providerId,
                venue_provider.isActive,
            )
        )

        logger.info(
            "Updated VenueProvider %s isActive attribut to %s",
            venue_provider.id,
            venue_provider.isActive,
            extra={"venue_id": venue_provider.venueId, "provider_id": venue_provider.providerId},
            technical_message_id="offer.sync.reactivated" if venue_provider.isActive else "offer.sync.deactivated",
        )


def update_venue_provider(
    venue_provider: providers_models.VenueProvider,
    venue_provider_payload: PostVenueProviderBody,
    author: users_models.User,
) -> providers_models.VenueProvider:
    activate_or_deactivate_venue_provider(venue_provider, bool(venue_provider_payload.isActive), author)
    if venue_provider.isFromAllocineProvider:
        venue_provider = update_allocine_venue_provider(venue_provider, venue_provider_payload)
    else:
        if venue_provider.provider.isCinemaProvider:
            venue_provider = update_cinema_venue_provider(venue_provider, venue_provider_payload)
        repository.save(venue_provider)
    return venue_provider


def update_cinema_venue_provider(
    venue_provider: providers_models.VenueProvider, venue_provider_payload: PostVenueProviderBody
) -> providers_models.VenueProvider:
    venue_provider.isDuoOffers = bool(venue_provider_payload.isDuo)

    return venue_provider


def update_allocine_venue_provider(
    allocine_venue_provider: providers_models.AllocineVenueProvider, venue_provider_payload: PostVenueProviderBody
) -> providers_models.AllocineVenueProvider:
    allocine_venue_provider.quantity = venue_provider_payload.quantity
    assert venue_provider_payload.isDuo is not None  # helps mypy, see PostVenueProviderBody
    allocine_venue_provider.isDuo = venue_provider_payload.isDuo
    allocine_venue_provider.price = venue_provider_payload.price

    repository.save(allocine_venue_provider)

    return allocine_venue_provider


def connect_venue_to_provider(
    venue: offerers_models.Venue,
    provider: providers_models.Provider,
) -> providers_models.VenueProvider:
    venue_provider = providers_models.VenueProvider()
    venue_provider.venue = venue
    venue_provider.provider = provider

    repository.save(venue_provider)

    return venue_provider


def connect_venue_to_allocine(
    venue: offerers_models.Venue,
    provider_id: int,
    payload: providers_models.VenueProviderCreationPayload,
) -> providers_models.AllocineVenueProvider:
    if not payload.price:
        raise providers_exceptions.NoPriceSpecified()
    if payload.isDuo is None:  # see PostVenueProviderBody
        raise ValueError("`isDuo` is required")

    pivot = providers_repository.get_allocine_pivot(venue)
    if not pivot:
        theater = providers_repository.get_allocine_theater(venue)
        if not theater:
            raise providers_exceptions.NoMatchingAllocineTheater()
        pivot = providers_models.AllocinePivot(
            venue=venue,
            theaterId=theater.theaterId,
            internalId=theater.internalId,
        )
        repository.save(pivot)

    venue_provider = providers_models.AllocineVenueProvider(
        venue=venue,
        providerId=provider_id,
        venueIdAtOfferProvider=pivot.theaterId,
        isDuo=payload.isDuo,
        quantity=payload.quantity,
        internalId=pivot.internalId,
        price=payload.price,
    )
    repository.save(venue_provider)

    return venue_provider


def connect_venue_to_cinema_provider(
    venue: offerers_models.Venue,
    provider: providers_models.Provider,
    payload: providers_models.VenueProviderCreationPayload,
) -> providers_models.VenueProvider:
    provider_pivot = providers_repository.get_cinema_provider_pivot_for_venue(venue)

    if not provider_pivot:
        raise providers_exceptions.NoCinemaProviderPivot()

    venue_provider = providers_models.VenueProvider()
    venue_provider.venue = venue
    venue_provider.provider = provider
    venue_provider.isDuoOffers = payload.isDuo if payload.isDuo else False
    venue_provider.venueIdAtOfferProvider = provider_pivot.idAtProvider

    repository.save(venue_provider)
    return venue_provider


def update_provider_external_urls(
    provider: providers_models.Provider,
    *,
    notification_external_url: str | None | T_UNCHANGED = UNCHANGED,
    booking_external_url: str | None | T_UNCHANGED = UNCHANGED,
    cancel_external_url: str | None | T_UNCHANGED = UNCHANGED,
) -> providers_models.Provider:
    ticketing_urls_are_unset = booking_external_url is None and cancel_external_url is None
    ticketing_urls_are_updated = booking_external_url != UNCHANGED or cancel_external_url != UNCHANGED

    # Validation
    if ticketing_urls_are_unset:
        validation.check_ticketing_urls_can_be_unset(provider)
    elif ticketing_urls_are_updated:
        validation.check_ticketing_urls_are_coherently_set(
            provider.bookingExternalUrl if booking_external_url == UNCHANGED else booking_external_url,
            provider.cancelExternalUrl if cancel_external_url == UNCHANGED else cancel_external_url,
        )

    # Update
    if notification_external_url != UNCHANGED:
        provider.notificationExternalUrl = notification_external_url

    if booking_external_url != UNCHANGED:
        provider.bookingExternalUrl = booking_external_url

    if cancel_external_url != UNCHANGED:
        provider.cancelExternalUrl = cancel_external_url

    repository.save(provider)

    return provider


def update_venue_provider_external_urls(
    venue_provider: providers_models.VenueProvider,
    *,
    notification_external_url: str | None | T_UNCHANGED = UNCHANGED,
    booking_external_url: str | None | T_UNCHANGED = UNCHANGED,
    cancel_external_url: str | None | T_UNCHANGED = UNCHANGED,
) -> None:
    ticketing_urls_are_unset = booking_external_url is None and cancel_external_url is None
    ticketing_urls_are_updated = booking_external_url != UNCHANGED or cancel_external_url != UNCHANGED
    ticketing_urls_are_set_at_provider_level = (
        venue_provider.provider.bookingExternalUrl and venue_provider.provider.cancelExternalUrl
    )

    venue_provider_external_urls = venue_provider.externalUrls
    # Existing URLs
    existing_cancel_external_url = (
        venue_provider_external_urls.cancelExternalUrl if venue_provider_external_urls else None
    )
    existing_booking_external_url = (
        venue_provider_external_urls.bookingExternalUrl if venue_provider_external_urls else None
    )
    existing_notification_external_url = (
        venue_provider_external_urls.notificationExternalUrl if venue_provider_external_urls else None
    )

    # Validation
    if ticketing_urls_are_unset and not ticketing_urls_are_set_at_provider_level:
        validation.check_ticketing_urls_can_be_unset(venue_provider.provider, venue_provider.venue)
    elif ticketing_urls_are_updated:
        validation.check_ticketing_urls_are_coherently_set(
            existing_booking_external_url if booking_external_url == UNCHANGED else booking_external_url,
            existing_cancel_external_url if cancel_external_url == UNCHANGED else cancel_external_url,
        )

    # Type of operation
    is_creation = not venue_provider_external_urls and (
        notification_external_url not in (None, UNCHANGED) or booking_external_url not in (None, UNCHANGED)
    )
    is_deletion = venue_provider_external_urls and (
        # expected final notification url
        (existing_notification_external_url if notification_external_url is UNCHANGED else notification_external_url)
        is None
        # expected final booking url
        and (existing_booking_external_url if booking_external_url is UNCHANGED else booking_external_url) is None
    )

    if is_deletion:
        repository.delete(venue_provider_external_urls)
        return

    if is_creation:
        venue_provider_external_urls = providers_models.VenueProviderExternalUrls(
            venueProvider=venue_provider,
        )

    # Update
    if notification_external_url != UNCHANGED:
        venue_provider_external_urls.notificationExternalUrl = notification_external_url

    if booking_external_url != UNCHANGED:
        venue_provider_external_urls.bookingExternalUrl = booking_external_url

    if cancel_external_url != UNCHANGED:
        venue_provider_external_urls.cancelExternalUrl = cancel_external_url

    repository.save(venue_provider_external_urls)

    return


def disable_offers_linked_to_provider(provider_id: int, current_user: typing.Any) -> None:
    venue_providers = db.session.query(providers_models.VenueProvider).filter_by(providerId=provider_id).all()
    for venue_provider in venue_providers:
        on_commit(
            functools.partial(
                update_venue_synchronized_offers_active_status_job.delay,
                venue_provider.venueId,
                provider_id,
                False,
            ),
        )
        collective_offers_filters = {
            "user_id": current_user.id,
            "is_user_admin": current_user.has_admin_role,
            "offerer_id": None,
            "status": None,
            "venue_id": venue_provider.venueId,
            "provider_id": provider_id,
            "name_or_isbn": None,
            "creation_mode": None,
            "period_beginning_date": None,
            "period_ending_date": None,
        }
        on_commit(
            functools.partial(
                update_all_collective_offers_active_status_job.delay,
                collective_offers_filters,
                False,
            ),
        )
        venue_provider.isActive = False

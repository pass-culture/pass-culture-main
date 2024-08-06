from dataclasses import asdict
from datetime import datetime
import decimal
import enum
import logging
import typing
from typing import Iterable

from pcapi.core import search
from pcapi.core.history import api as history_api
from pcapi.core.history import models as history_models
from pcapi.core.logging import log_elapsed
import pcapi.core.mails.transactional as transactional_mails
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers.repository import find_venue_by_id
import pcapi.core.offers.api as offers_api
import pcapi.core.offers.models as offers_models
import pcapi.core.offers.repository as offers_repository
import pcapi.core.providers.constants as providers_constants
import pcapi.core.providers.exceptions as providers_exceptions
import pcapi.core.providers.models as providers_models
import pcapi.core.providers.repository as providers_repository
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.repository import repository
from pcapi.routes.serialization.venue_provider_serialize import PostVenueProviderBody
from pcapi.validation.models.entity_validator import validate
from pcapi.workers.update_all_offers_active_status_job import update_all_collective_offers_active_status_job
from pcapi.workers.update_all_offers_active_status_job import update_venue_synchronized_offers_active_status_job

from . import validation


logger = logging.getLogger(__name__)


class T_UNCHANGED(enum.Enum):
    TOKEN = 0


UNCHANGED = T_UNCHANGED.TOKEN


def create_venue_provider(
    provider_id: int,
    venue_id: int,
    current_user: users_models.User,
    payload: providers_models.VenueProviderCreationPayload = providers_models.VenueProviderCreationPayload(),
) -> providers_models.VenueProvider:
    provider = providers_repository.get_provider_enabled_for_pro_by_id(provider_id)
    if not provider:
        raise providers_exceptions.ProviderNotFound()

    venue = find_venue_by_id(venue_id)

    if not venue:
        raise providers_exceptions.VenueNotFound()

    if provider.localClass == "AllocineStocks":
        new_venue_provider = connect_venue_to_allocine(venue, provider_id, payload)
    elif provider.localClass in providers_constants.CINEMA_PROVIDER_NAMES:
        new_venue_provider = connect_venue_to_cinema_provider(venue, provider, payload)
    else:
        new_venue_provider = connect_venue_to_provider(venue, provider, payload.venueIdAtOfferProvider)

    if (
        provider.isActive
        and provider.enabledForPro
        and venue.venueTypeCode
        in (
            offerers_models.VenueTypeCode.BOOKSTORE,
            offerers_models.VenueTypeCode.MOVIE,
        )
        and not venue.isPermanent
    ):
        venue.isPermanent = True
        repository.save(venue)
        search.async_index_venue_ids(
            [venue.id],
            reason=search.IndexationReason.VENUE_PROVIDER_CREATION,
        )

    history_api.add_action(
        history_models.ActionType.SYNC_VENUE_TO_PROVIDER,
        author=current_user,
        venue=venue,
        provider_name=provider.name,
    )
    db.session.commit()

    logger.info(
        "La synchronisation d'offre a été activée",
        extra={"venue_id": venue_id, "provider_id": provider_id},
        technical_message_id="offer.sync.activated",
    )
    return new_venue_provider


def reset_stock_quantity(venue: offerers_models.Venue) -> None:
    """Reset all stock quantity with the number of non-cancelled bookings."""
    logger.info("Resetting all stock quantity for changed sync", extra={"venue": venue.id})
    stocks = offers_models.Stock.query.filter(
        offers_models.Stock.offerId == offers_models.Offer.id,
        offers_models.Offer.venue == venue,
        offers_models.Offer.idAtProvider.is_not(None),
    )
    stocks.update({"quantity": offers_models.Stock.dnBookedQuantity}, synchronize_session=False)
    db.session.commit()


def delete_venue_provider(
    venue_provider: providers_models.VenueProvider, author: users_models.User, send_email: bool = True
) -> None:
    update_venue_synchronized_offers_active_status_job.delay(venue_provider.venueId, venue_provider.providerId, False)
    if send_email and venue_provider.venue.bookingEmail:
        transactional_mails.send_venue_provider_deleted_email(venue_provider.venue.bookingEmail)

    # Save data now: it won't be available after we have deleted the object.
    venue_id = venue_provider.venueId
    provider_id = venue_provider.provider.id
    history_api.add_action(
        history_models.ActionType.LINK_VENUE_PROVIDER_DELETED,
        author,
        venue=venue_provider.venue,
        provider_id=venue_provider.providerId,
        provider_name=venue_provider.provider.name,
    )
    db.session.delete(venue_provider)
    db.session.commit()
    logger.info(
        "Deleted VenueProvider for venue %d",
        venue_id,
        extra={"venue_id": venue_id, "provider_id": provider_id},
        technical_message_id="offer.sync.deleted",
    )


def update_venue_provider(
    venue_provider: providers_models.VenueProvider, venue_provider_payload: PostVenueProviderBody
) -> providers_models.VenueProvider:
    if venue_provider.isActive != venue_provider_payload.isActive:
        venue_provider.isActive = bool(venue_provider_payload.isActive)
        if not venue_provider.isActive and venue_provider.venue.bookingEmail:
            transactional_mails.send_venue_provider_disabled_email(venue_provider.venue.bookingEmail)
        update_venue_synchronized_offers_active_status_job.delay(
            venue_provider.venueId, venue_provider.providerId, venue_provider.isActive
        )
        logger.info(
            "Updated VenueProvider %s isActive attribut to %s",
            venue_provider.id,
            venue_provider.isActive,
            extra={"venue_id": venue_provider.venueId, "provider_id": venue_provider.providerId},
            technical_message_id="offer.sync.reactivated" if venue_provider.isActive else "offer.sync.deactivated",
        )

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
    venue: offerers_models.Venue, provider: providers_models.Provider, venueIdAtOfferProvider: str | None = None
) -> providers_models.VenueProvider:
    if provider.hasOffererProvider:
        id_at_provider = None
    else:
        id_at_provider = _get_siret(venueIdAtOfferProvider, venue.siret)

    _check_provider_can_be_connected(provider, id_at_provider)

    venue_provider = providers_models.VenueProvider()
    venue_provider.venue = venue
    venue_provider.provider = provider
    venue_provider.venueIdAtOfferProvider = id_at_provider

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
            raise providers_exceptions.UnknownVenueToAlloCine()
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
    if ticketing_urls_are_unset:
        validation.check_venue_ticketing_urls_can_be_unset(venue_provider)
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


def _check_provider_can_be_connected(provider: providers_models.Provider, id_at_provider: str | None) -> None:
    if provider.hasOffererProvider:
        return
    if not provider.implements_provider_api:
        raise providers_exceptions.ProviderWithoutApiImplementation()

    if not _siret_can_be_synchronized(id_at_provider, provider):
        raise providers_exceptions.VenueSiretNotRegistered(provider.name, id_at_provider)
    return


def _siret_can_be_synchronized(
    siret: str | None,
    provider: providers_models.Provider,
) -> bool:
    if not siret:
        return False

    if provider.implements_provider_api:
        provider_api = provider.getProviderAPI()
        return provider_api.is_siret_registered(siret)

    return False


def synchronize_stocks(
    stock_details: Iterable[providers_models.StockDetail], venue: offerers_models.Venue, provider_id: int | None = None
) -> dict[str, int]:
    products_provider_references = [stock_detail.products_provider_reference for stock_detail in stock_details]
    # here product.id_at_providers is the "ref" field that provider api gives use.
    products_by_provider_reference = offers_repository.get_products_map_by_provider_reference(
        products_provider_references
    )

    stock_details = [
        stock for stock in stock_details if stock.products_provider_reference in products_by_provider_reference
    ]

    offers_provider_references = [stock_detail.offers_provider_reference for stock_detail in stock_details]
    # here offers.id_at_providers is the "ref" field that provider api gives use.
    with log_elapsed(
        logger,
        "get_offers_map_by_id_at_provider",
        extra={
            "venue": venue.id,
            "ref_count": len(offers_provider_references),
        },
    ):
        offers_by_provider_reference = offers_repository.get_offers_map_by_id_at_provider(
            offers_provider_references, venue
        )

    products_references = [stock_detail.products_provider_reference for stock_detail in stock_details]
    with log_elapsed(
        logger,
        "get_offers_map_by_venue_reference",
        extra={
            "venue": venue.id,
            "ref_count": len(products_references),
        },
    ):
        offers_by_venue_reference = offers_repository.get_offers_map_by_venue_reference(products_references, venue.id)

    offers_update_mapping = [
        {"id": offer_id, "lastProviderId": provider_id} for offer_id in offers_by_provider_reference.values()
    ]
    db.session.bulk_update_mappings(offers_models.Offer, offers_update_mapping)

    new_offers = _build_new_offers_from_stock_details(
        stock_details,
        offers_by_provider_reference,
        products_by_provider_reference,
        offers_by_venue_reference,
        venue,
        provider_id,
    )
    new_offers_references = [new_offer.idAtProvider for new_offer in new_offers if new_offer.idAtProvider]

    db.session.bulk_save_objects(new_offers)

    new_offers_by_provider_reference = offers_repository.get_offers_map_by_id_at_provider(new_offers_references, venue)
    offers_by_provider_reference = {**offers_by_provider_reference, **new_offers_by_provider_reference}

    stocks_provider_references = [stock.stocks_provider_reference for stock in stock_details]
    stocks_by_provider_reference = offers_repository.get_stocks_by_id_at_providers(stocks_provider_references)
    update_stock_mapping, new_stocks, offer_ids = _get_stocks_to_upsert(
        stock_details,
        stocks_by_provider_reference,
        offers_by_provider_reference,
        products_by_provider_reference,
        provider_id,
    )

    db.session.bulk_save_objects(new_stocks)
    db.session.bulk_update_mappings(offers_models.Stock, update_stock_mapping)

    db.session.commit()

    search.async_index_offer_ids(
        offer_ids,
        reason=search.IndexationReason.STOCK_SYNCHRONIZATION,
        log_extra={"provider_id": provider_id},
    )

    return {
        "new_offers": len(new_offers),
        "new_stocks": len(new_stocks),
        "updated_stocks": len(update_stock_mapping),
    }


def _build_new_offers_from_stock_details(
    stock_details: list[providers_models.StockDetail],
    existing_offers_by_provider_reference: dict[str, int],
    products_by_provider_reference: dict[str, offers_models.Product],
    existing_offers_by_venue_reference: dict[str, int],
    venue: offerers_models.Venue,
    provider_id: int | None,
) -> list[offers_models.Offer]:
    new_offers = []
    for stock_detail in stock_details:
        if stock_detail.offers_provider_reference in existing_offers_by_provider_reference:
            continue
        if stock_detail.venue_reference in existing_offers_by_venue_reference:
            logger.error(
                "There is already an offer with same (ean,venueId) but with a different idAtProviders. Update the idAtProviders of offers and stocks attached to venue %s with update_offer_and_stock_id_at_providers method",
                venue.id,
                extra=asdict(stock_detail),
            )
            continue
        if not stock_detail.available_quantity:
            continue

        product = products_by_provider_reference[stock_detail.products_provider_reference]
        offer = offers_api.build_new_offer_from_product(
            venue,
            product,
            id_at_provider=stock_detail.products_provider_reference,
            provider_id=provider_id,
        )

        if not _validate_stock_or_offer(offer):
            continue

        new_offers.append(offer)

    return new_offers


def _get_stocks_to_upsert(
    stock_details: list[providers_models.StockDetail],
    stocks_by_provider_reference: dict[str, dict],
    offers_by_provider_reference: dict[str, int],
    products_by_provider_reference: dict[str, offers_models.Product],
    provider_id: int | None,
) -> tuple[list[dict], list[offers_models.Stock], set[int]]:
    update_stock_mapping = []
    new_stocks = []
    offer_ids = set()

    for stock_detail in stock_details:
        stock_provider_reference = stock_detail.stocks_provider_reference
        if stock_provider_reference in stocks_by_provider_reference:
            stock = stocks_by_provider_reference[stock_provider_reference]

            # We sometimes get a price of zero for books that should
            # not be free (and are not free in our product table).
            # This happens when the library sets a wrong price in
            # their own software. In that case, we keep the current
            # price.
            if not stock_detail.price and stock["price"] != stock_detail.price:
                logger.info(
                    "Ignored stock price that has been changed to zero",
                    extra={
                        "provider": provider_id,
                        "stock": stock["id"],
                        "previous_stock_price": stock["price"],
                        "new_price": stock_detail.price,
                    },
                )
                stock_detail.price = stock["price"]

            update_stock_mapping.append(
                {
                    "id": stock["id"],
                    "quantity": stock_detail.available_quantity + stock["booking_quantity"],
                    "rawProviderQuantity": stock_detail.available_quantity,
                    "price": stock_detail.price,
                    "lastProviderId": provider_id,
                    "isSoftDeleted": False,
                }
            )
            if _should_reindex_offer(stock_detail.available_quantity, stock_detail.price, stock):
                offer_ids.add(offers_by_provider_reference[stock_detail.offers_provider_reference])

        else:
            if not stock_detail.available_quantity:
                continue

            offer_id = offers_by_provider_reference.get(stock_detail.offers_provider_reference)

            if not offer_id:
                continue

            stock = _build_stock_from_stock_detail(
                stock_detail,
                offer_id,
                provider_id,
            )
            if not _validate_stock_or_offer(stock):
                continue

            new_stocks.append(stock)
            offer_ids.add(stock.offerId)

    return update_stock_mapping, new_stocks, offer_ids


def _build_stock_from_stock_detail(
    stock_detail: providers_models.StockDetail, offers_id: int, provider_id: int | None
) -> offers_models.Stock:
    return offers_models.Stock(
        quantity=stock_detail.available_quantity,
        rawProviderQuantity=stock_detail.available_quantity,
        bookingLimitDatetime=None,
        offerId=offers_id,
        price=stock_detail.price,
        dateModified=datetime.utcnow(),
        idAtProviders=stock_detail.stocks_provider_reference,
        lastProviderId=provider_id,
    )


def _validate_stock_or_offer(model: offers_models.Offer | offers_models.Stock) -> bool:
    model_api_errors = validate(model)
    if model_api_errors.errors.keys():
        logger.exception(
            "[SYNC] errors while trying to add stock or offer with ref %s: %s",
            getattr(model, "idAtProvider", None) or getattr(model, "idAtProviders", None),
            model_api_errors.errors,
        )
        return False

    return True


def _should_reindex_offer(new_quantity: int, new_price: decimal.Decimal, existing_stock: dict) -> bool:
    if existing_stock["price"] != new_price:
        return True

    is_existing_stock_empty = (
        # Existing stock could be None (i.e. infinite) if the offerer manually overrides
        # the quantity of this synchronized offers_models.Stock.
        existing_stock["quantity"] is not None
        and existing_stock["quantity"] <= existing_stock["booking_quantity"]
    )
    is_new_quantity_stock_empty = new_quantity == 0

    return is_existing_stock_empty is not is_new_quantity_stock_empty


def _get_siret(venue_id_at_offer_provider: str | None, siret: str | None) -> str:
    if venue_id_at_offer_provider is not None:
        return venue_id_at_offer_provider
    if siret is not None:
        return siret
    raise providers_exceptions.NoSiretSpecified()


def disable_offers_linked_to_provider(provider_id: int, current_user: typing.Any) -> None:
    venue_providers = providers_models.VenueProvider.query.filter_by(providerId=provider_id).all()
    for venue_provider in venue_providers:
        update_venue_synchronized_offers_active_status_job.delay(venue_provider.venueId, provider_id, False)
        collective_offers_filters = {
            "user_id": current_user.id,
            "is_user_admin": current_user.has_admin_role,
            "offerer_id": None,
            "status": None,
            "venue_id": venue_provider.venueId,
            "provider_id": provider_id,
            "category_id": None,
            "name_or_isbn": None,
            "creation_mode": None,
            "period_beginning_date": None,
            "period_ending_date": None,
        }
        update_all_collective_offers_active_status_job.delay(collective_offers_filters, False)
        venue_provider.isActive = False

from dataclasses import asdict
from datetime import datetime
import logging
from typing import Iterable

from pcapi.core import search
from pcapi.core.logging import log_elapsed
from pcapi.core.offerers.models import Venue
from pcapi.core.offerers.repository import find_venue_by_id
import pcapi.core.offers.models as offers_models
import pcapi.core.offers.repository as offers_repository
import pcapi.core.providers.constants as providers_constants
import pcapi.core.providers.exceptions as providers_exceptions
import pcapi.core.providers.models as providers_models
import pcapi.core.providers.repository as providers_repository
from pcapi.domain.price_rule import PriceRule
from pcapi.models import db
from pcapi.models.product import Product
from pcapi.repository import repository
from pcapi.routes.serialization.venue_provider_serialize import PostVenueProviderBody
from pcapi.use_cases.connect_venue_to_allocine import connect_venue_to_allocine
from pcapi.validation.models.entity_validator import validate
from pcapi.workers.update_all_offers_active_status_job import update_venue_synchronized_offers_active_status_job


logger = logging.getLogger(__name__)


def create_venue_provider(
    provider_id: int,
    venue_id: int,
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

    return new_venue_provider


def reset_stock_quantity(venue: Venue) -> None:
    """Reset all stock quantity with the number of non-cancelled bookings."""
    logger.info("Resetting all stock quantity for changed sync", extra={"venue": venue.id})
    stocks = offers_models.Stock.query.filter(
        offers_models.Stock.offerId == offers_models.Offer.id,
        offers_models.Offer.venue == venue,
        offers_models.Offer.idAtProvider.isnot(None),
    )
    stocks.update({"quantity": offers_models.Stock.dnBookedQuantity}, synchronize_session=False)
    db.session.commit()


def update_last_provider_id(venue: Venue, provider_id: int) -> None:
    """Update all offers' lastProviderId with the new provider_id."""
    logger.info(
        "Updating Offer.last_provider_id for changed sync",
        extra={"venue": venue.id, "provider": provider_id},
    )
    offers = offers_models.Offer.query.filter(
        offers_models.Offer.venue == venue, offers_models.Offer.idAtProvider.isnot(None)
    )
    offers.update({"lastProviderId": provider_id}, synchronize_session=False)
    db.session.commit()


def change_venue_provider(
    venue_provider: providers_models.VenueProvider, new_provider_id: int, venueIdAtOfferProvider: str = None
) -> providers_models.VenueProvider:
    new_provider = providers_repository.get_provider_enabled_for_pro_by_id(new_provider_id)
    if not new_provider:
        raise providers_exceptions.ProviderNotFound()

    id_at_provider = _get_siret(venueIdAtOfferProvider, venue_provider.venue.siret)

    _check_provider_can_be_connected(new_provider, id_at_provider)

    reset_stock_quantity(venue_provider.venue)

    venue_provider.lastSyncDate = None
    venue_provider.provider = new_provider
    venue_provider.venueIdAtOfferProvider = id_at_provider

    logger.info(
        "Changing venue_provider.provider_id", extra={"venue_provider": venue_provider.id, "provider": new_provider_id}
    )
    repository.save(venue_provider)

    update_last_provider_id(venue_provider.venue, new_provider_id)

    return venue_provider


def delete_venue_provider(venue_provider: providers_models.VenueProvider) -> None:
    update_venue_synchronized_offers_active_status_job.delay(venue_provider.venueId, venue_provider.providerId, False)

    if venue_provider.isFromAllocineProvider:
        for price_rule in venue_provider.priceRules:
            repository.delete(price_rule)

    repository.delete(venue_provider)


def update_venue_provider(
    venue_provider: providers_models.VenueProvider, venue_provider_payload: PostVenueProviderBody
) -> providers_models.VenueProvider:
    if venue_provider.isActive != venue_provider_payload.isActive:
        venue_provider.isActive = bool(venue_provider_payload.isActive)
        update_venue_synchronized_offers_active_status_job.delay(
            venue_provider.venueId, venue_provider.providerId, venue_provider.isActive
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
    allocine_venue_provider.isDuo = venue_provider_payload.isDuo  # type: ignore [assignment]
    for price_rule in allocine_venue_provider.priceRules:
        # PriceRule.default is the only existing value at this time
        # could need to be tweaked in the future
        if price_rule.priceRule == PriceRule.default:
            price_rule.price = venue_provider_payload.price

    repository.save(allocine_venue_provider, *allocine_venue_provider.priceRules)

    return allocine_venue_provider


def connect_venue_to_provider(
    venue: Venue, provider: providers_models.Provider, venueIdAtOfferProvider: str = None
) -> providers_models.VenueProvider:
    id_at_provider = _get_siret(venueIdAtOfferProvider, venue.siret)

    _check_provider_can_be_connected(provider, id_at_provider)

    venue_provider = providers_models.VenueProvider()
    venue_provider.venue = venue
    venue_provider.provider = provider
    venue_provider.venueIdAtOfferProvider = id_at_provider

    repository.save(venue_provider)
    return venue_provider


def connect_venue_to_cinema_provider(
    venue: Venue, provider: providers_models.Provider, payload: providers_models.VenueProviderCreationPayload
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


def _check_provider_can_be_connected(provider: providers_models.Provider, id_at_provider: str) -> None:
    if not provider.implements_provider_api:
        raise providers_exceptions.ProviderWithoutApiImplementation()

    if not _siret_can_be_synchronized(id_at_provider, provider):
        raise providers_exceptions.VenueSiretNotRegistered(provider.name, id_at_provider)
    return


def _siret_can_be_synchronized(
    siret: str,
    provider: providers_models.Provider,
) -> bool:
    if not siret:
        return False

    if provider.implements_provider_api:
        provider_api = provider.getProviderAPI()
        return provider_api.is_siret_registered(siret)

    return False


def synchronize_stocks(
    stock_details: Iterable[providers_models.StockDetail], venue: Venue, provider_id: int | None = None
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
    new_offers_references = [new_offer.idAtProvider for new_offer in new_offers]

    db.session.bulk_save_objects(new_offers)

    new_offers_by_provider_reference = offers_repository.get_offers_map_by_id_at_provider(new_offers_references, venue)  # type: ignore [arg-type]
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

    search.async_index_offer_ids(offer_ids)

    return {"new_offers": len(new_offers), "new_stocks": len(new_stocks), "updated_stocks": len(update_stock_mapping)}


def _build_new_offers_from_stock_details(
    stock_details: list[providers_models.StockDetail],
    existing_offers_by_provider_reference: dict[str, int],
    products_by_provider_reference: dict[str, Product],
    existing_offers_by_venue_reference: dict[str, int],
    venue: Venue,
    provider_id: int | None,
) -> list[offers_models.Offer]:
    new_offers = []
    for stock_detail in stock_details:
        if stock_detail.offers_provider_reference in existing_offers_by_provider_reference:
            continue
        if stock_detail.venue_reference in existing_offers_by_venue_reference:
            logger.error(
                "There is already an offer with same (isbn,venueId) but with a different idAtProviders. Update the idAtProviders of offers and stocks attached to venue %s with update_offer_and_stock_id_at_providers method",
                venue.id,
                extra=asdict(stock_detail),
            )
            continue
        if not stock_detail.available_quantity:
            continue

        product = products_by_provider_reference[stock_detail.products_provider_reference]
        offer = _build_new_offer(
            venue,
            product,
            id_at_providers=stock_detail.offers_provider_reference,
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
    products_by_provider_reference: dict[str, Product],
    provider_id: int | None,
) -> tuple[list[dict], list[offers_models.Stock], set[int]]:
    update_stock_mapping = []
    new_stocks = []
    offer_ids = set()

    for stock_detail in stock_details:
        stock_provider_reference = stock_detail.stocks_provider_reference
        product = products_by_provider_reference[stock_detail.products_provider_reference]
        book_price = stock_detail.price or float(product.extraData["prix_livre"])  # type: ignore [call-overload, index]
        if stock_provider_reference in stocks_by_provider_reference:
            stock = stocks_by_provider_reference[stock_provider_reference]

            # FIXME (dbaty, 2021-05-18): analyze logs to see if the
            # provider sometimes stops sending a price after having
            # sent a specific price before. Should we keep the
            # possibly specific price that we have received before? Or
            # should we override with the (generic) product price?
            if not stock_detail.price and float(stock["price"]) != book_price:
                logger.warning(
                    "Stock specific price has been overriden by product price because provider price is missing",
                    extra={
                        "stock": stock["id"],
                        "previous_stock_price": float(stock["price"]),
                        "new_price": book_price,
                    },
                )

            update_stock_mapping.append(
                {
                    "id": stock["id"],
                    "quantity": stock_detail.available_quantity + stock["booking_quantity"],
                    "rawProviderQuantity": stock_detail.available_quantity,
                    "price": book_price,
                    "lastProviderId": provider_id,
                }
            )
            if _should_reindex_offer(stock_detail.available_quantity, book_price, stock):
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
                book_price,
                provider_id,
            )
            if not _validate_stock_or_offer(stock):
                continue

            new_stocks.append(stock)
            offer_ids.add(stock.offerId)

    return update_stock_mapping, new_stocks, offer_ids


def _build_stock_from_stock_detail(
    stock_detail: providers_models.StockDetail, offers_id: int, price: float, provider_id: int | None
) -> offers_models.Stock:
    return offers_models.Stock(
        quantity=stock_detail.available_quantity,
        rawProviderQuantity=stock_detail.available_quantity,
        bookingLimitDatetime=None,
        offerId=offers_id,
        price=price,
        dateModified=datetime.utcnow(),
        idAtProviders=stock_detail.stocks_provider_reference,
        lastProviderId=provider_id,
    )


def _validate_stock_or_offer(model: offers_models.Offer | offers_models.Stock) -> bool:
    model_api_errors = validate(model)
    if model_api_errors.errors.keys():
        logger.exception(
            "[SYNC] errors while trying to add stock or offer with ref %s: %s",
            model.idAtProviders,
            model_api_errors.errors,
        )
        return False

    return True


def _build_new_offer(
    venue: Venue, product: Product, id_at_providers: str, id_at_provider: str, provider_id: int | None
) -> offers_models.Offer:
    return offers_models.Offer(
        bookingEmail=venue.bookingEmail,
        description=product.description,
        extraData=product.extraData,
        idAtProvider=id_at_provider,
        lastProviderId=provider_id,
        name=product.name,
        productId=product.id,
        venueId=venue.id,
        subcategoryId=product.subcategoryId,
        withdrawalDetails=venue.withdrawalDetails,
    )


def _should_reindex_offer(new_quantity: int, new_price: float, existing_stock: dict) -> bool:
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

import logging
import typing

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

from pcapi.core.categories import subcategories
from pcapi.core.finance import utils as finance_utils
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import api as offers_api
from pcapi.core.offers import models as offers_models
from pcapi.core.offers import schemas as offers_schemas
from pcapi.core.providers import models as providers_models
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationType
from pcapi.routes.public.individual_offers.v1.serializers import events as events_serializers
from pcapi.utils import date as date_utils
from pcapi.utils.repository import atomic


logger = logging.getLogger(__name__)


def batch_update_cinema_offers_etl(provider_id: int, request_payload: events_serializers.PutCinemaSessions) -> None:
    extract_result = _extract(provider_id, request_payload)
    transform_result = _transform(request_payload, extract_result)
    with atomic():
        _load(
            transform_result,
            extract_result["provider"],
            extract_result["venue"],
            extract_result["offerer_addresses_by_label_address_id"],
        )


# ETL steps


class _ExtractResult(typing.TypedDict):
    venue: offerers_models.Venue
    provider: providers_models.Provider
    # Products
    products_by_film_id: dict[str, offers_models.Product]
    # Addresses
    offerer_addresses_by_label_address_id: dict[tuple[int, str | None], offerers_models.OffererAddress]
    # Offers and Stocks
    offers_by_id_at_provider: dict[str, offers_models.Offer]


def _extract(provider_id: int, request_payload: events_serializers.PutCinemaSessions) -> _ExtractResult:
    """Extract existing data from DB"""
    allocine_ids, visas = request_payload.get_film_ids_split_by_id_origin()
    offers_addresses = request_payload.get_offers_addresses()
    offers_computed_ids = set()

    for offer in request_payload.offers:
        offers_computed_ids.add(_compute_offer_id_at_provider(request_payload.venue_id, offer))

    provider = db.session.query(providers_models.Provider).filter_by(id=provider_id).one()
    venue = db.session.query(offerers_models.Venue).filter_by(id=request_payload.venue_id).one()

    return {
        "venue": venue,
        "provider": provider,
        "products_by_film_id": _get_existing_movie_products(allocine_ids, visas),
        "offerer_addresses_by_label_address_id": _get_offerer_addresses(offers_addresses, venue_id=venue.id),
        "offers_by_id_at_provider": _get_offers(offers_computed_ids, venue_id=venue.id),
    }


class _OfferUpdate(typing.TypedDict):
    offer: offers_models.Offer
    pricing_categories_to_update: list[tuple[offers_models.PriceCategory, events_serializers.CinemaPriceCategory]]
    pricing_categories_to_create: list[events_serializers.CinemaPriceCategory]
    stocks_to_update: list[tuple[offers_models.Stock, events_serializers.CinemaStock]]
    stocks_to_create: list[events_serializers.CinemaStock]
    stocks_to_delete: list[offers_models.Stock]


class _OfferCreate(typing.TypedDict):
    offer_data: events_serializers.CinemaOffer
    pricing_categories_to_create: list[events_serializers.CinemaPriceCategory]
    stocks_to_create: list[events_serializers.CinemaStock]
    product: offers_models.Product
    address: events_serializers.CinemaOfferAddress | None


class _TransformResult(typing.TypedDict):
    offerers_addresses_to_create: list[events_serializers.CinemaOfferAddress]
    offers_to_update: list[_OfferUpdate]
    offers_to_create: list[_OfferCreate]


def _transform(
    request_payload: events_serializers.PutCinemaSessions,
    extract_result: _ExtractResult,
) -> _TransformResult:
    offerers_addresses_to_create: dict[tuple[int, str | None], events_serializers.CinemaOfferAddress] = {}
    offers_to_update: list[_OfferUpdate] = []
    offers_to_create: list[_OfferCreate] = []

    naive_utc_now = date_utils.get_naive_utc_now()

    for offer_data in request_payload.offers:
        if offer_data.film_id not in extract_result["products_by_film_id"]:
            logger.warning(
                "Movie not found",
                extra={
                    "film_id": offer_data.film_id,
                    "provider_id": extract_result["provider"].id,
                    "venue_id": extract_result["venue"].id,
                },
            )
            continue

        if (
            offer_data.address
            and (offer_data.address.id, offer_data.address.label)
            not in extract_result["offerer_addresses_by_label_address_id"]
        ):
            offerers_addresses_to_create[(offer_data.address.id, offer_data.address.label)] = offer_data.address

        computed_id = _compute_offer_id_at_provider(request_payload.venue_id, offer_data)
        if computed_id in extract_result["offers_by_id_at_provider"]:
            offer = extract_result["offers_by_id_at_provider"][computed_id]

            # Pricing Categories
            price_categories_by_id_at_provider = {pc.idAtProvider: pc for pc in offer.priceCategories}
            pricing_categories_to_update = []
            pricing_categories_to_create = []
            for price_category_data in offer_data.price_categories:
                if price_category_data.id_at_provider in price_categories_by_id_at_provider:
                    pricing_categories_to_update.append(
                        (
                            price_categories_by_id_at_provider[price_category_data.id_at_provider],
                            price_category_data,
                        )
                    )
                else:
                    pricing_categories_to_create.append(price_category_data)

            # Stocks
            stocks_data_by_id_at_provider = {stock.id_at_provider: stock for stock in offer_data.stocks}
            stocks_to_update = []
            stocks_to_delete = []

            for stock in offer.stocks:
                assert stock.idAtProviders  # to make mypy happy
                # stock is in payload -> to update
                if stock.idAtProviders in stocks_data_by_id_at_provider:
                    stock_data = stocks_data_by_id_at_provider.pop(stock.idAtProviders)
                    stocks_to_update.append((stock, stock_data))

                # stock is in the future and not in the payload -> to delete
                elif stock.beginningDatetime and stock.beginningDatetime >= naive_utc_now:
                    stocks_to_delete.append(stock)

            offers_to_update.append(
                {
                    "offer": offer,
                    "pricing_categories_to_update": pricing_categories_to_update,
                    "pricing_categories_to_create": pricing_categories_to_create,
                    "stocks_to_update": stocks_to_update,
                    "stocks_to_create": list(stocks_data_by_id_at_provider.values()),
                    "stocks_to_delete": stocks_to_delete,
                }
            )
        else:
            offers_to_create.append(
                {
                    "offer_data": offer_data,
                    "pricing_categories_to_create": offer_data.price_categories,
                    "stocks_to_create": offer_data.stocks,
                    "product": extract_result["products_by_film_id"][offer_data.film_id],
                    "address": offer_data.address,
                }
            )

    return {
        "offerers_addresses_to_create": list(offerers_addresses_to_create.values()),
        "offers_to_create": offers_to_create,
        "offers_to_update": offers_to_update,
    }


def _load(
    transform_result: _TransformResult,
    provider: providers_models.Provider,
    venue: offerers_models.Venue,
    offerer_addresses_by_label_address_id: dict[tuple[int, str | None], offerers_models.OffererAddress],
) -> None:
    # to avoid mutating arg
    _offerer_addresses_by_label_address_id = dict(offerer_addresses_by_label_address_id.items())
    # Update offers
    for offer_to_update in transform_result["offers_to_update"]:
        with atomic():
            _update_offer(offer_to_update, provider=provider)

    # Create missing offerer addresses
    with atomic():
        for offerer_address_data in transform_result["offerers_addresses_to_create"]:
            offerer_address = offerers_api.get_or_create_offer_location(
                offerer_id=venue.managingOffererId,
                venue_id=venue.id,
                address_id=offerer_address_data.id,
                label=offerer_address_data.label,
            )
            _offerer_addresses_by_label_address_id[(offerer_address.addressId, offerer_address.label)] = offerer_address

    # Create offers
    for offer_data in transform_result["offers_to_create"]:
        with atomic():
            _create_offer(
                offer_data,
                offerer_addresses_by_label_address_id=_offerer_addresses_by_label_address_id,
                venue=venue,
                provider=provider,
            )


# Generic helpers


def _compute_offer_id_at_provider(venue_id: int, offer: events_serializers.CinemaOffer) -> str:
    """To easily find an offer from one update to the other, we compute an offer id that is stored in `offer.idAtProvider`"""
    computed_id = f"{offer.film_id}%{venue_id}"
    if offer.address:
        computed_id = f"{computed_id}%{offer.address.id}"
    return computed_id


# Extract helpers


def _get_existing_movie_products(allocine_ids: set[str], visas: set[str]) -> dict[str, offers_models.Product]:
    products = (
        db.session.query(offers_models.Product)
        .filter(
            sa.or_(
                offers_models.Product.extraData.op("->")("allocineId").in_(allocine_ids),
                offers_models.Product.extraData.op("->>")("visa").in_(visas),
            )
        )
        .all()
    )

    products_by_film_id = {}

    for product in products:
        assert product.extraData  # to make mypy happy
        if product.extraData.get("allocineId"):
            film_id = f"allocine_id:{product.extraData['allocineId']}"
            products_by_film_id[film_id] = product
        if product.extraData.get("visa"):
            film_id = f"visa:{product.extraData['visa']}"
            products_by_film_id[film_id] = product

    return products_by_film_id


def _get_offers(computed_ids: set[str], venue_id: int) -> dict[str, offers_models.Offer]:
    result = {}
    offers = (
        db.session.query(offers_models.Offer)
        .filter(offers_models.Offer.venueId == venue_id)
        .filter(offers_models.Offer.idAtProvider.in_(list(computed_ids)))
        .options(
            sa_orm.selectinload(offers_models.Offer.stocks),
            sa_orm.selectinload(offers_models.Offer.priceCategories),
        )
        .all()
    )

    for offer in offers:
        assert offer.idAtProvider  # to make mypy happy
        result[offer.idAtProvider] = offer

    return result


def _get_offerer_addresses(
    filters_params: list[events_serializers.CinemaOfferAddress],
    venue_id: int,
) -> dict[tuple[int, str | None], offerers_models.OffererAddress]:
    filters = []

    for param in filters_params:
        filters.append(
            sa.and_(
                offerers_models.OffererAddress.label == param.label,
                offerers_models.OffererAddress.addressId == param.id,
                offerers_models.OffererAddress.type == offerers_models.LocationType.OFFER_LOCATION,
                offerers_models.OffererAddress.venueId == venue_id,
            )
        )
    offerer_addresses = db.session.query(offerers_models.OffererAddress).filter(sa.or_(*filters)).all()

    offerer_addresses_by_label_address_id = {}

    for offerer_address in offerer_addresses:
        offerer_addresses_by_label_address_id[(offerer_address.addressId, offerer_address.label)] = offerer_address

    return offerer_addresses_by_label_address_id


# Load helpers


def _create_offer(
    offer_data: _OfferCreate,
    *,
    offerer_addresses_by_label_address_id: dict[tuple[int, str | None], offerers_models.OffererAddress],
    venue: offerers_models.Venue,
    provider: providers_models.Provider,
) -> None:
    product = offer_data["product"]
    oa: None | offerers_models.OffererAddress = None
    if offer_data["address"]:
        oa = offerer_addresses_by_label_address_id[(offer_data["address"].id, offer_data["address"].label)]

    offer = offers_api.create_offer(
        offers_schemas.CreateOffer(  # type: ignore[call-arg]
            name=product.name,
            subcategoryId=subcategories.SEANCE_CINE.id,
            idAtProvider=_compute_offer_id_at_provider(venue_id=venue.id, offer=offer_data["offer_data"]),
            ean=None,
            audioDisabilityCompliant=False,
            mentalDisabilityCompliant=False,
            motorDisabilityCompliant=False,
            visualDisabilityCompliant=False,
        ),
        product=offer_data["product"],
        venue=venue,
        provider=provider,
        offerer_address=oa,
    )
    offers_api.finalize_offer(offer, publication_datetime=date_utils.get_naive_utc_now(), booking_allowed_datetime=None)
    offer.lastValidationDate = date_utils.get_naive_utc_now()
    offer.lastValidationType = OfferValidationType.AUTO
    offer.lastValidationAuthorUserId = None
    offer.validation = offers_models.OfferValidationStatus.APPROVED

    price_category_by_id_at_provider = {}

    # Create price categories
    for price_category_data in offer_data["pricing_categories_to_create"]:
        price_category = offers_api.create_price_category(
            offer,
            price_category_data.label,
            finance_utils.cents_to_full_unit(price_category_data.price),
            id_at_provider=price_category_data.id_at_provider,
        )
        price_category_by_id_at_provider[price_category.idAtProvider] = price_category

    # Create stocks
    for stock_data in offer_data["stocks_to_create"]:
        _create_stock(
            stock_data,
            offer=offer,
            provider=provider,
            price_category=price_category_by_id_at_provider[stock_data.price_category_id_at_provider],
        )


def _update_offer(data: _OfferUpdate, *, provider: providers_models.Provider) -> None:
    offer = data["offer"]
    price_category_by_id_at_provider = {}

    # Update existing price categories
    for price_category, price_category_data in data["pricing_categories_to_update"]:
        price_category.price = finance_utils.cents_to_full_unit(price_category_data.price)
        price_category.label = price_category_data.label
        db.session.flush()
        price_category_by_id_at_provider[price_category.idAtProvider] = price_category

    # Create missing price categories
    for price_category_data in data["pricing_categories_to_create"]:
        price_category = offers_api.create_price_category(
            offer,
            price_category_data.label,
            finance_utils.cents_to_full_unit(price_category_data.price),
            id_at_provider=price_category_data.id_at_provider,
        )
        price_category_by_id_at_provider[price_category.idAtProvider] = price_category

    # Update existing stock
    for stock, stock_data in data["stocks_to_update"]:
        stock.features = [feature.value for feature in stock_data.features]
        offers_api.edit_stock(
            stock,
            price_category=price_category_by_id_at_provider[stock_data.price_category_id_at_provider],
            quantity=stock_data.quantity + stock.dnBookedQuantity,
            beginning_datetime=stock_data.beginning_datetime,
            booking_limit_datetime=stock_data.beginning_datetime,
            editing_provider=provider,
        )
        db.session.flush()

    # Create missing stocks
    for stock_data in data["stocks_to_create"]:
        _create_stock(
            stock_data,
            offer=offer,
            provider=provider,
            price_category=price_category_by_id_at_provider[stock_data.price_category_id_at_provider],
        )

    # Delete stocks
    for stock in data["stocks_to_delete"]:
        # to avoid colision if idAtProvider is reused by provider
        deleted_id_at_provider = f"[DELETED:{date_utils.get_naive_utc_now().timestamp()}]{stock.idAtProviders}"
        stock.idAtProviders = deleted_id_at_provider[0:70]
        offers_api.delete_stock(stock)


def _create_stock(
    stock_data: events_serializers.CinemaStock,
    offer: offers_models.Offer,
    provider: providers_models.Provider,
    price_category: offers_models.PriceCategory,
) -> offers_models.Stock:
    stock = offers_api.create_stock(
        offer,
        quantity=stock_data.quantity,
        price_category=price_category,
        beginning_datetime=stock_data.beginning_datetime,
        booking_limit_datetime=stock_data.beginning_datetime,
        creating_provider=provider,
        id_at_provider=stock_data.id_at_provider,
    )
    stock.features = [feature.value for feature in stock_data.features]
    db.session.flush()

    return stock

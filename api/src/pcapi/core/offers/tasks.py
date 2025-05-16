import datetime
import logging
from typing import TypedDict

import sqlalchemy as sa

from pcapi import repository
from pcapi.celery_tasks.tasks import celery_async_task
from pcapi.core import search
from pcapi.core.finance import utils as finance_utils
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import api as offers_api
from pcapi.core.offers import constants as offers_constants
from pcapi.core.offers import exceptions as offers_exceptions
from pcapi.core.offers import models as offers_models
from pcapi.core.offers import schemas as offers_schemas
from pcapi.core.providers import models as providers_models
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationType
from pcapi.routes.public.individual_offers.v1 import serialization as individual_offers_serialization
from pcapi.routes.public.individual_offers.v1 import utils as individual_offers_utils
from pcapi.workers import worker
from pcapi.workers.decorators import job


logger = logging.getLogger(__name__)


def _get_existing_offers(
    ean_to_create_or_update: set[str],
    venue: offerers_models.Venue,
) -> list[offers_models.Offer]:
    subquery = (
        db.session.query(
            sa.func.max(offers_models.Offer.id).label("max_id"),
        )
        .filter(offers_models.Offer.isEvent == False)
        .filter(offers_models.Offer.venue == venue)
        .filter(offers_models.Offer.ean.in_(ean_to_create_or_update))
        .group_by(
            offers_models.Offer.ean,
            offers_models.Offer.venueId,
        )
        .subquery()
    )

    return (
        individual_offers_utils.retrieve_offer_relations_query(offers_models.Offer.query)
        .join(subquery, offers_models.Offer.id == subquery.c.max_id)
        .all()
    )


def _get_existing_products(ean_to_create: set[str]) -> list[offers_models.Product]:
    return offers_models.Product.query.filter(
        offers_models.Product.ean.in_(ean_to_create),
        offers_models.Product.can_be_synchronized == True,
        offers_models.Product.subcategoryId.in_(offers_constants.ALLOWED_PRODUCT_SUBCATEGORIES),
        # FIXME (cepehang, 2023-09-21) remove these condition when the product table is cleaned up
        offers_models.Product.lastProviderId.is_not(None),
        offers_models.Product.idAtProviders.is_not(None),
    ).all()


def _create_offer_from_product(
    venue: offerers_models.Venue,
    product: offers_models.Product,
    provider: providers_models.Provider,
    offererAddress: offerers_models.OffererAddress,
) -> offers_models.Offer:
    ean = product.ean

    offer = offers_api.build_new_offer_from_product(
        venue,
        product,
        id_at_provider=ean,
        provider_id=provider.id,
        offerer_address_id=offererAddress.id,
    )

    offer.audioDisabilityCompliant = venue.audioDisabilityCompliant
    offer.mentalDisabilityCompliant = venue.mentalDisabilityCompliant
    offer.motorDisabilityCompliant = venue.motorDisabilityCompliant
    offer.visualDisabilityCompliant = venue.visualDisabilityCompliant

    offer.isActive = True
    offer.lastValidationDate = datetime.datetime.utcnow()
    offer.lastValidationType = OfferValidationType.AUTO
    offer.lastValidationAuthorUserId = None

    logger.info(
        "models.Offer has been created",
        extra={
            "offer_id": offer.id,
            "venue_id": venue.id,
            "product_id": offer.productId,
        },
        technical_message_id="offer.created",
    )

    return offer


@celery_async_task(
    name="tasks.offers.default.create_or_update_ean_offers",
    autoretry_for=(),
    model=offers_schemas.CreateOrUpdateEANOffersRequest,
)
def create_or_update_ean_offers_celery(
    payload: offers_schemas.CreateOrUpdateEANOffersRequest,
) -> None:
    _create_or_update_ean_offers(
        serialized_products_stocks=payload.serialized_products_stocks,
        venue_id=payload.venue_id,
        provider_id=payload.provider_id,
        address_id=payload.address_id,
        address_label=payload.address_label,
    )


@job(worker.low_queue)
def create_or_update_ean_offers_rq(
    *,
    serialized_products_stocks: dict[str, offers_schemas.SerializedProductsStocks],
    venue_id: int,
    provider_id: int,
    address_id: int | None = None,
    address_label: str | None = None,
) -> None:
    _create_or_update_ean_offers(
        serialized_products_stocks=serialized_products_stocks,
        venue_id=venue_id,
        provider_id=provider_id,
        address_id=address_id,
        address_label=address_label,
    )


def _create_or_update_ean_offers(
    *,
    serialized_products_stocks: dict[str, offers_schemas.SerializedProductsStocks],
    venue_id: int,
    provider_id: int,
    address_id: int | None = None,
    address_label: str | None = None,
) -> None:
    provider = providers_models.Provider.query.filter_by(id=provider_id).one()
    venue = offerers_models.Venue.query.filter_by(id=venue_id).one()

    ean_to_create_or_update = set(serialized_products_stocks.keys())

    offers_to_update = _get_existing_offers(ean_to_create_or_update, venue)
    offer_to_update_by_ean = {}
    ean_list_to_update = set()
    for offer in offers_to_update:
        offer_ean = offer.ean
        ean_list_to_update.add(offer_ean)
        offer_to_update_by_ean[offer_ean] = offer

    ean_list_to_create = ean_to_create_or_update - ean_list_to_update
    offers_to_index = []
    with repository.transaction():
        offerer_address = venue.offererAddress  # default offerer_address

        if address_id:
            offerer_address = offerers_api.get_or_create_offerer_address(
                offerer_id=venue.managingOffererId,
                address_id=address_id,
                label=address_label,
            )

        if ean_list_to_create:
            created_offers = []
            existing_products = _get_existing_products(ean_list_to_create)
            product_by_ean = {product.ean: product for product in existing_products}
            not_found_eans = [ean for ean in ean_list_to_create if ean not in product_by_ean.keys()]
            if not_found_eans:
                logger.warning(
                    "Some provided eans were not found",
                    extra={"eans": ",".join(not_found_eans), "venue": venue_id},
                    technical_message_id="ean.not_found",
                )
            for product in existing_products:
                try:
                    ean = product.ean
                    stock_data = serialized_products_stocks[ean]

                    if stock_data["quantity"] == 0:
                        continue

                    created_offer = _create_offer_from_product(
                        venue,
                        product_by_ean[ean],
                        provider,
                        offererAddress=offerer_address,
                    )
                    created_offers.append(created_offer)

                except (
                    offers_exceptions.OfferCreationBaseException,
                    offers_exceptions.OfferEditionBaseException,
                ) as exc:
                    logger.info(
                        "Error while creating offer by ean",
                        extra={
                            "ean": ean,
                            "venue_id": venue_id,
                            "provider_id": provider_id,
                            "exc": exc.__class__.__name__,
                        },
                    )

            db.session.bulk_save_objects(created_offers)

            reloaded_offers = _get_existing_offers(ean_list_to_create, venue)
            for offer in reloaded_offers:
                try:
                    ean = offer.ean
                    stock_data = serialized_products_stocks[ean]
                    booking_limit_datetime = _parse_booking_datetime(stock_data["booking_limit_datetime"])
                    # FIXME (mageoffray, 2023-05-26): stock saving optimisation
                    # Stocks are inserted one by one for now, we need to improve create_stock to remove the repository.session.add()
                    # It will be done before the release of this API
                    offers_api.create_stock(
                        offer=offer,
                        price=finance_utils.cents_to_full_unit(stock_data["price"]),
                        quantity=individual_offers_serialization.deserialize_quantity(stock_data["quantity"]),
                        booking_limit_datetime=booking_limit_datetime,
                        creating_provider=provider,
                    )
                except (
                    offers_exceptions.OfferCreationBaseException,
                    offers_exceptions.OfferEditionBaseException,
                ) as exc:
                    logger.info(
                        "Error while creating offer by ean",
                        extra={
                            "ean": ean,
                            "venue_id": venue_id,
                            "provider_id": provider_id,
                            "exc": exc.__class__.__name__,
                        },
                    )

        for offer in offers_to_update:
            try:
                offer.lastProvider = provider
                offer.isActive = True

                ean = offer.ean
                stock_data = serialized_products_stocks[ean]
                booking_limit_datetime = _parse_booking_datetime(stock_data["booking_limit_datetime"])
                # FIXME (mageoffray, 2023-05-26): stock upserting optimisation
                # Stocks are edited one by one for now, we need to improve edit_stock to remove the repository.session.add()
                # It will be done before the release of this API

                # TODO(jbaudet-pass): remove call to .replace(): it should not
                # be needed.
                # Why? Because input checks remove the timezone information as
                # it is not expected after... but StockEdition needs a
                # timezone-aware datetime object.
                # -> datetimes are not always handleded the same way.
                # -> it can be messy.
                booking_limit_datetime = (
                    booking_limit_datetime.replace(tzinfo=datetime.timezone.utc) if booking_limit_datetime else None
                )

                offers_api.upsert_product_stock(
                    offer_to_update_by_ean[ean],
                    individual_offers_serialization.StockEdition(
                        **{
                            "price": stock_data["price"],
                            "quantity": stock_data["quantity"],
                            "booking_limit_datetime": booking_limit_datetime,
                        }
                    ),
                    provider,
                )
                offers_to_index.append(offer_to_update_by_ean[ean].id)
            except (
                offers_exceptions.OfferCreationBaseException,
                offers_exceptions.OfferEditionBaseException,
            ) as exc:
                logger.info(
                    "Error while creating offer by ean",
                    extra={
                        "ean": ean,
                        "venue_id": venue_id,
                        "provider_id": provider_id,
                        "exc": exc.__class__.__name__,
                    },
                )

            except offers_exceptions.TooLateToDeleteStock:
                logger.info(
                    "Could not update stock: too late",
                    extra={
                        "ean": ean,
                        "venue_id": venue_id,
                        "provider_id": provider_id,
                        "stock_data": stock_data,
                    },
                )

    search.async_index_offer_ids(
        offers_to_index,
        reason=search.IndexationReason.OFFER_UPDATE,
        log_extra={"venue_id": venue_id, "source": "offers_public_api"},
    )


def _parse_booking_datetime(datetime_str: str | None) -> datetime.datetime | None:
    result = None
    if datetime_str is not None:
        result = datetime.datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    return result

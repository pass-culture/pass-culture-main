import datetime
import logging

import sqlalchemy as sqla

from pcapi import repository
from pcapi.core import search
from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.finance import utils as finance_utils
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import api as offers_api
from pcapi.core.offers import exceptions as offers_exceptions
from pcapi.core.offers import models as offers_models
from pcapi.core.providers import models as providers_models
from pcapi.models import api_errors
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationType
from pcapi.routes.public.individual_offers.v1 import serialization
from pcapi.routes.public.individual_offers.v1 import utils
from pcapi.workers import worker
from pcapi.workers.decorators import job


logger = logging.getLogger(__name__)


@job(worker.low_queue)
def create_or_update_ean_offers(serialized_products_stocks: dict, venue_id: int, provider_id: int) -> None:
    provider = providers_models.Provider.query.filter_by(id=provider_id).one()
    venue = offerers_models.Venue.query.filter_by(id=venue_id).one()

    ean_to_create_or_update = set(serialized_products_stocks.keys())

    offers_to_update = _get_existing_offers(ean_to_create_or_update, venue)

    offer_to_update_by_ean = {}
    ean_list_to_update = set()
    for offer in offers_to_update:
        ean_list_to_update.add(offer.extraData["ean"])  # type: ignore [index]
        offer_to_update_by_ean[offer.extraData["ean"]] = offer  # type: ignore [index]

    ean_list_to_create = ean_to_create_or_update - ean_list_to_update
    offers_to_index = []
    with repository.transaction():
        if ean_list_to_create:
            created_offers = []
            existing_products = _get_existing_products(ean_list_to_create)
            product_by_ean = {product.extraData["ean"]: product for product in existing_products}  # type: ignore [index]
            not_found_eans = [ean for ean in ean_list_to_create if ean not in product_by_ean.keys()]
            if not_found_eans:
                logger.warning(
                    "Some provided eans were not found",
                    extra={"eans": ",".join(not_found_eans), "venue": venue_id},
                    technical_message_id="ean.not_found",
                )
            for product in existing_products:
                try:
                    ean = product.extraData["ean"] if product.extraData else None
                    stock_data = serialized_products_stocks[ean]
                    created_offer = _create_offer_from_product(
                        venue,
                        product_by_ean[ean],
                        provider,
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
                    ean = offer.extraData["ean"]  # type: ignore [index]
                    stock_data = serialized_products_stocks[ean]
                    # FIXME (mageoffray, 2023-05-26): stock saving optimisation
                    # Stocks are inserted one by one for now, we need to improve create_stock to remove the repository.session.add()
                    # It will be done before the release of this API
                    offers_api.create_stock(
                        offer=offer,
                        price=finance_utils.to_euros(stock_data["price"]),
                        quantity=serialization.deserialize_quantity(stock_data["quantity"]),
                        booking_limit_datetime=stock_data["booking_limit_datetime"],
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

                ean = offer.extraData["ean"]  # type: ignore [index]
                stock_data = serialized_products_stocks[ean]
                # FIXME (mageoffray, 2023-05-26): stock upserting optimisation
                # Stocks are edited one by one for now, we need to improve edit_stock to remove the repository.session.add()
                # It will be done before the release of this API
                upsert_product_stock(
                    offer_to_update_by_ean[ean],
                    serialization.StockEdition(
                        **{
                            "price": stock_data["price"],
                            "quantity": stock_data["quantity"],
                            "booking_limit_datetime": stock_data["booking_limit_datetime"],
                        }
                    ),
                    provider,
                )
                offers_to_index.append(offer_to_update_by_ean[ean].id)
            except (offers_exceptions.OfferCreationBaseException, offers_exceptions.OfferEditionBaseException) as exc:
                logger.info(
                    "Error while creating offer by ean",
                    extra={"ean": ean, "venue_id": venue_id, "provider_id": provider_id, "exc": exc.__class__.__name__},
                )

    search.async_index_offer_ids(
        offers_to_index,
        reason=search.IndexationReason.OFFER_UPDATE,
        log_extra={"venue_id": venue_id, "source": "offers_public_api"},
    )


def _get_existing_products(ean_to_create: set[str]) -> list[offers_models.Product]:
    allowed_product_subcategories = [
        subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id,
        subcategories.SUPPORT_PHYSIQUE_MUSIQUE_VINYLE.id,
        subcategories.LIVRE_PAPIER.id,
    ]
    return offers_models.Product.query.filter(
        offers_models.Product.extraData["ean"].astext.in_(ean_to_create),
        offers_models.Product.can_be_synchronized == True,
        offers_models.Product.subcategoryId.in_(allowed_product_subcategories),
        # FIXME (cepehang, 2023-09-21) remove these condition when the product table is cleaned up
        offers_models.Product.lastProviderId.is_not(None),
        offers_models.Product.idAtProviders.is_not(None),
    ).all()


def _get_existing_offers(
    ean_to_create_or_update: set[str],
    venue: offerers_models.Venue,
) -> list[offers_models.Offer]:
    subquery = (
        db.session.query(
            sqla.func.max(offers_models.Offer.id).label("max_id"),
        )
        .filter(offers_models.Offer.isEvent == False)
        .filter(offers_models.Offer.venue == venue)
        .filter(offers_models.Offer.extraData["ean"].astext.in_(ean_to_create_or_update))
        .group_by(offers_models.Offer.extraData["ean"], offers_models.Offer.venueId)
        .subquery()
    )

    return (
        utils.retrieve_offer_relations_query(offers_models.Offer.query)
        .join(subquery, offers_models.Offer.id == subquery.c.max_id)
        .all()
    )


def serialize_products_from_body(
    products: list[serialization.ProductOfferByEanCreation],
) -> dict:
    stock_details = {}
    for product in products:
        stock_details[product.ean] = {
            "quantity": product.stock.quantity,
            "price": product.stock.price,
            "booking_limit_datetime": product.stock.booking_limit_datetime,
        }
    return stock_details


def _create_offer_from_product(
    venue: offerers_models.Venue,
    product: offers_models.Product,
    provider: providers_models.Provider,
) -> offers_models.Offer:
    ean = product.extraData.get("ean") if product.extraData else None

    offer = offers_api.build_new_offer_from_product(venue, product, ean, provider.id)

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


def upsert_product_stock(
    offer: offers_models.Offer,
    stock_body: serialization.StockEdition | None,
    provider: providers_models.Provider,
) -> None:
    existing_stock = next((stock for stock in offer.activeStocks), None)
    if not stock_body:
        if existing_stock:
            offers_api.delete_stock(existing_stock)
        return

    if not existing_stock:
        if not stock_body.price:
            raise api_errors.ApiErrors({"stock.price": ["Required"]})
        offers_api.create_stock(
            offer=offer,
            price=finance_utils.to_euros(stock_body.price),
            quantity=serialization.deserialize_quantity(stock_body.quantity),
            booking_limit_datetime=stock_body.booking_limit_datetime,
            creating_provider=provider,
        )
        return

    stock_update_body = stock_body.dict(exclude_unset=True)
    price = stock_update_body.get("price", offers_api.UNCHANGED)
    quantity = serialization.deserialize_quantity(stock_update_body.get("quantity", offers_api.UNCHANGED))
    offers_api.edit_stock(
        existing_stock,
        quantity=quantity + existing_stock.dnBookedQuantity if isinstance(quantity, int) else quantity,
        price=finance_utils.to_euros(price) if price != offers_api.UNCHANGED else offers_api.UNCHANGED,
        booking_limit_datetime=stock_update_body.get("booking_limit_datetime", offers_api.UNCHANGED),
        editing_provider=provider,
    )

import datetime
import logging
from typing import cast

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
def bulk_upsert_ean_offers(
    stocks_details_by_eans: dict, venue: offerers_models.Venue, provider: providers_models.Provider
) -> None:
    """
    Upsert (i.e. update if existing otherwise create) offers & their stocks using eans.

    :stocks_details_by_eans: Stock details organized by eans.
                stocks_details_by_eans has the following structure:
                {
                    [ean] : {
                        "quantity": 29,
                        "price": 1234,
                        "booking_limit_datetime": "2024-06-30T14:00:00+02:00"
                    }
                }
    :venue:    Venue for which the offers & stocks are upserted
    :provider: Provider upserting the offers & stocks
    """
    offers_to_upsert_eans = set(stocks_details_by_eans.keys())

    # Update existing offers
    offers_to_update = _get_existing_offers(offers_to_upsert_eans, venue)
    updated_offers_eans = _update_ean_offers(offers_to_update, stocks_details_by_eans, venue, provider)

    # Compute missing offers to create
    offers_to_create_eans = offers_to_upsert_eans - updated_offers_eans

    # Creating missing offers
    if offers_to_create_eans:
        _create_ean_offers(offers_to_create_eans, stocks_details_by_eans, venue, provider)


def serialize_products_from_body(
    products: list[serialization.ProductOfferByEanCreation],
) -> dict:
    """
    Take the serialized JSON to format it into a dict giving the stocks details by eans

    :return: A dict with the following structure:
        {
            [ean] : {
                "quantity": 29,
                "price": 1234,
                "booking_limit_datetime": "2024-06-30T14:00:00+02:00"
            }
        }
    """
    stock_details = {}
    for product in products:
        stock_details[product.ean] = {
            "quantity": product.stock.quantity,
            "price": product.stock.price,
            "booking_limit_datetime": product.stock.booking_limit_datetime,
        }
    return stock_details


def upsert_offer_stock(
    offer: offers_models.Offer,
    stock_body: serialization.StockEdition | None,
    provider: providers_models.Provider,
) -> None:
    """
    Upsert a an offer stock

    :offer:      Offer for which the stock is upserted
    :stock_body: Stock details
    :provider:   Provider doing the upsert
    """
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


def _create_ean_offers(
    offers_to_create_eans: set[str],
    stocks_details_by_eans: dict,
    venue: offerers_models.Venue,
    provider: providers_models.Provider,
) -> None:
    with repository.transaction():
        created_offers = []
        existing_products = _get_existing_products(offers_to_create_eans)
        existing_products_eans = set()

        # Create and save offers
        for product in existing_products:
            ean = product.extraData["ean"]  # type: ignore[index]
            existing_products_eans.add(ean)

            created_offer = _create_offer_by_ean_product(
                ean,  # type: ignore[arg-type]
                venue,
                product,
                provider,
            )

            if created_offer:
                created_offers.append(created_offer)

        db.session.bulk_save_objects(created_offers)

        # Compute missing EANs and warn
        not_found_eans = offers_to_create_eans - existing_products_eans
        if not_found_eans:
            logger.warning(
                "Some provided eans were not found",
                extra={"eans": ",".join(not_found_eans), "venue": venue.id},
                technical_message_id="ean.not_found",
            )

        # Create and save stocks
        reloaded_offers = _get_existing_offers(offers_to_create_eans, venue)
        for offer in reloaded_offers:
            ean = offer.extraData["ean"]  # type: ignore[index]
            stock_data = stocks_details_by_eans[ean]
            # TODO (tcoudray, 2024-06-03): Sub-optimal, should only create.
            # The save should be done using `db.session.bulk_save_objects` like previously for the offer
            _create_and_save_ean_offer_stock(ean, stock_data, offer, provider, venue.id)  # type: ignore[arg-type]


def _update_ean_offers(
    offers_to_update: list[offers_models.Offer],
    stocks_details_by_eans: dict,
    venue: offerers_models.Venue,
    provider: providers_models.Provider,
) -> set[str]:
    offers_to_index = []
    updated_offers_eans = set()

    with repository.transaction():
        for offer in offers_to_update:
            try:
                offer.lastProvider = provider
                offer.isActive = True

                ean = cast(str, offer.extraData["ean"])  # type: ignore[index]
                stock_data = stocks_details_by_eans[ean]
                # FIXME (mageoffray, 2023-05-26): stock upserting optimisation
                # Stocks are edited one by one for now, we need to improve edit_stock to remove the repository.session.add()
                # It will be done before the release of this API
                upsert_offer_stock(
                    offer,
                    serialization.StockEdition(
                        **{
                            "price": stock_data["price"],
                            "quantity": stock_data["quantity"],
                            "booking_limit_datetime": stock_data["booking_limit_datetime"],
                        }
                    ),
                    provider,
                )
                offers_to_index.append(offer.id)
                updated_offers_eans.add(ean)
            except (offers_exceptions.OfferCreationBaseException, offers_exceptions.OfferEditionBaseException) as exc:
                logger.info(
                    "Error while creating offer by ean",
                    extra={"ean": ean, "venue_id": venue.id, "provider_id": provider.id, "exc": exc.__class__.__name__},
                )

    search.async_index_offer_ids(
        offers_to_index,
        reason=search.IndexationReason.OFFER_UPDATE,
        log_extra={"venue_id": venue.id, "source": "offers_public_api"},
    )

    return updated_offers_eans


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


def _create_offer_by_ean_product(
    ean: str,
    venue: offerers_models.Venue,
    product: offers_models.Product,
    provider: providers_models.Provider,
) -> offers_models.Offer | None:
    try:
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
    except (
        offers_exceptions.OfferCreationBaseException,
        offers_exceptions.OfferEditionBaseException,
    ) as exc:
        logger.info(
            "Error while creating offer by ean",
            extra={
                "ean": ean,
                "venue_id": venue.id,
                "provider_id": provider.id,
                "exc": exc.__class__.__name__,
            },
        )
        return None


def _create_and_save_ean_offer_stock(
    ean: str,
    stock_data: dict,
    offer: offers_models.Offer,
    provider: providers_models.Provider,
    venue_id: int,
) -> None:
    try:
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
            "Error while creating offer stock by ean",
            extra={
                "ean": ean,
                "venue_id": venue_id,
                "provider_id": provider.id,
                "exc": exc.__class__.__name__,
            },
        )

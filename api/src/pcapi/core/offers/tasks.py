import datetime
import logging

import sqlalchemy as sa

from pcapi import repository
from pcapi.core import search
from pcapi.core.categories import subcategories
from pcapi.core.finance import utils as finance_utils
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import api as offers_api
from pcapi.core.offers import exceptions as offers_exceptions
from pcapi.core.offers import models as offers_models
from pcapi.core.providers import models as providers_models
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationType
from pcapi.routes.public.individual_offers.v1 import serialization as individual_offers_v1_serialization
from pcapi.routes.public.individual_offers.v1 import utils as individual_offers_v1_utils
from pcapi.workers import worker
from pcapi.workers.decorators import job


logger = logging.getLogger(__name__)

ALLOWED_PRODUCT_SUBCATEGORIES = [
    subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id,
    subcategories.SUPPORT_PHYSIQUE_MUSIQUE_VINYLE.id,
    subcategories.LIVRE_PAPIER.id,
]


def upsert_product_stock(
    offer: offers_models.Offer,
    stock_body: individual_offers_v1_serialization.StockEdition | None,
    provider: providers_models.Provider,
) -> None:
    existing_stock = next((stock for stock in offer.activeStocks), None)
    if not stock_body:
        if existing_stock:
            offers_api.delete_stock(existing_stock)
        return

    if not existing_stock:
        if stock_body.price is None:
            raise offers_exceptions.OfferException({"stock.price": ["Required"]})
        offers_api.create_stock(
            offer=offer,
            price=finance_utils.cents_to_full_unit(stock_body.price),
            quantity=individual_offers_v1_serialization.deserialize_quantity(stock_body.quantity),
            booking_limit_datetime=stock_body.booking_limit_datetime,
            creating_provider=provider,
        )
        return

    stock_update_body = stock_body.dict(exclude_unset=True)
    price = stock_update_body.get("price", offers_api.UNCHANGED)
    quantity = individual_offers_v1_serialization.deserialize_quantity(
        stock_update_body.get("quantity", offers_api.UNCHANGED)
    )
    offers_api.edit_stock(
        existing_stock,
        quantity=quantity + existing_stock.dnBookedQuantity if isinstance(quantity, int) else quantity,
        price=finance_utils.cents_to_full_unit(price) if price != offers_api.UNCHANGED else offers_api.UNCHANGED,
        booking_limit_datetime=stock_update_body.get("booking_limit_datetime", offers_api.UNCHANGED),
        editing_provider=provider,
    )


def _create_offer_from_product(
    venue: offerers_models.Venue,
    product: offers_models.Product,
    provider: providers_models.Provider,
    offererAddress: offerers_models.OffererAddress,
) -> offers_models.Offer:
    offer = offers_api.build_new_offer_from_product(
        venue,
        product,
        id_at_provider=None,
        provider_id=provider.id,
        offerer_address_id=offererAddress.id,
    )

    offer.audioDisabilityCompliant = venue.audioDisabilityCompliant
    offer.mentalDisabilityCompliant = venue.mentalDisabilityCompliant
    offer.motorDisabilityCompliant = venue.motorDisabilityCompliant
    offer.visualDisabilityCompliant = venue.visualDisabilityCompliant

    offer.publicationDatetime = datetime.datetime.utcnow()
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


def _get_existing_products(ean_to_create: set[str]) -> list[offers_models.Product]:
    return (
        db.session.query(offers_models.Product)
        .filter(
            offers_models.Product.ean.in_(ean_to_create),
            offers_models.Product.can_be_synchronized == True,
            offers_models.Product.subcategoryId.in_(ALLOWED_PRODUCT_SUBCATEGORIES),
            # FIXME (cepehang, 2023-09-21) remove these condition when the product table is cleaned up
            offers_models.Product.lastProviderId.is_not(None),
        )
        .all()
    )


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
        individual_offers_v1_utils.retrieve_offer_relations_query(db.session.query(offers_models.Offer))
        .join(subquery, offers_models.Offer.id == subquery.c.max_id)
        .all()
    )


@job(worker.low_queue)
def create_or_update_ean_offers(
    *,
    serialized_products_stocks: dict,
    venue_id: int,
    provider_id: int,
    address_id: int | None = None,
    address_label: str | None = None,
) -> None:
    provider = db.session.query(providers_models.Provider).filter_by(id=provider_id).one()
    venue = db.session.query(offerers_models.Venue).filter_by(id=venue_id).one()

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
            found_eans = {product.ean for product in existing_products}
            not_found_eans = ean_list_to_create - found_eans
            if not_found_eans:
                logger.warning(
                    "Some provided eans were not found",
                    extra={"eans": ",".join(not_found_eans), "venue": venue_id},
                    technical_message_id="ean.not_found",
                )
            for product in existing_products:
                try:
                    created_offer = _create_offer_from_product(
                        venue,
                        product,
                        provider,
                        offererAddress=offerer_address,
                    )
                    created_offers.append(created_offer)

                except offers_exceptions.OfferException as exc:
                    logger.warning(
                        "Error while creating offer by ean",
                        extra={
                            "ean": product.ean,
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
                    # FIXME (mageoffray, 2023-05-26): stock saving optimisation
                    # Stocks are inserted one by one for now, we need to improve create_stock to remove the repository.session.add()
                    # It will be done before the release of this API
                    offers_api.create_stock(
                        offer=offer,
                        price=finance_utils.cents_to_full_unit(stock_data["price"]),
                        quantity=stock_data["quantity"],
                        booking_limit_datetime=stock_data["booking_limit_datetime"],
                        creating_provider=provider,
                    )
                except offers_exceptions.OfferException as exc:
                    logger.warning(
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
                offer.publicationDatetime = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
                offer.offererAddress = offerer_address

                ean = offer.ean
                stock_data = serialized_products_stocks[ean]
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
                booking_limit = stock_data["booking_limit_datetime"]
                booking_limit = booking_limit.replace(tzinfo=datetime.timezone.utc) if booking_limit else None

                upsert_product_stock(
                    offer_to_update_by_ean[ean],
                    individual_offers_v1_serialization.StockEdition(
                        **{
                            "price": stock_data["price"],
                            "quantity": stock_data["quantity"],
                            "booking_limit_datetime": booking_limit,
                        }
                    ),
                    provider,
                )
                offers_to_index.append(offer_to_update_by_ean[ean].id)
            except offers_exceptions.OfferException as exc:
                logger.warning(
                    "Error while creating offer by ean",
                    extra={"ean": ean, "venue_id": venue_id, "provider_id": provider_id, "exc": exc.__class__.__name__},
                )

    search.async_index_offer_ids(
        offers_to_index,
        reason=search.IndexationReason.OFFER_UPDATE,
        log_extra={"venue_id": venue_id, "source": "offers_public_api"},
    )

import datetime
import logging

import sqlalchemy as sa
from pydantic import BaseModel as BaseModelV2

from pcapi.celery_tasks.tasks import celery_async_task
from pcapi.core import search
from pcapi.core.categories import subcategories
from pcapi.core.finance import utils as finance_utils
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers import schemas as offerers_schemas
from pcapi.core.offers import api as offers_api
from pcapi.core.offers import exceptions as offers_exceptions
from pcapi.core.offers import models as offers_models
from pcapi.core.offers import repository as offers_repository
from pcapi.core.offers import schemas as offers_schemas
from pcapi.core.providers import models as providers_models
from pcapi.core.search.models import IndexationReason
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationType
from pcapi.routes.public.individual_offers.v1 import serialization as individual_offers_v1_serialization
from pcapi.routes.public.individual_offers.v1 import utils as individual_offers_v1_utils
from pcapi.routes.public.individual_offers.v1.serializers import products as products_serializers
from pcapi.utils import date as utils_date
from pcapi.utils import repository


logger = logging.getLogger(__name__)

ALLOWED_PRODUCT_SUBCATEGORIES = [
    subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id,
    subcategories.SUPPORT_PHYSIQUE_MUSIQUE_VINYLE.id,
    subcategories.LIVRE_PAPIER.id,
]


# Batch update offer.isActive tasks
class UpdateAllOffersActiveStatusPayload(BaseModelV2):
    is_active: bool
    user_id: int
    offerer_id: int | None
    venue_id: int | None
    name_or_ean: str | None
    category_id: str | None
    creation_mode: str | None
    status: str | None
    period_beginning_date: datetime.date | None
    period_ending_date: datetime.date | None
    offerer_address_id: int | None


@celery_async_task(
    name="tasks.batch_updates.default.update_all_offers_active_status",
    model=UpdateAllOffersActiveStatusPayload,
)
def update_all_offers_active_status_task(payload: UpdateAllOffersActiveStatusPayload) -> None:
    payload_dict = payload.model_dump()
    # TODO (tcoudray-pass, 13/11/25): this is legacy, should be renamed when we drop the RQ job
    name_or_ean = payload_dict.pop("name_or_ean")
    is_active = payload_dict.pop("is_active")

    query = offers_repository.get_offers_by_filters(name_keywords_or_ean=name_or_ean, **payload_dict)
    query = offers_repository.exclude_offers_from_inactive_venue_provider(query)

    offers_api.batch_update_offers(query, activate=is_active)


class UpdateVenueOffersActiveStatusPayload(BaseModelV2):
    is_active: bool
    venue_id: int
    provider_id: int


@celery_async_task(
    name="tasks.batch_updates.default.update_venue_offers_active_status",
    model=UpdateVenueOffersActiveStatusPayload,
)
def update_venue_offers_active_status_task(payload: UpdateVenueOffersActiveStatusPayload) -> None:
    query = offers_repository.get_synchronized_offers_with_provider_for_venue(payload.venue_id, payload.provider_id)
    offers_api.batch_update_offers(query, activate=payload.is_active)


# Batch upsert ean offers task


def upsert_product_stock(
    offer: offers_models.Offer,
    stock_body: products_serializers.StockEdition | None,
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


def _ensure_timezone_exists(dt: datetime.datetime | None) -> datetime.datetime | None:
    # TODO(jbaudet-pass - 12/2025): this utility can be removed once we
    # can be 100% sure that incoming data used to create products, offers
    # and stocks will always have a timezone.
    # Until then, please keep this function: removing it because it
    # SHOULD be ok might be a little bit risky.
    if dt is not None and dt.tzinfo is None:
        return dt.replace(tzinfo=datetime.UTC)
    return dt


def _create_offer_from_product(
    venue: offerers_models.Venue,
    product: offers_models.Product,
    provider: providers_models.Provider,
    offererAddress: offerers_models.OffererAddress,
    publicationDatetime: datetime.datetime | None,
    bookingAllowedDatetime: datetime.datetime | None,
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

    offer.publicationDatetime = publicationDatetime
    offer.bookingAllowedDatetime = bookingAllowedDatetime
    offer.lastValidationDate = utils_date.get_naive_utc_now()
    offer.lastValidationType = OfferValidationType.AUTO
    offer.lastValidationAuthorUserId = None

    db.session.add(offer)
    db.session.flush()

    offers_api.finalize_offer(
        offer, publication_datetime=publicationDatetime, booking_allowed_datetime=bookingAllowedDatetime
    )

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
        .filter(offers_models.Offer.venueId == venue.id)
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


@celery_async_task(
    name="tasks.offers.default.create_or_update_ean_offers",
    model=offers_schemas.CreateOrUpdateEANOffersRequest,
)
def create_or_update_ean_offers_celery(payload: offers_schemas.CreateOrUpdateEANOffersRequest) -> None:
    _create_or_update_ean_offers(
        serialized_products_stocks=payload.serialized_products_stocks,
        venue_id=payload.venue_id,
        provider_id=payload.provider_id,
        address_id=payload.address_id,
        address_label=payload.address_label,
    )


def _update_offer_and_related_stock(
    offer: offers_models.Offer,
    stock_data: offers_schemas.SerializedProductsStock,
    provider: providers_models.Provider,
    offerer_address: offerers_models.OffererAddress,
) -> tuple[bool, offers_models.Offer]:
    """
    Update offer and its stock only when necessary

    :return: (bool, Offer) bool is equal to `True` if the offer or its stock has been updated.
    """
    # Part 1 - Offer update
    should_update_offer = (
        offer.lastProviderId != provider.id  # provider has changed
        or (offer.offererAddress != offerer_address)  # address has changed
        or (
            # offer should be published
            (offer.publicationDatetime is None and stock_data["publication_datetime"])
            # offer should be unpublished
            or (offer.publicationDatetime and stock_data["publication_datetime"] is None)
            # offer should be published in the future
            or (
                stock_data["publication_datetime"]
                and stock_data["publication_datetime"] > utils_date.get_naive_utc_now()
            )
            # offer was planned to be published in the future but should be published now
            or (offer.publicationDatetime and offer.publicationDatetime > utils_date.get_naive_utc_now())
        )
        or (offer.bookingAllowedDatetime != stock_data["booking_allowed_datetime"])
    )

    if should_update_offer:
        offer.lastProvider = provider
        offer.offererAddress = offerer_address
        offer.publicationDatetime = stock_data["publication_datetime"]
        offer.bookingAllowedDatetime = stock_data["booking_allowed_datetime"]

    # Part 2 - Stock create or update
    current_stock = next((stock for stock in offer.activeStocks), None)
    target_stock_price = finance_utils.cents_to_full_unit(stock_data["price"])
    remaining_quantity = individual_offers_v1_serialization.deserialize_quantity(stock_data["quantity"])

    if not current_stock:
        offers_api.create_stock(
            offer=offer,
            price=target_stock_price,
            quantity=remaining_quantity,
            booking_limit_datetime=stock_data["booking_limit_datetime"],
            creating_provider=provider,
        )
        return True, offer

    should_update_stock = (
        # booking_limit_datetime has changed
        (current_stock.bookingLimitDatetime != stock_data["booking_limit_datetime"])
        # price has changed
        or (current_stock.price != target_stock_price)
        # available quantity should be updated
        or (
            isinstance(remaining_quantity, int)
            and remaining_quantity + current_stock.dnBookedQuantity != current_stock.quantity
        )
        # quantity should be set to unlimited
        or (current_stock.quantity and remaining_quantity is None)
    )

    if should_update_stock:
        target_quantity = None  # i.e unlimited
        if isinstance(remaining_quantity, int):
            target_quantity = remaining_quantity + current_stock.dnBookedQuantity

        offers_api.edit_stock(
            current_stock,
            quantity=target_quantity,
            price=target_stock_price,
            booking_limit_datetime=stock_data["booking_limit_datetime"],
            editing_provider=provider,
        )

    return bool(should_update_offer or should_update_stock), offer


def _create_or_update_ean_offers(
    *,
    serialized_products_stocks: dict[str, offers_schemas.SerializedProductsStock],
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
        if address_id:
            offerer_address = offerers_api.get_or_create_offer_location(
                offerer_id=venue.managingOffererId,
                address_id=address_id,
                label=address_label,
            )
        else:
            offerer_address = offers_api.get_or_create_offerer_address_from_address_body(
                offerers_schemas.LocationOnlyOnVenueModel(),
                venue,
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
                    if offerer_address is None:
                        # FIXME(PC-37261): change workflow to make this case impossible.
                        raise Exception("offerer_address should not be None here")
                    assert product.ean  # to make mypy happy
                    stock_data = serialized_products_stocks[product.ean]
                    created_offer = _create_offer_from_product(
                        venue,
                        product,
                        provider,
                        offererAddress=offerer_address,
                        publicationDatetime=stock_data["publication_datetime"],
                        bookingAllowedDatetime=stock_data["booking_allowed_datetime"],
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
                    assert ean  # to make mypy happy
                    stock_data = serialized_products_stocks[ean]
                    # FIXME (mageoffray, 2023-05-26): stock saving optimisation
                    # Stocks are inserted one by one for now, we need to improve create_stock to remove the repository.session.add()
                    # It will be done before the release of this API
                    offers_api.create_stock(
                        offer=offer,
                        price=finance_utils.cents_to_full_unit(stock_data["price"]),
                        quantity=individual_offers_v1_serialization.deserialize_quantity(stock_data["quantity"]),
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
                ean = offer.ean
                assert ean  # to make mypy happy
                # TODO (tcoudray-pass, 08/10/25) : (OA) Remove when `Venue.offererAddress` is not nullable
                assert offerer_address  # to make mypy happy
                has_been_updated, offer = _update_offer_and_related_stock(
                    offer=offer,
                    stock_data=serialized_products_stocks[ean],
                    provider=provider,
                    offerer_address=offerer_address,
                )
                if has_been_updated:
                    offers_to_index.append(offer.id)
            except offers_exceptions.OfferException as exc:
                logger.warning(
                    "Error while creating offer by ean",
                    extra={"ean": ean, "venue_id": venue_id, "provider_id": provider_id, "exc": exc.__class__.__name__},
                )

    search.async_index_offer_ids(
        offers_to_index,
        reason=IndexationReason.OFFER_UPDATE,
        log_extra={"venue_id": venue_id, "source": "offers_public_api"},
    )

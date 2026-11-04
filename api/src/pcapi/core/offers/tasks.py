import datetime
import logging

from pydantic import BaseModel as BaseModelV2

from pcapi.celery_tasks.tasks import celery_async_task
from pcapi.core.categories import subcategories
from pcapi.core.educational import models as educational_models
from pcapi.core.educational.api import offer as educational_api_offer
from pcapi.core.finance import utils as finance_utils
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import api as offers_api
from pcapi.core.offers import exceptions as offers_exceptions
from pcapi.core.offers import models as offers_models
from pcapi.core.offers import repository as offers_repository
from pcapi.core.offers import schemas as offers_schemas
from pcapi.core.providers import models as providers_models
from pcapi.core.providers.etls import public_api_ean_etl
from pcapi.models import db
from pcapi.models import offer_mixin
from pcapi.routes.provider.individual_offers.v1 import serialization as individual_offers_v1_serialization
from pcapi.routes.provider.individual_offers.v1.serializers import products as products_serializers


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
    venue_id: int | None
    name_or_ean: str | None
    category_id: str | None
    creation_mode: str | None
    status: offer_mixin.OfferStatus | None
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
    query = offers_repository.exclude_offers_from_closed_venues(query)

    offers_api.batch_activate_offers(query, activate=is_active)


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
    offers_api.batch_activate_offers(query, activate=payload.is_active)


class UpdateAllVenueOffersEmailPayload(BaseModelV2):
    venue_id: int
    email: str


@celery_async_task(
    name="tasks.batch_updates.default.update_all_venue_offers_email",
    model=UpdateAllVenueOffersEmailPayload,
)
def update_all_venue_offers_email_task(payload: UpdateAllVenueOffersEmailPayload) -> None:
    query = db.session.query(offers_models.Offer).filter_by(venueId=payload.venue_id)
    offers_api.batch_update_offers(query, {"bookingEmail": payload.email})


class UpdateAllVenueOffersAccessibilityPayload(BaseModelV2):
    venue_id: int
    accessibility: dict[str, bool | None]


@celery_async_task(
    name="tasks.batch_updates.default.update_all_venue_offers_accessibility",
    model=UpdateAllVenueOffersAccessibilityPayload,
)
def update_all_venue_offers_accessibility_task(payload: UpdateAllVenueOffersAccessibilityPayload) -> None:
    offer_query = db.session.query(offers_models.Offer).filter(offers_models.Offer.venueId == payload.venue_id)
    collective_offer_query = db.session.query(educational_models.CollectiveOffer).filter(
        educational_models.CollectiveOffer.venueId == payload.venue_id
    )
    collective_offer_template_query = db.session.query(educational_models.CollectiveOfferTemplate).filter(
        educational_models.CollectiveOfferTemplate.venueId == payload.venue_id
    )

    offers_api.batch_update_offers(offer_query, payload.accessibility)
    educational_api_offer.batch_update_collective_offers(collective_offer_query, payload.accessibility)
    educational_api_offer.batch_update_collective_offers_template(
        collective_offer_template_query, payload.accessibility
    )


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


@celery_async_task(
    name="tasks.offers.default.create_or_update_ean_offers_etl",
    model=offers_schemas.CreateOrUpdateEANOffersRequest,
)
def create_or_update_ean_offers_celery_etl(payload: offers_schemas.CreateOrUpdateEANOffersRequest) -> None:
    public_api_ean_etl.batch_create_or_update_ean_offers(payload)


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
    now = datetime.datetime.now(datetime.UTC)
    should_update_offer = (
        offer.lastProviderId != provider.id  # provider has changed
        or (offer.offererAddress != offerer_address)  # address has changed
        or (
            # offer should be published
            (offer.publicationDatetime is None and stock_data["publication_datetime"])
            # offer should be unpublished
            or (offer.publicationDatetime and stock_data["publication_datetime"] is None)
            # offer should be published in the future
            or (stock_data["publication_datetime"] and stock_data["publication_datetime"] > now)
            # offer was planned to be published in the future but should be published now
            or (offer.publicationDatetime and offer.publicationDatetime > now)
        )
        or (offer.bookingAllowedDatetime != stock_data["booking_allowed_datetime"])
        or (offer.externalTicketOfficeUrl != stock_data["external_ticket_office_url"])
    )

    if should_update_offer:
        offer.lastProvider = provider
        offer.offererAddress = offerer_address
        offer.publicationDatetime = stock_data["publication_datetime"]
        offer.bookingAllowedDatetime = stock_data["booking_allowed_datetime"]
        offer.externalTicketOfficeUrl = (
            str(stock_data["external_ticket_office_url"]) if stock_data["external_ticket_office_url"] else None
        )

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

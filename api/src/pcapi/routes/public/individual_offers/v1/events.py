import copy
from datetime import datetime
from datetime import timezone

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

import pcapi.utils.date as date_utils
from pcapi.core.bookings import exceptions as booking_exceptions
from pcapi.core.categories import subcategories
from pcapi.core.finance import utils as finance_utils
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import repository as offerers_repository
from pcapi.core.offerers import schemas as offerers_schemas
from pcapi.core.offers import api as offers_api
from pcapi.core.offers import exceptions as offers_exceptions
from pcapi.core.offers import models as offers_models
from pcapi.core.offers import repository as offers_repository
from pcapi.core.offers import schemas as offers_schemas
from pcapi.core.offers.validation import check_for_duplicated_price_categories
from pcapi.models import api_errors
from pcapi.models import db
from pcapi.routes.public import blueprints
from pcapi.routes.public import spectree_schemas
from pcapi.routes.public import utils as public_utils
from pcapi.routes.public.documentation_constants import http_responses
from pcapi.routes.public.documentation_constants import tags
from pcapi.routes.public.individual_offers.v1.serializers import events as events_serializers
from pcapi.routes.public.services import authorization
from pcapi.routes.public.services.authentication import api_key_required
from pcapi.routes.public.services.authentication import current_api_key
from pcapi.serialization.decorator import spectree_serialize
from pcapi.serialization.spec_tree import ExtendResponse as SpectreeResponse
from pcapi.utils.custom_keys import get_field
from pcapi.utils.transaction_manager import atomic

from . import serialization
from . import utils


def _deserialize_has_ticket(
    has_ticket: bool,
    subcategory_id: str,
) -> offers_models.WithdrawalTypeEnum | None:
    if has_ticket:
        return offers_models.WithdrawalTypeEnum.IN_APP

    if subcategories.ALL_SUBCATEGORIES_DICT[subcategory_id].can_be_withdrawable:
        return offers_models.WithdrawalTypeEnum.NO_TICKET

    return None


@blueprints.public_api.route("/public/offers/v1/events", methods=["POST"])
@atomic()
@api_key_required
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.EVENT_OFFERS],
    response_model=events_serializers.EventOfferResponse,
    resp=SpectreeResponse(
        **(
            http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
            | http_responses.HTTP_400_BAD_REQUEST
            | http_responses.HTTP_404_VENUE_NOT_FOUND
            | {
                "HTTP_200": (events_serializers.EventOfferResponse, "The event offer has been created successfully"),
            }
        )
    ),
)
def post_event_offer(body: events_serializers.EventOfferCreation) -> events_serializers.EventOfferResponse:
    """
    Create Event Offer
    """
    venue_provider = authorization.get_venue_provider_or_raise_404(body.location.venue_id)
    venue = offerers_repository.find_venue_by_id(body.location.venue_id)
    if not venue:
        raise api_errors.ApiErrors({"location.venueId": ["Resource cannot be found"]})
    venue = utils.get_venue_with_offerer_address(body.location.venue_id)

    if body.has_ticket and not (venue_provider.provider.hasTicketingService or venue_provider.hasTicketingService):
        raise api_errors.ApiErrors(
            {
                "global": "You cannot create an event with `has_ticket=true` because you dont have a ticketing service enabled (neither at provider level nor at venue level)."
            }
        )

    withdrawal_type = _deserialize_has_ticket(body.has_ticket, body.category_related_fields.subcategory_id)

    try:
        if body.location.type == "address":
            address = public_utils.get_address_or_raise_404(body.location.address_id)
            offerer_address = offerers_api.get_or_create_offer_location(
                offerer_id=venue.managingOffererId,
                address_id=address.id,
                label=body.location.address_label,
            )
        else:
            offerer_address = offers_api.get_or_create_offerer_address_from_address_body(
                offerers_schemas.LocationOnlyOnVenueModel(),
                venue,
            )

        created_offer = offers_api.create_offer(
            offers_schemas.CreateOffer(
                name=body.name,
                subcategoryId=body.category_related_fields.subcategory_id,
                audioDisabilityCompliant=body.accessibility.audio_disability_compliant,
                mentalDisabilityCompliant=body.accessibility.mental_disability_compliant,
                motorDisabilityCompliant=body.accessibility.motor_disability_compliant,
                visualDisabilityCompliant=body.accessibility.visual_disability_compliant,
                bookingContact=body.booking_contact,
                bookingEmail=body.booking_email,
                description=body.description,
                durationMinutes=body.event_duration,
                externalTicketOfficeUrl=body.external_ticket_office_url,
                extraData=serialization.deserialize_extra_data(body.category_related_fields, venue_id=venue.id),
                idAtProvider=body.id_at_provider,
                isDuo=body.enable_double_bookings,
                url=body.location.url if isinstance(body.location, serialization.DigitalLocation) else None,
                withdrawalDetails=body.withdrawal_details,
                withdrawalType=withdrawal_type,
            ),  # type: ignore[call-arg]
            venue=venue,
            venue_provider=venue_provider,
            provider=current_api_key.provider,
            offerer_address=offerer_address,
        )

        price_categories = body.price_categories or []

        for price_category in price_categories:
            euro_price = finance_utils.cents_to_full_unit(price_category.price)
            offers_api.create_price_category(
                created_offer,
                price_category.label,
                euro_price,
                id_at_provider=price_category.id_at_provider,
            )

        if body.image:
            utils.save_image(body.image, created_offer)

        if body.video_url:
            utils.save_video(body.video_url, created_offer, current_api_key.provider.id)

        publication_date = body.publication_date

        if publication_date:  # the provider used the legacy `publicationDate` param
            # LEGACY :
            # we must must do this transformation on `publicationDate`
            # as our serializer authorizes naive datetimes
            if publication_date.tzinfo is None:  # the provider did not provide a tz in the payload
                # TODO: CLEAN_OA remove this fallback and always use offerer_address when it's not nullable in Venue
                tz = offerer_address.address.timezone if offerer_address else date_utils.METROPOLE_TIMEZONE
                publication_date = date_utils.local_datetime_to_default_timezone(publication_date, local_tz=tz).replace(
                    tzinfo=None
                )
            else:
                publication_date = date_utils.to_naive_utc_datetime(publication_date)
        else:  # the provider used the `publicationDatetime` param
            publication_date = body.publication_datetime  # type: ignore[assignment]

        offers_api.finalize_offer(
            created_offer,
            publication_datetime=publication_date,
            booking_allowed_datetime=body.booking_allowed_datetime,
        )
        db.session.flush()

    except offers_exceptions.OfferException as error:
        raise api_errors.ApiErrors(error.errors)

    return events_serializers.EventOfferResponse.build_event_offer(created_offer)


@blueprints.public_api.route("/public/offers/v1/events/<int:event_id>", methods=["GET"])
@atomic()
@api_key_required
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.EVENT_OFFERS],
    response_model=events_serializers.EventOfferResponse,
    resp=SpectreeResponse(
        **(
            {"HTTP_200": (events_serializers.EventOfferResponse, "The event offer has been returned")}
            # errors
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
            | http_responses.HTTP_404_EVENT_NOT_FOUND
        )
    ),
)
def get_event(event_id: int) -> events_serializers.EventOfferResponse:
    """
    Get Event Offer

    Return event offer by id.
    """
    offer: offers_models.Offer | None = (
        utils.retrieve_offer_relations_query(utils.retrieve_offer_query(event_id))
        .filter(offers_models.Offer.isEvent)
        .one_or_none()
    )
    if not offer:
        raise api_errors.ApiErrors({"event_id": ["The event offer could not be found"]}, status_code=404)

    return events_serializers.EventOfferResponse.build_event_offer(offer)


@blueprints.public_api.route("/public/offers/v1/events", methods=["GET"])
@atomic()
@api_key_required
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.EVENT_OFFERS],
    response_model=events_serializers.EventOffersResponse,
    resp=SpectreeResponse(
        **(
            {"HTTP_200": (events_serializers.EventOffersResponse, "The event offers have been returned")}
            # errors
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
            | http_responses.HTTP_403_UNAUTHORIZED
            | http_responses.HTTP_404_VENUE_NOT_FOUND
        )
    ),
)
def get_events(query: serialization.GetOffersQueryParams) -> events_serializers.EventOffersResponse:
    """
    Get Event Offers

    Return filtered events.

    Results are paginated (by default there are `50` events per page).
    """
    if query.venue_id:
        authorization.get_venue_provider_or_raise_404(query.venue_id)

    total_offers_query = utils.get_filtered_offers_linked_to_provider(query, is_event=True)

    return events_serializers.EventOffersResponse(
        events=[events_serializers.EventOfferResponse.build_event_offer(offer) for offer in total_offers_query],
    )


@blueprints.public_api.route("/public/offers/v1/events/<int:event_id>", methods=["PATCH"])
@atomic()
@api_key_required
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.EVENT_OFFERS],
    response_model=events_serializers.EventOfferResponse,
    resp=SpectreeResponse(
        **(
            {"HTTP_200": (events_serializers.EventOfferResponse, "The event offer has been returned")}
            # errors
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
            | http_responses.HTTP_400_BAD_REQUEST
            | http_responses.HTTP_404_EVENT_NOT_FOUND
        )
    ),
)
def edit_event(event_id: int, body: events_serializers.EventOfferEdition) -> events_serializers.EventOfferResponse:
    """
    Update Event Offer

    Will update only the non-blank fields. If you want some fields to keep their current values, leave them `undefined`.
    """
    offer: offers_models.Offer | None = (
        utils.retrieve_offer_relations_query(utils.retrieve_offer_query(event_id))
        .filter(offers_models.Offer.isEvent)
        .one_or_none()
    )

    if not offer:
        raise api_errors.ApiErrors({"event_id": ["The event offer could not be found"]}, status_code=404)
    utils.check_offer_subcategory(body, offer.subcategoryId)

    venue, offerer_address = utils.extract_venue_and_offerer_address_from_location(body)

    try:
        updates = body.dict(by_alias=True, exclude_unset=True)
        dc = updates.get("accessibility", {})
        extra_data = copy.deepcopy(offer.extraData)

        publication_datetime = get_field(offer, updates, "publicationDatetime")
        is_active = get_field(offer, updates, "isActive")

        # TODO(jbaudet): remove this part, do not use isActive once
        # the public API does not allow it anymore
        if "publicationDatetime" not in updates and updates.get("isActive") is not None:
            publication_datetime = datetime.now(timezone.utc) if is_active else None

        offer = offers_api.update_offer(
            offer,
            offers_schemas.UpdateOffer(
                audioDisabilityCompliant=get_field(offer, dc, "audioDisabilityCompliant"),
                mentalDisabilityCompliant=get_field(offer, dc, "mentalDisabilityCompliant"),
                motorDisabilityCompliant=get_field(offer, dc, "motorDisabilityCompliant"),
                visualDisabilityCompliant=get_field(offer, dc, "visualDisabilityCompliant"),
                bookingContact=get_field(offer, updates, "bookingContact"),
                bookingEmail=get_field(offer, updates, "bookingEmail"),
                description=get_field(offer, updates, "description"),
                durationMinutes=get_field(offer, updates, "eventDuration", col="durationMinutes"),
                ean=get_field(offer, updates, "ean"),
                extraData=(
                    serialization.deserialize_extra_data(
                        body.category_related_fields, extra_data, venue_id=offer.venueId
                    )
                    if "categoryRelatedFields" in updates
                    else extra_data
                ),
                publicationDatetime=publication_datetime,
                idAtProvider=get_field(offer, updates, "idAtProvider"),
                isDuo=get_field(offer, updates, "enableDoubleBookings", col="isDuo"),
                withdrawalDetails=get_field(offer, updates, "itemCollectionDetails", col="withdrawalDetails"),
                name=get_field(offer, updates, "name"),
                url=body.location.url if isinstance(body.location, serialization.DigitalLocation) else None,
                bookingAllowedDatetime=get_field(offer, updates, "bookingAllowedDatetime"),
            ),  # type: ignore[call-arg]
            venue=venue,
            offerer_address=offerer_address,
        )

        if body.image:
            utils.save_image(body.image, offer)
        if "videoUrl" in updates:
            utils.update_or_delete_video(body.video_url, offer, current_api_key.provider.id)

    except offers_exceptions.OfferException as error:
        raise api_errors.ApiErrors(error.errors)

    return events_serializers.EventOfferResponse.build_event_offer(offer)


@blueprints.public_api.route("/public/offers/v1/events/<int:event_id>/price_categories", methods=["POST"])
@atomic()
@api_key_required
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.EVENT_OFFER_PRICES],
    response_model=events_serializers.PriceCategoriesResponse,
    resp=SpectreeResponse(
        **(
            {
                "HTTP_200": (
                    events_serializers.PriceCategoriesResponse,
                    "The price category has been created successfully",
                )
            }
            # errors
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
            | http_responses.HTTP_400_BAD_REQUEST
            | http_responses.HTTP_404_EVENT_NOT_FOUND
        )
    ),
)
def post_event_price_categories(
    event_id: int, body: events_serializers.PriceCategoriesCreation
) -> events_serializers.PriceCategoriesResponse:
    """
    Create Price Categories

    Batch create price categories for given event.
    """
    offer = utils.retrieve_offer_query(event_id).filter(offers_models.Offer.isEvent).one_or_none()
    if not offer:
        raise api_errors.ApiErrors({"event_id": ["The event could not be found"]}, status_code=404)

    # We convert the price to euros because the price has different types in different apis
    new_labels_and_prices = {(p.label, finance_utils.cents_to_full_unit(p.price)) for p in body.price_categories}
    check_for_duplicated_price_categories(new_labels_and_prices, offer.id)

    existing_price_categories_count = offers_repository.get_offer_price_categories(offer.id).count()

    if (
        existing_price_categories_count + len(body.price_categories)
        > offers_models.Offer.MAX_PRICE_CATEGORIES_PER_OFFER
    ):
        raise api_errors.ApiErrors(
            {
                "priceCategories": [
                    f"An offer cannot have more than {offers_models.Offer.MAX_PRICE_CATEGORIES_PER_OFFER} price categories"
                ]
            }
        )

    created_price_categories: list[offers_models.PriceCategory] = []

    for price_category in body.price_categories:
        created_price_categories.append(
            offers_api.create_price_category(
                offer,
                label=price_category.label,
                price=finance_utils.cents_to_full_unit(price_category.price),
                id_at_provider=price_category.id_at_provider,
            )
        )

    return events_serializers.PriceCategoriesResponse.build_price_categories(created_price_categories)


@blueprints.public_api.route("/public/offers/v1/events/<int:event_id>/price_categories", methods=["GET"])
@atomic()
@api_key_required
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.EVENT_OFFER_PRICES],
    response_model=events_serializers.PriceCategoriesResponse,
    resp=SpectreeResponse(
        **(
            {
                "HTTP_200": (
                    events_serializers.PriceCategoriesResponse,
                    "The price category has been created successfully",
                )
            }
            # errors
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
            | http_responses.HTTP_400_BAD_REQUEST
            | http_responses.HTTP_404_EVENT_NOT_FOUND
        )
    ),
)
def get_event_price_categories(
    event_id: int, query: events_serializers.IsAtProviderQueryParams
) -> events_serializers.PriceCategoriesResponse:
    """
    Get Price Categories

    Get existing price categories for given event
    """
    offer = utils.retrieve_offer_query(event_id).filter(offers_models.Offer.isEvent).one_or_none()

    if not offer:
        raise api_errors.ApiErrors({"event_id": ["The event could not be found"]}, status_code=404)

    price_categories = offers_repository.get_offer_price_categories(
        offer.id,
        id_at_provider_list=query.ids_at_provider,  # type: ignore[arg-type]
    ).all()

    return events_serializers.PriceCategoriesResponse.build_price_categories(price_categories)


@blueprints.public_api.route(
    "/public/offers/v1/events/<int:event_id>/price_categories/<int:price_category_id>", methods=["PATCH"]
)
@atomic()
@api_key_required
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.EVENT_OFFER_PRICES],
    response_model=events_serializers.PriceCategoryResponse,
    resp=SpectreeResponse(
        **(
            {
                "HTTP_200": (
                    events_serializers.PriceCategoryResponse,
                    "The price category has been modified successfully",
                )
            }
            # errors
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
            | http_responses.HTTP_400_BAD_REQUEST
            | http_responses.HTTP_404_PRICE_CATEGORY_OR_EVENT_NOT_FOUND
        )
    ),
)
def patch_event_price_category(
    event_id: int,
    price_category_id: int,
    body: events_serializers.PriceCategoryEdition,
) -> events_serializers.PriceCategoryResponse:
    """
    Update Price Category

    Will update only the non-blank field.
    If you want one of the field to remain unchanged, leave it `undefined`.
    """
    event_offer = utils.get_event_with_details(event_id)
    if not event_offer:
        raise api_errors.ApiErrors({"event_id": ["The event could not be found"]}, status_code=404)

    price_category_to_edit = utils.get_price_category_from_event(event_offer, price_category_id)
    if not price_category_to_edit:
        raise api_errors.ApiErrors({"price_category_id": ["No price category could be found"]}, status_code=404)

    update_body = body.dict(exclude_unset=True)

    eurocent_price = update_body.get("price", offers_api.UNCHANGED)
    offers_api.edit_price_category(
        event_offer,
        price_category=price_category_to_edit,
        label=update_body.get("label", offers_api.UNCHANGED),
        price=(
            finance_utils.cents_to_full_unit(eurocent_price)
            if eurocent_price != offers_api.UNCHANGED
            else offers_api.UNCHANGED
        ),
        id_at_provider=update_body.get("id_at_provider", offers_api.UNCHANGED),
        editing_provider=current_api_key.provider,
    )

    return events_serializers.PriceCategoryResponse.from_orm(price_category_to_edit)


@blueprints.public_api.route("/public/offers/v1/events/<int:event_id>/dates", methods=["POST"])
@atomic()
@api_key_required
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.EVENT_OFFER_STOCKS],
    response_model=events_serializers.PostDatesResponse,
    resp=SpectreeResponse(
        **(
            {"HTTP_200": (events_serializers.PostDatesResponse, "The event dates have been created successfully")}
            # errors
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
            | http_responses.HTTP_400_BAD_REQUEST
            | http_responses.HTTP_404_PRICE_CATEGORY_OR_EVENT_NOT_FOUND
        )
    ),
)
def post_event_stocks(
    event_id: int, body: events_serializers.EventStocksCreation
) -> events_serializers.PostDatesResponse:
    """
    Add Stocks to an Event

    Add stocks to given event. Each stock is attached to a price category and to a date.
    For a given date, you will have one stock per price category.

    **⚠️ Event must have less than 2 500 stocks** otherwise they will not be published.
    """
    offer = (
        utils.retrieve_offer_query(event_id)
        .options(sa_orm.joinedload(offers_models.Offer.priceCategories))
        .filter(offers_models.Offer.isEvent)
        .one_or_none()
    )

    if not offer:
        raise api_errors.ResourceNotFoundError({"event_id": ["The event could not be found"]})

    new_dates: list[offers_models.Stock] = []
    existing_stocks_count = offers_repository.get_offer_existing_stocks_count(offer.id)

    if len(body.dates) + existing_stocks_count > offers_models.Offer.MAX_STOCKS_PER_OFFER:
        raise api_errors.ApiErrors(
            {
                "dates": [
                    f"The maximum number of stock entries allowed per offer is {offers_models.Offer.MAX_STOCKS_PER_OFFER}"
                ]
            }
        )

    errors = {}

    for date_index, date_item in enumerate(body.dates):
        try:
            price_category = next((c for c in offer.priceCategories if c.id == date_item.price_category_id), None)
            if not price_category:
                errors[f"dates.{date_index}.priceCategoryId"] = ["The price category could not be found"]
                continue

            new_dates.append(
                offers_api.create_stock(
                    offer=offer,
                    price_category=price_category,
                    quantity=serialization.deserialize_quantity(date_item.quantity),
                    beginning_datetime=date_item.beginning_datetime,
                    booking_limit_datetime=date_item.booking_limit_datetime,
                    creating_provider=current_api_key.provider,
                    id_at_provider=date_item.id_at_provider,
                )
            )
            if not existing_stocks_count and body.dates:
                offers_api.update_offer_fraud_information(offer, user=None)
        except offers_exceptions.OfferException as exc:
            for error_key, error_msg in exc.errors.items():
                errors[f"dates.{date_index}.{error_key}"] = error_msg

    if errors:
        raise api_errors.ApiErrors(errors)

    return events_serializers.PostDatesResponse(
        dates=[events_serializers.DateResponse.build_date(new_date) for new_date in new_dates]
    )


@blueprints.public_api.route("/public/offers/v1/events/<int:event_id>/dates", methods=["GET"])
@atomic()
@api_key_required
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.EVENT_OFFER_STOCKS],
    response_model=events_serializers.GetDatesResponse,
    resp=SpectreeResponse(
        **(
            {"HTTP_200": (events_serializers.GetDatesResponse, "The event dates have been returned")}
            # errors
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
            | http_responses.HTTP_400_BAD_REQUEST
            | http_responses.HTTP_404_PRICE_CATEGORY_OR_EVENT_NOT_FOUND
        )
    ),
)
def get_event_stocks(
    event_id: int, query: events_serializers.IsAtProviderQueryParams
) -> events_serializers.GetDatesResponse:
    """
    Get Event Stocks

    Return all stocks for given event. Results are paginated (by default there are `50` date per page).
    """
    offer = utils.retrieve_offer_query(event_id).filter(offers_models.Offer.isEvent).one_or_none()
    if not offer:
        raise api_errors.ApiErrors({"event_id": ["The event could not be found"]}, status_code=404)

    stock_id_query = (
        db.session.query(offers_models.Stock)
        .filter(
            offers_models.Stock.offerId == offer.id,
            sa.not_(offers_models.Stock.isSoftDeleted),
            offers_models.Stock.id >= query.firstIndex,
        )
        .with_entities(offers_models.Stock.id)
    )

    if query.ids_at_provider is not None:
        stock_id_query = stock_id_query.filter(offers_models.Stock.idAtProviders.in_(query.ids_at_provider))

    total_stock_ids = [stock_id for (stock_id,) in stock_id_query.all()]

    stocks = (
        db.session.query(offers_models.Stock)
        .filter(offers_models.Stock.id.in_(total_stock_ids))
        .options(
            sa_orm.joinedload(offers_models.Stock.priceCategory).joinedload(
                offers_models.PriceCategory.priceCategoryLabel
            )
        )
        .order_by(offers_models.Stock.id)
        .limit(query.limit)
    )

    return events_serializers.GetDatesResponse(
        dates=[events_serializers.DateResponse.build_date(stock) for stock in stocks],
    )


@blueprints.public_api.route("/public/offers/v1/events/<int:event_id>/dates/<int:stock_id>", methods=["DELETE"])
@atomic()
@api_key_required
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.EVENT_OFFER_STOCKS],
    on_success_status=204,
    resp=SpectreeResponse(
        **(
            {"HTTP_204": (None, "The event date has been deleted successfully")}
            # errors
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
            | http_responses.HTTP_400_BAD_REQUEST
            | http_responses.HTTP_404_PRICE_CATEGORY_OR_EVENT_NOT_FOUND
        )
    ),
)
def delete_event_stock(event_id: int, stock_id: int) -> None:
    """
    Delete Event Stock

    When an event stock is deleted, all cancellable bookings (i.e not used) are cancelled.
    To prevent from further bookings, you may alternatively update the stock's quantity to the bookedQuantity (but not below).
    """
    offer = (
        utils.retrieve_offer_query(event_id)
        .filter(offers_models.Offer.isEvent)
        .options(sa_orm.joinedload(offers_models.Offer.stocks))
        .one_or_none()
    )
    if not offer:
        raise api_errors.ResourceNotFoundError({"event_id": ["The event could not be found"]})
    stock_to_delete = next((stock for stock in offer.stocks if stock.id == stock_id and not stock.isSoftDeleted), None)
    if not stock_to_delete:
        raise api_errors.ResourceNotFoundError({"stock_id": ["No stock could be found"]})
    try:
        offers_api.delete_stock(stock_to_delete)
    except offers_exceptions.OfferException as error:
        raise api_errors.ApiErrors(error.errors)


@blueprints.public_api.route("/public/offers/v1/events/<int:event_id>/dates/<int:stock_id>", methods=["PATCH"])
@atomic()
@api_key_required
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.EVENT_OFFER_STOCKS],
    response_model=events_serializers.DateResponse,
    resp=SpectreeResponse(
        **(
            {"HTTP_200": (events_serializers.DateResponse, "The event date has been modified successfully")}
            # errors
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
            | http_responses.HTTP_400_BAD_REQUEST
            | http_responses.HTTP_404_PRICE_CATEGORY_OR_EVENT_NOT_FOUND
        )
    ),
)
def patch_event_stock(
    event_id: int,
    stock_id: int,
    body: events_serializers.EventStockEdition,
) -> events_serializers.DateResponse:
    """
    Update Event Stock

    Update the price category and the beginning time of an event stock.
    """
    offer: offers_models.Offer | None = (
        utils.retrieve_offer_relations_query(utils.retrieve_offer_query(event_id))
        .filter(offers_models.Offer.isEvent)
        .one_or_none()
    )
    if not offer:
        raise api_errors.ResourceNotFoundError({"event_id": ["The event could not be found"]})

    stock_to_edit = next((stock for stock in offer.stocks if stock.id == stock_id and not stock.isSoftDeleted), None)
    if not stock_to_edit:
        raise api_errors.ResourceNotFoundError({"stock_id": ["No stock could be found"]})

    price_category: offers_models.PriceCategory | offers_api.T_UNCHANGED | None = offers_api.UNCHANGED

    if body.price_category_id is not None:
        price_category = next((c for c in offer.priceCategories if c.id == body.price_category_id), None)

        if not price_category:
            raise api_errors.ResourceNotFoundError({"priceCategoryId": ["The price category could not be found"]})

    update_body = body.dict(exclude_unset=True)
    try:
        quantity = serialization.deserialize_quantity(update_body.get("quantity", offers_api.UNCHANGED))
        edited_stock, is_beginning_updated = offers_api.edit_stock(
            stock_to_edit,
            quantity=quantity + stock_to_edit.dnBookedQuantity if isinstance(quantity, int) else quantity,
            price_category=price_category,
            booking_limit_datetime=update_body.get("booking_limit_datetime", offers_api.UNCHANGED),
            beginning_datetime=update_body.get("beginning_datetime", offers_api.UNCHANGED),
            id_at_provider=update_body.get("id_at_provider", offers_api.UNCHANGED),
            editing_provider=current_api_key.provider,
        )
        offers_api.handle_stocks_edition([(stock_to_edit, is_beginning_updated)])
    except offers_exceptions.OfferException as error:
        raise api_errors.ApiErrors(error.errors)
    except booking_exceptions.BookingIsAlreadyCancelled:
        raise api_errors.ResourceGoneError({"booking": ["Cette réservation a été annulée"]})
    except booking_exceptions.BookingIsAlreadyRefunded:
        raise api_errors.ResourceGoneError({"payment": ["Le remboursement est en cours de traitement"]})
    except booking_exceptions.BookingHasActivationCode:
        raise api_errors.ForbiddenError({"booking": ["Cette réservation ne peut pas être marquée comme inutilisée"]})
    except booking_exceptions.BookingIsNotUsed:
        raise api_errors.ResourceGoneError({"booking": ["Cette contremarque n'a pas encore été validée"]})
    # `edited_stock` could be None if nothing was changed.
    return events_serializers.DateResponse.build_date(edited_stock or stock_to_edit)


@blueprints.public_api.route("/public/offers/v1/events/categories", methods=["GET"])
@atomic()
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.OFFER_ATTRIBUTES],
    response_model=events_serializers.GetEventCategoriesResponse,
    resp=SpectreeResponse(
        **(
            {"HTTP_200": (events_serializers.GetEventCategoriesResponse, "The event categories have been returned")}
            # errors
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
        )
    ),
)
@api_key_required
def get_event_categories() -> events_serializers.GetEventCategoriesResponse:
    """
    Get Event Categories

    Return all the categories available, with their conditional fields, and whether they are required.
    """
    event_categories_response = []
    for subcategory in subcategories.EVENT_SUBCATEGORIES.values():
        if subcategory.is_selectable:
            event_categories_response.append(
                events_serializers.EventCategoryResponse(
                    id=subcategory.id,
                    conditional_fields={
                        field: condition.is_required_in_external_form
                        for field, condition in subcategory.conditional_fields.items()
                    },
                    label=subcategory.pro_label,
                )
            )
    return events_serializers.GetEventCategoriesResponse(root=event_categories_response)

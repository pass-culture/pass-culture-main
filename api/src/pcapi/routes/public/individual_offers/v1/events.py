import copy

import sqlalchemy as sqla

from pcapi import repository
from pcapi.core.bookings import exceptions as booking_exceptions
from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.finance import utils as finance_utils
from pcapi.core.offers import api as offers_api
from pcapi.core.offers import exceptions as offers_exceptions
from pcapi.core.offers import models as offers_models
from pcapi.core.offers.validation import check_for_duplicated_price_categories
from pcapi.models import api_errors
from pcapi.models import db
from pcapi.routes.public import spectree_schemas
from pcapi.routes.public.documentation_constants import http_responses
from pcapi.routes.public.documentation_constants import tags
from pcapi.serialization.decorator import spectree_serialize
from pcapi.serialization.spec_tree import ExtendResponse as SpectreeResponse
from pcapi.validation.routes.users_authentifications import api_key_required
from pcapi.validation.routes.users_authentifications import current_api_key

from . import blueprint
from . import serialization
from . import utils


def _deserialize_has_ticket(
    has_ticket: bool,
    subcategory_id: str,
) -> offers_models.WithdrawalTypeEnum | None:
    if not has_ticket:
        if subcategories.ALL_SUBCATEGORIES_DICT[subcategory_id].can_be_withdrawable:
            return offers_models.WithdrawalTypeEnum.NO_TICKET
        return None

    if not current_api_key.provider.hasProviderEnableCharlie:
        raise api_errors.ApiErrors(
            {"global": "You must support the pass culture ticketting interface to use the in_app value."},
            status_code=400,
        )
    return offers_models.WithdrawalTypeEnum.IN_APP


@blueprint.v1_offers_blueprint.route("/events", methods=["POST"])
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.EVENT_OFFERS_TAG],
    response_model=serialization.EventOfferResponse,
    resp=SpectreeResponse(
        **(
            http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
            | http_responses.HTTP_400_BAD_REQUEST
            | http_responses.HTTP_404_VENUE_NOT_FOUND
            | {
                "HTTP_200": (serialization.EventOfferResponse, "The event offer has been created successfully"),
            }
        )
    ),
)
@api_key_required
def post_event_offer(body: serialization.EventOfferCreation) -> serialization.EventOfferResponse:
    """
    Create event offer
    """
    venue = utils.retrieve_venue_from_location(body.location)
    withdrawal_type = _deserialize_has_ticket(body.has_ticket, body.category_related_fields.subcategory_id)
    try:
        with repository.transaction():
            created_offer = offers_api.create_offer(
                audio_disability_compliant=body.accessibility.audio_disability_compliant,
                booking_contact=body.booking_contact,
                booking_email=body.booking_email,
                description=body.description,
                duration_minutes=body.duration_minutes,
                external_ticket_office_url=body.external_ticket_office_url,
                extra_data=serialization.deserialize_extra_data(body.category_related_fields),
                is_duo=body.is_duo,
                mental_disability_compliant=body.accessibility.mental_disability_compliant,
                motor_disability_compliant=body.accessibility.motor_disability_compliant,
                name=body.name,
                provider=current_api_key.provider,
                subcategory_id=body.category_related_fields.subcategory_id,
                url=body.location.url if isinstance(body.location, serialization.DigitalLocation) else None,
                venue=venue,
                visual_disability_compliant=body.accessibility.visual_disability_compliant,
                withdrawal_details=body.withdrawal_details,
                withdrawal_type=withdrawal_type,
                id_at_provider=body.id_at_provider,
            )
            # To create the priceCategories, the offer needs to have an id
            db.session.flush()

            price_categories = body.price_categories or []
            for price_category in price_categories:
                euro_price = finance_utils.to_euros(price_category.price)
                offers_api.create_price_category(created_offer, price_category.label, euro_price)

            if body.image:
                utils.save_image(body.image, created_offer)

            offers_api.publish_offer(created_offer, user=None)

    except (offers_exceptions.OfferCreationBaseException, offers_exceptions.OfferEditionBaseException) as error:
        raise api_errors.ApiErrors(error.errors, status_code=400)

    return serialization.EventOfferResponse.build_event_offer(created_offer)


@blueprint.v1_offers_blueprint.route("/events/<int:event_id>", methods=["GET"])
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.EVENT_OFFERS_TAG],
    response_model=serialization.EventOfferResponse,
    resp=SpectreeResponse(
        **(
            {"HTTP_200": (serialization.EventOfferResponse, "The event offer has been returned")}
            # errors
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
            | http_responses.HTTP_404_EVENT_NOT_FOUND
        )
    ),
)
@api_key_required
def get_event(event_id: int) -> serialization.EventOfferResponse:
    """
    Get event offer

    Return event offer by id.
    """
    offer: offers_models.Offer | None = (
        utils.retrieve_offer_relations_query(utils.retrieve_offer_query(event_id))
        .filter(offers_models.Offer.isEvent)
        .one_or_none()
    )
    if not offer:
        raise api_errors.ApiErrors({"event_id": ["The event offer could not be found"]}, status_code=404)

    return serialization.EventOfferResponse.build_event_offer(offer)


@blueprint.v1_offers_blueprint.route("/events", methods=["GET"])
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.EVENT_OFFERS_TAG],
    response_model=serialization.EventOffersResponse,
    resp=SpectreeResponse(
        **(
            {"HTTP_200": (serialization.EventOffersResponse, "The event offers have been returned")}
            # errors
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
            | http_responses.HTTP_404_VENUE_NOT_FOUND
        )
    ),
)
@api_key_required
def get_events(query: serialization.GetOffersQueryParams) -> serialization.EventOffersResponse:
    """
    Get events

    Return all the events linked to given venue.
    Results are paginated (by default there are `50` events per page).
    """
    utils.check_venue_id_is_tied_to_api_key(query.venue_id)
    total_offers_query = utils.retrieve_offers(
        is_event=True,
        firstIndex=query.firstIndex,
        filtered_venue_id=query.venue_id,
        ids_at_provider=query.ids_at_provider,  # type: ignore[arg-type]
    ).limit(query.limit)

    return serialization.EventOffersResponse(
        events=[serialization.EventOfferResponse.build_event_offer(offer) for offer in total_offers_query],
    )


@blueprint.v1_offers_blueprint.route("/events/<int:event_id>", methods=["PATCH"])
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.EVENT_OFFERS_TAG],
    response_model=serialization.EventOfferResponse,
    resp=SpectreeResponse(
        **(
            {"HTTP_200": (serialization.EventOfferResponse, "The event offer has been returned")}
            # errors
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
            | http_responses.HTTP_400_BAD_REQUEST
            | http_responses.HTTP_404_EVENT_NOT_FOUND
        )
    ),
)
@api_key_required
def edit_event(event_id: int, body: serialization.EventOfferEdition) -> serialization.EventOfferResponse:
    """
    Update event offer

    Will update only the non-blank fields. If you some fields to keep their current values, leave them `undefined`.
    """
    offer: offers_models.Offer | None = (
        utils.retrieve_offer_relations_query(utils.retrieve_offer_query(event_id))
        .filter(offers_models.Offer.isEvent)
        .one_or_none()
    )

    if not offer:
        raise api_errors.ApiErrors({"event_id": ["The event offer could not be found"]}, status_code=404)
    utils.check_offer_subcategory(body, offer.subcategoryId)

    update_body = body.dict(exclude_unset=True)

    try:
        with repository.transaction():
            offer = offers_api.update_offer(
                offer,
                bookingContact=update_body.get("booking_contact", offers_api.UNCHANGED),
                bookingEmail=update_body.get("booking_email", offers_api.UNCHANGED),
                durationMinutes=update_body.get("duration_minutes", offers_api.UNCHANGED),
                extraData=(
                    serialization.deserialize_extra_data(body.category_related_fields, copy.deepcopy(offer.extraData))
                    if body.category_related_fields
                    else offers_api.UNCHANGED
                ),
                isActive=update_body.get("is_active", offers_api.UNCHANGED),
                isDuo=update_body.get("is_duo", offers_api.UNCHANGED),
                withdrawalDetails=update_body.get("withdrawal_details", offers_api.UNCHANGED),
                description=update_body.get("description", offers_api.UNCHANGED),
                idAtProvider=update_body.get("id_at_provider", offers_api.UNCHANGED),
                **utils.compute_accessibility_edition_fields(update_body.get("accessibility")),
            )
            if body.image:
                utils.save_image(body.image, offer)
    except (offers_exceptions.OfferCreationBaseException, offers_exceptions.OfferEditionBaseException) as error:
        raise api_errors.ApiErrors(error.errors, status_code=400)

    return serialization.EventOfferResponse.build_event_offer(offer)


@blueprint.v1_offers_blueprint.route("/events/<int:event_id>/price_categories", methods=["POST"])
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.EVENT_OFFER_PRICES_TAG],
    response_model=serialization.PriceCategoriesResponse,
    resp=SpectreeResponse(
        **(
            {"HTTP_200": (serialization.PriceCategoriesResponse, "The price category has been created successfully")}
            # errors
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
            | http_responses.HTTP_400_BAD_REQUEST
            | http_responses.HTTP_404_EVENT_NOT_FOUND
        )
    ),
)
@api_key_required
def post_event_price_categories(
    event_id: int, body: serialization.PriceCategoriesCreation
) -> serialization.PriceCategoriesResponse:
    """
    Create price categories

    Batch create price categories for given event.
    """
    offer = utils.retrieve_offer_query(event_id).filter(offers_models.Offer.isEvent).one_or_none()
    if not offer:
        raise api_errors.ApiErrors({"event_id": ["The event could not be found"]}, status_code=404)

    # We convert the price to euros beucause the price has different types in different apis
    new_labels_and_prices = {(p.label, finance_utils.to_euros(p.price)) for p in body.price_categories}
    check_for_duplicated_price_categories(new_labels_and_prices, offer.id)

    created_price_categories: list[offers_models.PriceCategory] = []
    try:
        with repository.transaction():
            for price_category in body.price_categories:
                euro_price = finance_utils.to_euros(price_category.price)
                created_price_categories.append(
                    offers_api.create_price_category(offer, price_category.label, euro_price)
                )
    except offers_exceptions.OfferEditionBaseException as error:
        raise api_errors.ApiErrors(error.errors, status_code=400)

    return serialization.PriceCategoriesResponse.build_price_categories(created_price_categories)


@blueprint.v1_offers_blueprint.route(
    "/events/<int:event_id>/price_categories/<int:price_category_id>", methods=["PATCH"]
)
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.EVENT_OFFER_PRICES_TAG],
    response_model=serialization.PriceCategoryResponse,
    resp=SpectreeResponse(
        **(
            {"HTTP_200": (serialization.PriceCategoryResponse, "The price category has been modified successfully")}
            # errors
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
            | http_responses.HTTP_400_BAD_REQUEST
            | http_responses.HTTP_404_PRICE_CATEGORY_OR_EVENT_NOT_FOUND
        )
    ),
)
@api_key_required
def patch_event_price_categories(
    event_id: int,
    price_category_id: int,
    body: serialization.PriceCategoryEdition,
) -> serialization.PriceCategoryResponse:
    """
    Update price category

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
    try:
        with repository.transaction():
            eurocent_price = update_body.get("price", offers_api.UNCHANGED)
            offers_api.edit_price_category(
                event_offer,
                price_category=price_category_to_edit,
                label=update_body.get("label", offers_api.UNCHANGED),
                price=(
                    finance_utils.to_euros(eurocent_price)
                    if eurocent_price != offers_api.UNCHANGED
                    else offers_api.UNCHANGED
                ),
                editing_provider=current_api_key.provider,
            )
    except offers_exceptions.OfferEditionBaseException as error:
        raise api_errors.ApiErrors(error.errors, status_code=400)

    return serialization.PriceCategoryResponse.from_orm(price_category_to_edit)


@blueprint.v1_offers_blueprint.route("/events/<int:event_id>/dates", methods=["POST"])
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.EVENT_OFFER_DATES_TAG],
    response_model=serialization.PostDatesResponse,
    resp=SpectreeResponse(
        **(
            {"HTTP_200": (serialization.PostDatesResponse, "The event dates have been created successfully")}
            # errors
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
            | http_responses.HTTP_400_BAD_REQUEST
            | http_responses.HTTP_404_PRICE_CATEGORY_OR_EVENT_NOT_FOUND
        )
    ),
)
@api_key_required
def post_event_dates(event_id: int, body: serialization.DatesCreation) -> serialization.PostDatesResponse:
    """
    Add dates to event

    Add a dates to given event. Each date is attached to a price category so if there are several prices categories, several dates must be added.
    **⚠️ Event must have less than 1 000 stocks** otherwise they will not be published.
    """
    offer = (
        utils.retrieve_offer_query(event_id)
        .options(sqla.orm.joinedload(offers_models.Offer.priceCategories))
        .filter(offers_models.Offer.isEvent)
        .one_or_none()
    )
    if not offer:
        raise api_errors.ApiErrors({"event_id": ["The event could not be found"]}, status_code=404)

    new_dates: list[offers_models.Stock] = []
    try:
        with repository.transaction():
            for date in body.dates:
                price_category = next((c for c in offer.priceCategories if c.id == date.price_category_id), None)
                if not price_category:
                    raise api_errors.ApiErrors(
                        {"price_category_id": ["The price category could not be found"]}, status_code=404
                    )

                new_dates.append(
                    offers_api.create_stock(
                        offer=offer,
                        price_category=price_category,
                        quantity=serialization.deserialize_quantity(date.quantity),
                        beginning_datetime=date.beginning_datetime,
                        booking_limit_datetime=date.booking_limit_datetime,
                        creating_provider=current_api_key.provider,
                        id_at_provider=date.id_at_provider,
                    )
                )
    except (offers_exceptions.OfferCreationBaseException, offers_exceptions.OfferEditionBaseException) as error:
        raise api_errors.ApiErrors(error.errors, status_code=400)

    return serialization.PostDatesResponse(
        dates=[serialization.DateResponse.build_date(new_date) for new_date in new_dates]
    )


@blueprint.v1_offers_blueprint.route("/events/<int:event_id>/dates", methods=["GET"])
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.EVENT_OFFER_DATES_TAG],
    response_model=serialization.GetDatesResponse,
    resp=SpectreeResponse(
        **(
            {"HTTP_200": (serialization.GetDatesResponse, "The event dates have been returned")}
            # errors
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
            | http_responses.HTTP_400_BAD_REQUEST
            | http_responses.HTTP_404_PRICE_CATEGORY_OR_EVENT_NOT_FOUND
        )
    ),
)
@api_key_required
def get_event_dates(event_id: int, query: serialization.GetDatesQueryParams) -> serialization.GetDatesResponse:
    """
    Get event dates

    Return all the dates linked to an event. Results are paginated (by default there are `50` date per page).
    """
    offer = utils.retrieve_offer_query(event_id).filter(offers_models.Offer.isEvent).one_or_none()
    if not offer:
        raise api_errors.ApiErrors({"event_id": ["The event could not be found"]}, status_code=404)

    stock_id_query = offers_models.Stock.query.filter(
        offers_models.Stock.offerId == offer.id,
        sqla.not_(offers_models.Stock.isSoftDeleted),
        offers_models.Stock.id >= query.firstIndex,
    ).with_entities(offers_models.Stock.id)
    total_stock_ids = [stock_id for (stock_id,) in stock_id_query.all()]

    stocks = (
        offers_models.Stock.query.filter(offers_models.Stock.id.in_(total_stock_ids))
        .options(
            sqla.orm.joinedload(offers_models.Stock.priceCategory).joinedload(
                offers_models.PriceCategory.priceCategoryLabel
            )
        )
        .order_by(offers_models.Stock.id)
        .limit(query.limit)
    )

    return serialization.GetDatesResponse(
        dates=[serialization.DateResponse.build_date(stock) for stock in stocks],
    )


@blueprint.v1_offers_blueprint.route("/events/<int:event_id>/dates/<int:date_id>", methods=["DELETE"])
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.EVENT_OFFER_DATES_TAG],
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
@api_key_required
def delete_event_date(event_id: int, date_id: int) -> None:
    """
    Delete event date

    When an event date is deleted, all cancellable bookings (i.e not used) are cancelled.
    To prevent from further bookings, you may alternatively update the date's quantity to the bookedQuantity (but not below).
    """
    offer = (
        utils.retrieve_offer_query(event_id)
        .filter(offers_models.Offer.isEvent)
        .options(sqla.orm.joinedload(offers_models.Offer.stocks))
        .one_or_none()
    )
    if not offer:
        raise api_errors.ApiErrors({"event_id": ["The event could not be found"]}, status_code=404)
    stock_to_delete = next((stock for stock in offer.stocks if stock.id == date_id and not stock.isSoftDeleted), None)
    if not stock_to_delete:
        raise api_errors.ApiErrors({"date_id": ["The date could not be found"]}, status_code=404)
    try:
        offers_api.delete_stock(stock_to_delete)
    except offers_exceptions.OfferEditionBaseException as error:
        raise api_errors.ApiErrors(error.errors, status_code=400)


@blueprint.v1_offers_blueprint.route("/events/<int:event_id>/dates/<int:date_id>", methods=["PATCH"])
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.EVENT_OFFER_DATES_TAG],
    response_model=serialization.DateResponse,
    resp=SpectreeResponse(
        **(
            {"HTTP_200": (serialization.DateResponse, "The event date has been modified successfully")}
            # errors
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
            | http_responses.HTTP_400_BAD_REQUEST
            | http_responses.HTTP_404_PRICE_CATEGORY_OR_EVENT_NOT_FOUND
        )
    ),
)
@api_key_required
def patch_event_date(
    event_id: int,
    date_id: int,
    body: serialization.DateEdition,
) -> serialization.DateResponse:
    """
    Update event date

    Update the price category and the beginning time of an event date.
    """
    offer: offers_models.Offer | None = (
        utils.retrieve_offer_relations_query(utils.retrieve_offer_query(event_id))
        .filter(offers_models.Offer.isEvent)
        .one_or_none()
    )
    if not offer:
        raise api_errors.ApiErrors({"event_id": ["The event could not be found"]}, status_code=404)

    stock_to_edit = next((stock for stock in offer.stocks if stock.id == date_id and not stock.isSoftDeleted), None)
    if not stock_to_edit:
        raise api_errors.ApiErrors({"date_id": ["No date could be found"]}, status_code=404)

    update_body = body.dict(exclude_unset=True)
    try:
        with repository.transaction():
            price_category_id = update_body.get("price_category_id", None)
            price_category = (
                next((c for c in offer.priceCategories if c.id == price_category_id), None)
                if price_category_id is not None
                else offers_api.UNCHANGED
            )
            if not price_category:
                raise api_errors.ApiErrors(
                    {"price_category_id": ["The price category could not be found"]}, status_code=404
                )

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
    except (offers_exceptions.OfferCreationBaseException, offers_exceptions.OfferEditionBaseException) as error:
        raise api_errors.ApiErrors(error.errors, status_code=400)
    except booking_exceptions.BookingIsAlreadyCancelled:
        raise api_errors.ResourceGoneError({"booking": ["Cette réservation a été annulée"]})
    except booking_exceptions.BookingIsAlreadyRefunded:
        raise api_errors.ResourceGoneError({"payment": ["Le remboursement est en cours de traitement"]})
    except booking_exceptions.BookingHasActivationCode:
        raise api_errors.ForbiddenError({"booking": ["Cette réservation ne peut pas être marquée comme inutilisée"]})
    except booking_exceptions.BookingIsNotUsed:
        raise api_errors.ResourceGoneError({"booking": ["Cette contremarque n'a pas encore été validée"]})
    # `edited_stock` could be None if nothing was changed.
    return serialization.DateResponse.build_date(edited_stock or stock_to_edit)


@blueprint.v1_offers_blueprint.route("/events/categories", methods=["GET"])
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.OFFER_ATTRIBUTES],
    response_model=serialization.GetEventCategoriesResponse,
    resp=SpectreeResponse(
        **(
            {"HTTP_200": (serialization.GetEventCategoriesResponse, "The event categories have been returned")}
            # errors
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
        )
    ),
)
@api_key_required
def get_event_categories() -> serialization.GetEventCategoriesResponse:
    """
    Get event categories

    Return all the categories available, with their conditional fields, and whether they are required.
    """
    # Individual offers API only relies on subcategories, not categories.
    # To make it simpler for the provider using this API, we only expose subcategories and call them categories.
    event_categories_response = [
        serialization.EventCategoryResponse.build_category(subcategory)
        for subcategory in subcategories.EVENT_SUBCATEGORIES.values()
        if subcategory.is_selectable
    ]
    return serialization.GetEventCategoriesResponse(__root__=event_categories_response)

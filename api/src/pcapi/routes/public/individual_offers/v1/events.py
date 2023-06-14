import copy

import flask
import sqlalchemy as sqla

from pcapi import repository
from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.finance import utils as finance_utils
from pcapi.core.offers import api as offers_api
from pcapi.core.offers import exceptions as offers_exceptions
from pcapi.core.offers import models as offers_models
from pcapi.models import api_errors
from pcapi.models import db
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils import rate_limiting
from pcapi.validation.routes.users_authentifications import api_key_required
from pcapi.validation.routes.users_authentifications import current_api_key

from . import blueprint
from . import constants
from . import serialization
from . import utils


def _deserialize_ticket_collection(
    ticket_collection: serialization.SentByEmailDetails | serialization.OnSiteCollectionDetails | None,
    subcategory_id: str,
) -> tuple[offers_models.WithdrawalTypeEnum | None, int | None]:
    if not ticket_collection:
        if subcategories.ALL_SUBCATEGORIES_DICT[subcategory_id].can_be_withdrawable:
            return offers_models.WithdrawalTypeEnum.NO_TICKET, None
        return None, None
    if isinstance(ticket_collection, serialization.SentByEmailDetails):
        return offers_models.WithdrawalTypeEnum.BY_EMAIL, ticket_collection.daysBeforeEvent * 24 * 3600
    return offers_models.WithdrawalTypeEnum.ON_SITE, ticket_collection.minutesBeforeEvent * 60


@blueprint.v1_blueprint.route("/events", methods=["POST"])
@spectree_serialize(
    api=blueprint.v1_event_schema,
    tags=[constants.EVENT_OFFER_INFO_TAG],
    response_model=serialization.EventOfferResponse,
)
@api_key_required
@rate_limiting.api_key_rate_limiter()
def post_event_offer(body: serialization.EventOfferCreation) -> serialization.EventOfferResponse:
    """
    Post an event offer.
    """
    venue = utils.retrieve_venue_from_location(body.location)
    withdrawal_type, withdrawal_delay = _deserialize_ticket_collection(
        body.ticket_collection, body.category_related_fields.subcategory_id
    )
    try:
        with repository.transaction():
            created_offer = offers_api.create_offer(
                audio_disability_compliant=body.accessibility.audio_disability_compliant,
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
                withdrawal_delay=withdrawal_delay,
                withdrawal_details=body.withdrawal_details,
                withdrawal_type=withdrawal_type,
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

    except offers_exceptions.OfferCreationBaseException as error:
        raise api_errors.ApiErrors(error.errors, status_code=400)

    return serialization.EventOfferResponse.build_event_offer(created_offer)


@blueprint.v1_blueprint.route("/events/<int:event_id>", methods=["GET"])
@spectree_serialize(
    api=blueprint.v1_event_schema,
    tags=[constants.EVENT_OFFER_INFO_TAG],
    response_model=serialization.EventOfferResponse,
)
@api_key_required
@rate_limiting.api_key_rate_limiter()
def get_event(event_id: int) -> serialization.EventOfferResponse:
    """
    Get an event offer.
    """
    offer: offers_models.Offer | None = (
        utils.retrieve_offer_relations_query(utils.retrieve_offer_query(event_id))
        .filter(offers_models.Offer.isEvent)
        .one_or_none()
    )
    if not offer:
        raise api_errors.ApiErrors({"event_id": ["The event offer could not be found"]}, status_code=404)

    return serialization.EventOfferResponse.build_event_offer(offer)


@blueprint.v1_blueprint.route("/events", methods=["GET"])
@spectree_serialize(
    api=blueprint.v1_event_schema,
    tags=[constants.EVENT_OFFER_INFO_TAG],
    response_model=serialization.EventOffersResponse,
)
@api_key_required
@rate_limiting.api_key_rate_limiter()
def get_events(query: serialization.GetOffersQueryParams) -> serialization.EventOffersResponse:
    """
    Get events. Results are paginated.
    """
    utils.check_venue_id_is_tied_to_api_key(query.venue_id)
    total_offer_ids = utils.retrieve_offer_ids(is_event=True, filtered_venue_id=query.venue_id)
    offset = query.limit * (query.page - 1)

    if offset > len(total_offer_ids):
        raise api_errors.ApiErrors(
            {
                "page": f"The page you requested does not exist. The maximum page for the specified limit is {len(total_offer_ids)//query.limit+1}"
            },
            status_code=404,
        )

    offers = (
        utils.retrieve_offer_relations_query(
            offers_models.Offer.query.filter(offers_models.Offer.id.in_(total_offer_ids[offset : offset + query.limit]))
        )
        .order_by(offers_models.Offer.id)
        .all()
    )

    return serialization.EventOffersResponse(
        events=[serialization.EventOfferResponse.build_event_offer(offer) for offer in offers],
        pagination=serialization.Pagination.build_pagination(
            flask.url_for(".get_events", _external=True),
            query.page,
            len(offers),
            len(total_offer_ids),
            query.limit,
            query.venue_id,
        ),
    )


@blueprint.v1_blueprint.route("/events/<int:event_id>", methods=["PATCH"])
@spectree_serialize(
    api=blueprint.v1_event_schema,
    tags=[constants.EVENT_OFFER_INFO_TAG],
    response_model=serialization.EventOfferResponse,
)
@api_key_required
@rate_limiting.api_key_rate_limiter()
def edit_event(event_id: int, body: serialization.EventOfferEdition) -> serialization.EventOfferResponse:
    """
    Edit a event offer.

    Leave fields undefined to keep their current value.
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

    withdrawal_type, withdrawal_delay = (
        _deserialize_ticket_collection(body.ticket_collection, offer.subcategoryId)
        if update_body.get("ticket_collection")
        else (offers_api.UNCHANGED, offers_api.UNCHANGED)
    )

    try:
        with repository.transaction():
            offer = offers_api.update_offer(
                offer,
                bookingEmail=update_body.get("booking_email", offers_api.UNCHANGED),
                durationMinutes=update_body.get("duration_minutes", offers_api.UNCHANGED),
                extraData=serialization.deserialize_extra_data(
                    body.category_related_fields, copy.deepcopy(offer.extraData)
                )
                if body.category_related_fields
                else offers_api.UNCHANGED,
                isActive=update_body.get("is_active", offers_api.UNCHANGED),
                isDuo=update_body.get("is_duo", offers_api.UNCHANGED),
                withdrawalDetails=update_body.get("withdrawal_details", offers_api.UNCHANGED),
                withdrawalType=withdrawal_type,
                withdrawalDelay=withdrawal_delay,
                **utils.compute_accessibility_edition_fields(update_body.get("accessibility")),
            )
    except offers_exceptions.OfferCreationBaseException as error:
        raise api_errors.ApiErrors(error.errors, status_code=400)

    return serialization.EventOfferResponse.build_event_offer(offer)


@blueprint.v1_blueprint.route("/events/<int:event_id>/price_categories", methods=["POST"])
@spectree_serialize(
    api=blueprint.v1_event_schema,
    tags=[constants.EVENT_OFFER_PRICES_TAG],
    response_model=serialization.PriceCategoriesResponse,
)
@api_key_required
@rate_limiting.api_key_rate_limiter()
def post_event_price_categories(
    event_id: int, body: serialization.PriceCategoriesCreation
) -> serialization.PriceCategoriesResponse:
    """
    Post price categories.
    """
    offer = utils.retrieve_offer_query(event_id).filter(offers_models.Offer.isEvent).one_or_none()
    if not offer:
        raise api_errors.ApiErrors({"event_id": ["The event could not be found"]}, status_code=404)

    created_price_categories: list[offers_models.PriceCategory] = []
    with repository.transaction():
        for price_category in body.price_categories:
            euro_price = finance_utils.to_euros(price_category.price)
            created_price_categories.append(offers_api.create_price_category(offer, price_category.label, euro_price))

    return serialization.PriceCategoriesResponse.build_price_categories(created_price_categories)


@blueprint.v1_blueprint.route("/events/<int:event_id>/price_categories/<int:price_category_id>", methods=["PATCH"])
@spectree_serialize(
    api=blueprint.v1_event_schema,
    tags=[constants.EVENT_OFFER_PRICES_TAG],
    response_model=serialization.PriceCategoryResponse,
)
@api_key_required
@rate_limiting.api_key_rate_limiter()
def patch_event_price_categories(
    event_id: int,
    price_category_id: int,
    body: serialization.PriceCategoryEdition,
) -> serialization.PriceCategoryResponse:
    """
    Patch price categories.
    """
    event_offer = (
        utils.retrieve_offer_query(event_id)
        .filter(offers_models.Offer.isEvent)
        .outerjoin(offers_models.Offer.stocks.and_(sqla.not_(offers_models.Stock.isEventExpired)))
        .options(sqla.orm.contains_eager(offers_models.Offer.stocks))
        .options(
            sqla.orm.joinedload(offers_models.Offer.priceCategories).joinedload(
                offers_models.PriceCategory.priceCategoryLabel
            )
        )
        .one_or_none()
    )
    if not event_offer:
        raise api_errors.ApiErrors({"event_id": ["The event could not be found"]}, status_code=404)

    price_category_to_edit = next(
        (price_category for price_category in event_offer.priceCategories if price_category.id == price_category_id)
    )
    if not price_category_to_edit:
        raise api_errors.ApiErrors({"price_category_id": ["No price category could be found"]}, status_code=404)

    update_body = body.dict(exclude_unset=True)
    with repository.transaction():
        eurocent_price = update_body.get("price", offers_api.UNCHANGED)
        offers_api.edit_price_category(
            event_offer,
            price_category=price_category_to_edit,
            label=update_body.get("label", offers_api.UNCHANGED),
            price=finance_utils.to_euros(eurocent_price)
            if eurocent_price != offers_api.UNCHANGED
            else offers_api.UNCHANGED,
            editing_provider=current_api_key.provider,
        )

    return serialization.PriceCategoryResponse.from_orm(price_category_to_edit)


@blueprint.v1_blueprint.route("/events/<int:event_id>/dates", methods=["POST"])
@spectree_serialize(
    api=blueprint.v1_event_schema,
    tags=[constants.EVENT_OFFER_DATES_TAG],
    response_model=serialization.PostDatesResponse,
)
@api_key_required
@rate_limiting.api_key_rate_limiter()
def post_event_dates(event_id: int, body: serialization.DatesCreation) -> serialization.PostDatesResponse:
    """
    Add dates to an event offer.
    Each date is attached to a price category so if there are several prices categories, several dates must be added.
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
                    )
                )
    except offers_exceptions.OfferCreationBaseException as error:
        raise api_errors.ApiErrors(error.errors, status_code=400)

    return serialization.PostDatesResponse(
        dates=[serialization.DateResponse.build_date(new_date) for new_date in new_dates]
    )


@blueprint.v1_blueprint.route("/events/<int:event_id>/dates", methods=["GET"])
@spectree_serialize(
    api=blueprint.v1_event_schema, tags=[constants.EVENT_OFFER_DATES_TAG], response_model=serialization.GetDatesResponse
)
@api_key_required
@rate_limiting.api_key_rate_limiter()
def get_event_dates(event_id: int, query: serialization.GetDatesQueryParams) -> serialization.GetDatesResponse:
    """
    Get dates of an event. Results are paginated.
    """
    offer = utils.retrieve_offer_query(event_id).filter(offers_models.Offer.isEvent).one_or_none()
    if not offer:
        raise api_errors.ApiErrors({"event_id": ["The event could not be found"]}, status_code=404)

    stock_id_query = offers_models.Stock.query.filter(
        offers_models.Stock.offerId == offer.id,
        sqla.not_(offers_models.Stock.isSoftDeleted),
    ).with_entities(offers_models.Stock.id)
    total_stock_ids = [stock_id for (stock_id,) in stock_id_query.all()]

    offset = query.limit * (query.page - 1)
    if offset > len(total_stock_ids):
        raise api_errors.ApiErrors(
            {
                "page": f"The page you requested does not exist. The maximum page for the specified limit is {len(total_stock_ids)//query.limit+1}"
            },
            status_code=404,
        )

    stocks = (
        offers_models.Stock.query.filter(offers_models.Stock.id.in_(total_stock_ids[offset : offset + query.limit]))
        .options(
            sqla.orm.joinedload(offers_models.Stock.priceCategory).joinedload(
                offers_models.PriceCategory.priceCategoryLabel
            )
        )
        .order_by(offers_models.Stock.id)
        .all()
    )

    return serialization.GetDatesResponse(
        dates=[serialization.DateResponse.build_date(stock) for stock in stocks],
        pagination=serialization.Pagination.build_pagination(
            flask.url_for(".get_event_dates", event_id=event_id, _external=True),
            query.page,
            len(stocks),
            len(total_stock_ids),
            query.limit,
        ),
    )


@blueprint.v1_blueprint.route("/events/<int:event_id>/dates/<int:date_id>", methods=["DELETE"])
@spectree_serialize(api=blueprint.v1_event_schema, tags=[constants.EVENT_OFFER_DATES_TAG], on_success_status=204)
@api_key_required
@rate_limiting.api_key_rate_limiter()
def delete_event_date(event_id: int, date_id: int) -> None:
    """
    Delete an event date.

    All cancellable bookings (i.e not used) will be cancelled. To prevent from further bookings, you may alternatively update the date's quantity to the bookedQuantity (but not below).
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

    offers_api.delete_stock(stock_to_delete)


@blueprint.v1_blueprint.route("/events/<int:event_id>/dates/<int:date_id>", methods=["PATCH"])
@spectree_serialize(
    api=blueprint.v1_event_schema, tags=[constants.EVENT_OFFER_DATES_TAG], response_model=serialization.DateResponse
)
@api_key_required
@rate_limiting.api_key_rate_limiter()
def patch_event_date(
    event_id: int,
    date_id: int,
    body: serialization.DateEdition,
) -> serialization.DateResponse:
    """
    Patch an event date.
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

            quantity = update_body.get("quantity", offers_api.UNCHANGED)
            edited_date, _ = offers_api.edit_stock(
                stock_to_edit,
                quantity=serialization.deserialize_quantity(quantity),
                price_category=price_category,
                booking_limit_datetime=update_body.get("booking_limit_datetime", offers_api.UNCHANGED),
                beginning_datetime=update_body.get("beginning_datetime", offers_api.UNCHANGED),
                editing_provider=current_api_key.provider,
            )
    except offers_exceptions.OfferCreationBaseException as error:
        raise api_errors.ApiErrors(error.errors, status_code=400)
    return serialization.DateResponse.build_date(edited_date)

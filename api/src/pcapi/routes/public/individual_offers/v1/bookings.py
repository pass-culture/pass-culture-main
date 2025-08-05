from datetime import datetime

import sqlalchemy.orm as sa_orm

from pcapi.core.achievements import models as achievements_models
from pcapi.core.bookings import api as bookings_api
from pcapi.core.bookings import exceptions
from pcapi.core.bookings import models as booking_models
from pcapi.core.bookings import validation as bookings_validation
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.core.providers import models as providers_models
from pcapi.core.users import models as users_models
from pcapi.models import api_errors
from pcapi.models import db
from pcapi.routes.public import blueprints
from pcapi.routes.public import spectree_schemas
from pcapi.routes.public.documentation_constants import http_responses
from pcapi.routes.public.documentation_constants import tags
from pcapi.serialization.decorator import spectree_serialize
from pcapi.serialization.spec_tree import ExtendResponse as SpectreeResponse
from pcapi.utils.transaction_manager import atomic
from pcapi.validation.routes.users_authentifications import current_api_key
from pcapi.validation.routes.users_authentifications import provider_api_key_required

from . import bookings_serialization as serialization


def _get_base_booking_query() -> sa_orm.Query:
    return (
        db.session.query(booking_models.Booking)
        .join(offerers_models.Venue)
        .join(offerers_models.Venue.managingOfferer)
        .join(providers_models.VenueProvider)
        .filter(providers_models.VenueProvider.providerId == current_api_key.providerId)
        .filter(providers_models.VenueProvider.isActive == True)
        .join(offers_models.Stock)
        .join(offers_models.Offer)
        .options(
            sa_orm.contains_eager(booking_models.Booking.venue)
            .load_only(
                offerers_models.Venue.id,
                offerers_models.Venue.name,
            )
            .options(
                sa_orm.contains_eager(offerers_models.Venue.managingOfferer).load_only(
                    offerers_models.Offerer.validationStatus
                ),
            )
        )
        .options(
            sa_orm.contains_eager(booking_models.Booking.stock)
            .load_only(
                offers_models.Stock.id, offers_models.Stock.beginningDatetime, offers_models.Stock.priceCategoryId
            )
            .contains_eager(offers_models.Stock.offer)
            .load_only(
                offers_models.Offer.id,
                offers_models.Offer.name,
                offers_models.Offer.ean,
                offers_models.Offer._extraData,
                offers_models.Offer.subcategoryId,
            )
            .joinedload(offers_models.Offer.offererAddress)
            .joinedload(offerers_models.OffererAddress.address)
        )
    )


def _get_paginated_and_filtered_bookings(
    offer_id: int,
    *,
    price_category_id: int | None,
    stock_id: int | None,
    status: booking_models.BookingStatus | None,
    beginning_datetime: datetime | None,
    firstIndex: int,
    limit: int,
) -> sa_orm.Query:
    bookings_query = _get_base_booking_query().filter(offers_models.Offer.id == offer_id)

    if price_category_id:
        bookings_query = bookings_query.join(offers_models.PriceCategory).filter(
            offers_models.PriceCategory.id == price_category_id
        )

    if stock_id:
        bookings_query = bookings_query.filter(booking_models.Booking.stockId == stock_id)

    if status:
        bookings_query = bookings_query.filter(booking_models.Booking.status == status)

    if beginning_datetime:
        bookings_query = bookings_query.filter(offers_models.Stock.beginningDatetime == beginning_datetime)

    return (
        bookings_query.filter(booking_models.Booking.id >= firstIndex).order_by(booking_models.Booking.id).limit(limit)
    )


@blueprints.public_api.route("/public/bookings/v1/bookings", methods=["GET"])
@atomic()
@provider_api_key_required
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    response_model=serialization.GetFilteredBookingsResponse,
    tags=[tags.BOOKINGS],
    resp=SpectreeResponse(
        **(
            {"HTTP_200": (serialization.GetFilteredBookingsResponse, http_responses.HTTP_200_MESSAGE)}
            # errors
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
            | http_responses.HTTP_404_OFFER_NOT_FOUND
        ),
    ),
)
def get_bookings_by_offer(
    query: serialization.GetFilteredBookingsRequest,
) -> serialization.GetFilteredBookingsResponse:
    """
    Get Offer Bookings

    Return all the bookings for a given offer. Results are paginated (by default, there are `50` bookings per page)
    """
    offer = (
        db.session.query(offers_models.Offer)
        .filter(offers_models.Offer.id == query.offer_id)
        .join(offerers_models.Venue)
        .join(providers_models.VenueProvider)
        .filter(providers_models.VenueProvider.providerId == current_api_key.providerId)
        .filter(providers_models.VenueProvider.isActive == True)
        .one_or_none()
    )

    if offer is None:
        raise api_errors.ResourceNotFoundError({"offer": "we could not find this offer id"})

    bookings = _get_paginated_and_filtered_bookings(
        query.offer_id,
        price_category_id=query.price_category_id,
        stock_id=query.stock_id,
        status=query.status,
        beginning_datetime=query.beginning_datetime,
        firstIndex=query.firstIndex,
        limit=query.limit,
    )

    return serialization.GetFilteredBookingsResponse(
        bookings=[serialization.GetBookingResponse.build_booking(booking) for booking in bookings]
    )


def _get_booking_by_token_query(token: str) -> sa_orm.Query:
    return _get_base_booking_query().filter(booking_models.Booking.token == token.upper())


def _get_booking_by_token(token: str) -> booking_models.Booking | None:
    return _get_booking_by_token_query(token).one_or_none()


@blueprints.public_api.route("/public/bookings/v1/token/<string:token>", methods=["GET"])
@atomic()
@provider_api_key_required
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    response_model=serialization.GetBookingResponse,
    tags=[tags.BOOKINGS],
    resp=SpectreeResponse(
        **(
            {"HTTP_200": (serialization.GetBookingResponse, "The booking has been found successfully")}
            # errors
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
            | http_responses.HTTP_403_BOOKING_REIMBURSED_OR_CONFIRMED_OR_NOT_USED
            | http_responses.HTTP_404_BOOKING_NOT_FOUND
            | http_responses.HTTP_410_BOOKING_CANCELED_OR_VALIDATED
        )
    ),
)
def get_booking_by_token(token: str) -> serialization.GetBookingResponse:
    """
    Get Booking

    The countermark or token code is a character string that identifies the reservation and serves as proof of booking.
    This unique code is generated for each user's booking on the application and is transmitted to them on that occasion.
    """
    booking = _get_booking_by_token(token)
    if booking is None:
        raise api_errors.ResourceNotFoundError({"global": "This countermark cannot be found"})

    try:
        bookings_validation.check_is_usable(booking)
    except exceptions.BookingIsAlreadyRefunded:
        raise api_errors.ForbiddenError({"payment": "This booking has already been reimbursed"})
    except exceptions.BookingIsAlreadyUsed:
        raise api_errors.ResourceGoneError({"booking": "This booking has already been validated"})
    except exceptions.BookingIsAlreadyCancelled:
        raise api_errors.ResourceGoneError({"booking": "This booking has been cancelled"})
    except exceptions.BookingIsNotConfirmed as exc:
        raise api_errors.ForbiddenError(errors={"booking": str(exc)})

    return serialization.GetBookingResponse.build_booking(booking)


@blueprints.public_api.route("/public/bookings/v1/use/token/<token>", methods=["PATCH"])
@atomic()
@provider_api_key_required
@spectree_serialize(
    on_success_status=204,
    api=spectree_schemas.public_api_schema,
    tags=[tags.BOOKINGS],
    resp=SpectreeResponse(
        **(
            http_responses.HTTP_204_BOOKING_VALIDATION_SUCCESS
            # errors
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
            | http_responses.HTTP_403_BOOKING_REIMBURSED_OR_CONFIRMED_OR_NOT_USED
            | http_responses.HTTP_404_BOOKING_NOT_FOUND
            | http_responses.HTTP_410_BOOKING_CANCELED_OR_VALIDATED
        )
    ),
)
def validate_booking_by_token(token: str) -> None:
    """
    Validate Booking

    Confirm that the booking has been used by the beneficiary.
    """
    booking = (
        _get_booking_by_token_query(token)
        .options(
            sa_orm.joinedload(booking_models.Booking.user)
            .selectinload(users_models.User.achievements)
            .load_only(achievements_models.Achievement.name)
        )
        .one_or_none()
    )
    if booking is None:
        raise api_errors.ResourceNotFoundError({"global": "This countermark cannot be found"})

    try:
        bookings_api.mark_as_used(booking, booking_models.BookingValidationAuthorType.OFFERER)
    except exceptions.BookingIsAlreadyRefunded:
        raise api_errors.ForbiddenError({"payment": "This booking has already been reimbursed"})
    except exceptions.BookingIsAlreadyUsed:
        raise api_errors.ResourceGoneError({"booking": "This booking has already been validated"})
    except exceptions.BookingIsAlreadyCancelled:
        raise api_errors.ResourceGoneError({"booking": "This booking has been cancelled"})
    except exceptions.BookingIsNotConfirmed as exc:
        raise api_errors.ForbiddenError({"booking": str(exc)})


@blueprints.public_api.route("/public/bookings/v1/keep/token/<token>", methods=["PATCH"])
@atomic()
@provider_api_key_required
@spectree_serialize(
    on_success_status=204,
    api=spectree_schemas.public_api_schema,
    tags=[tags.BOOKINGS],
    resp=SpectreeResponse(
        **(
            http_responses.HTTP_204_BOOKING_VALIDATION_CANCELLATION_SUCCESS
            # errors
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
            | http_responses.HTTP_403_BOOKING_REIMBURSED_OR_CONFIRMED_OR_NOT_USED
            | http_responses.HTTP_404_BOOKING_NOT_FOUND
            | http_responses.HTTP_410_BOOKING_CANCELED_OR_VALIDATED
        )
    ),
)
def cancel_booking_validation_by_token(token: str) -> None:
    """
    Revert Booking Validation

    This operation reverses the status of a booking from `USED` back to `CONFIRMED`.
    As a result, the pass Culture application will treat the booking as if the beneficiary has not retrieved it,
    and the cultural partner will not receive a refund.

    **⚠️ Warning:**
    Before using this endpoint, **ensure that the cultural partner has manually confirmed their desire to revert the booking validation**.
    Failure to do so may result in the cultural partner expecting a refund that will not be issued, due to the booking validation being reverted without their knowledge.
    """
    booking = _get_booking_by_token(token)
    if booking is None:
        raise api_errors.ResourceNotFoundError({"global": "This countermark cannot be found"})

    try:
        bookings_api.mark_as_unused(booking)
    except exceptions.BookingIsAlreadyRefunded:
        raise api_errors.ForbiddenError({"payment": "This booking has been reimbursed"})
    except exceptions.BookingIsNotUsed:
        raise api_errors.ForbiddenError({"booking": "This booking has not been used"})
    except exceptions.BookingIsAlreadyCancelled:
        raise api_errors.ResourceGoneError({"booking": "This booking has been cancelled"})
    except exceptions.BookingHasActivationCode:
        raise api_errors.ForbiddenError(
            {"booking": "This booking has validation codes, and cannot be marked as unused"}
        )


@blueprints.public_api.route("/public/bookings/v1/cancel/token/<token>", methods=["PATCH"])
@atomic()
@provider_api_key_required
@spectree_serialize(
    on_success_status=204,
    api=spectree_schemas.public_api_schema,
    tags=[tags.BOOKINGS],
    resp=SpectreeResponse(
        **(
            http_responses.HTTP_204_BOOKING_CANCELLATION_SUCCESS
            # errors
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
            | http_responses.HTTP_400_BAD_REQUEST
            | http_responses.HTTP_403_BOOKING_REIMBURSED_OR_CONFIRMED_OR_NOT_USED
            | http_responses.HTTP_404_BOOKING_NOT_FOUND
            | http_responses.HTTP_410_BOOKING_CANCELED_OR_VALIDATED
        )
    ),
)
def cancel_booking_by_token(token: str) -> None:
    """
    Delete Booking

    Delete a booking that has not been used or refunded. For events, a booking can only be deleted if it is in a pending state.

    **⚠️ Warning:**
    This operation is irreversible. Once a booking is deleted, the beneficiary cannot retrieve it and will need to create a new booking. **Use this endpoint only if you are certain that the order cannot be fulfilled.**
    """
    booking = _get_booking_by_token(token)
    if booking is None:
        raise api_errors.ResourceNotFoundError({"global": "This countermark cannot be found"})

    try:
        bookings_validation.check_booking_can_be_cancelled(booking)
        if booking.stock.offer.isEvent:
            bookings_validation.check_booking_cancellation_limit_date(booking)
    except exceptions.BookingIsAlreadyRefunded:
        raise api_errors.ForbiddenError({"payment": "This booking has been reimbursed"})
    except exceptions.BookingIsAlreadyUsed:
        raise api_errors.ResourceGoneError({"booking": "This booking has been validated"})
    except exceptions.BookingIsAlreadyCancelled:
        raise api_errors.ResourceGoneError({"booking": "This booking has already been cancelled"})
    except exceptions.BookingIsNotConfirmed as exc:
        raise api_errors.ForbiddenError({"booking": str(exc)})
    except exceptions.CannotCancelConfirmedBooking:
        raise api_errors.ForbiddenError({"booking": "This booking cannot be cancelled anymore"})

    bookings_api.cancel_booking_by_offerer(booking)

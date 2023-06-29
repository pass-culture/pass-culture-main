import flask
from sqlalchemy import orm as sqla_orm

from pcapi.core.bookings import api as bookings_api
from pcapi.core.bookings import exceptions
from pcapi.core.bookings import models as booking_models
from pcapi.core.bookings import validation as bookings_validation
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.core.providers import models as providers_models
from pcapi.models import api_errors
from pcapi.routes.public.individual_offers.v1 import constants
from pcapi.serialization.decorator import spectree_serialize
from pcapi.validation.routes.users_authentifications import api_key_required
from pcapi.validation.routes.users_authentifications import current_api_key

from . import blueprint
from . import bookings_serialization as serialization


def _get_bookings_query(offer_id: int) -> sqla_orm.Query:
    return (
        booking_models.Booking.query.join(offerers_models.Venue)
        .join(providers_models.VenueProvider)
        .filter(providers_models.VenueProvider.providerId == current_api_key.providerId)
        .filter(providers_models.VenueProvider.isActive == True)
        .join(offers_models.Stock)
        .join(offers_models.Offer)
        .filter(offers_models.Offer.id == offer_id)
        .order_by(booking_models.Booking.dateCreated.desc())
    )


@blueprint.v1_bookings_blueprint.route("/bookings", methods=["GET"])
@spectree_serialize(
    api=blueprint.v1_bookings_schema,
    response_model=serialization.GetFilteredBookingsResponse,
    tags=[constants.BOOKING_TAG],
)
@api_key_required
def get_bookings_by_offer(
    query: serialization.GetFilteredBookingsRequest,
) -> serialization.GetFilteredBookingsResponse:
    """
    Get paginated bookings for a given offer.
    """

    bookings_count = _get_bookings_query(query.offer_id).count()
    offset = query.limit * (query.page - 1)

    if offset > bookings_count:
        raise api_errors.ApiErrors(
            {
                "page": f"The page you requested does not exist. The maximum page for the specified limit is {bookings_count//query.limit+1}"
            },
            status_code=404,
        )

    bookings = _get_bookings_query(query.offer_id).offset(offset).limit(query.limit).all()

    return serialization.GetFilteredBookingsResponse(
        bookings=[serialization.GetBookingResponse.build_booking(booking) for booking in bookings],
        pagination=serialization.Pagination.build_pagination(
            flask.url_for(".get_bookings_by_offer", _external=True),
            query.page,
            len(bookings),
            bookings_count,
            query.limit,
        ),
    )


def _get_booking_by_token(token: str) -> booking_models.Booking:
    return (
        booking_models.Booking.query.filter_by(token=token.upper())
        .join(offerers_models.Venue)
        .join(providers_models.VenueProvider)
        .filter(providers_models.VenueProvider.providerId == current_api_key.providerId)
        .filter(providers_models.VenueProvider.isActive == True)
        .join(offers_models.Stock)
        .join(offers_models.Offer)
        .one_or_none()
    )


@blueprint.v1_bookings_blueprint.route("/token/<string:token>", methods=["GET"])
@spectree_serialize(
    api=blueprint.v1_bookings_schema, response_model=serialization.GetBookingResponse, tags=[constants.BOOKING_TAG]
)
@api_key_required
def get_booking_by_token(token: str) -> serialization.GetBookingResponse:
    """
    Consultation of a booking.

    The countermark or token code is a character string that identifies the reservation and serves as proof of booking.
    This unique code is generated for each user's booking on the application and is transmitted to them on that occasion.
    """
    booking = _get_booking_by_token(token)
    if booking is None:
        raise api_errors.ApiErrors(errors={"global": "This countermark cannot be found"}, status_code=404)

    try:
        bookings_validation.check_is_usable(booking)
    except exceptions.BookingIsAlreadyRefunded:
        raise api_errors.ApiErrors(errors={"payment": "This booking has already been reimbursed"}, status_code=403)
    except exceptions.BookingIsAlreadyUsed:
        raise api_errors.ApiErrors(errors={"booking": "This booking has already been validated"}, status_code=410)
    except exceptions.BookingIsAlreadyCancelled:
        raise api_errors.ApiErrors(errors={"booking": "This booking has been canceled"}, status_code=410)
    except exceptions.BookingIsNotConfirmed as exc:
        raise api_errors.ApiErrors(errors={"booking": str(exc)}, status_code=403)

    return serialization.GetBookingResponse.build_booking(booking)


@blueprint.v1_bookings_blueprint.route("/use/token/<token>", methods=["PATCH"])
@spectree_serialize(on_success_status=204, api=blueprint.v1_bookings_schema, tags=[constants.BOOKING_TAG])
@api_key_required
def validate_booking_by_token(token: str) -> None:
    """
    Validation of a booking.

    To confirm that the booking has been successfully used by the beneficiary.
    """
    booking = _get_booking_by_token(token)
    if booking is None:
        raise api_errors.ApiErrors(errors={"global": "This countermark cannot be found"}, status_code=404)

    try:
        bookings_validation.check_is_usable(booking)
    except exceptions.BookingIsAlreadyRefunded:
        raise api_errors.ApiErrors(errors={"payment": "This booking has already been reimbursed"}, status_code=403)
    except exceptions.BookingIsAlreadyUsed:
        raise api_errors.ApiErrors(errors={"booking": "This booking has already been validated"}, status_code=410)
    except exceptions.BookingIsAlreadyCancelled:
        raise api_errors.ApiErrors(errors={"booking": "This booking has been canceled"}, status_code=410)
    except exceptions.BookingIsNotConfirmed as exc:
        raise api_errors.ApiErrors(errors={"booking": str(exc)}, status_code=403)

    bookings_api.mark_as_used(booking)


@blueprint.v1_bookings_blueprint.route("/cancel/token/<token>", methods=["PATCH"])
@spectree_serialize(on_success_status=204, api=blueprint.v1_bookings_schema, tags=[constants.BOOKING_TAG])
@api_key_required
def cancel_booking_by_token(token: str) -> None:
    """
    Cancel a booking.

    To cancel a booking that has not been refunded.
    For events, the booking can be canceled until 48 hours before the event.
    """
    booking = _get_booking_by_token(token)
    if booking is None:
        raise api_errors.ApiErrors(errors={"global": "This countermark cannot be found"}, status_code=404)

    try:
        bookings_validation.check_booking_can_be_cancelled(booking)
        if booking.stock.offer.isEvent:
            bookings_validation.check_booking_cancellation_limit_date(booking)
    except exceptions.BookingIsAlreadyRefunded:
        raise api_errors.ApiErrors(errors={"payment": "This booking has been reimbursed"}, status_code=403)
    except exceptions.BookingIsAlreadyUsed:
        raise api_errors.ApiErrors(errors={"booking": "This booking has been validated"}, status_code=410)
    except exceptions.BookingIsAlreadyCancelled:
        raise api_errors.ApiErrors(errors={"booking": "This booking has already been canceled"}, status_code=410)
    except exceptions.BookingIsNotConfirmed as exc:
        raise api_errors.ApiErrors(errors={"booking": str(exc)}, status_code=403)
    except exceptions.CannotCancelConfirmedBooking:
        raise api_errors.ApiErrors(errors={"booking": "This booking cannot be canceled anymore"}, status_code=403)

    bookings_api.cancel_booking_by_offerer(booking)

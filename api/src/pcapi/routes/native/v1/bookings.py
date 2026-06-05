import logging

import sqlalchemy.orm as sa_orm
from flask_login import current_user

import pcapi.core.bookings.api as bookings_api
import pcapi.core.bookings.exceptions as bookings_exceptions
from pcapi.core.bookings.models import Booking
from pcapi.core.external_bookings import exceptions as external_bookings_exceptions
from pcapi.core.offers.exceptions import UnexpectedCinemaProvider
from pcapi.core.offers.models import Stock
from pcapi.core.providers.exceptions import InactiveProvider
from pcapi.models import db
from pcapi.models.api_errors import ApiErrors
from pcapi.models.utils import first_or_404
from pcapi.routes.native.security import authenticated_and_active_user_required
from pcapi.routes.native.v1.serialization.bookings import BookOfferRequest
from pcapi.routes.native.v1.serialization.bookings import BookOfferResponse
from pcapi.routes.native.v1.serialization.bookings import BookingDisplayStatusRequest
from pcapi.routes.native.v1.serialization.bookings import BookingReponse
from pcapi.routes.native.v1.serialization.bookings import BookingsResponse
from pcapi.serialization.decorator import spectree_serialize

from .. import blueprint


logger = logging.getLogger(__name__)

_BOOKING_EXCEPTION_TO_CODE_MAPPING: dict[type[Exception], tuple[str, str]] = {
    # credit exceptions
    bookings_exceptions.UserHasInsufficientFunds: ("INSUFFICIENT_CREDIT", "insufficient credit"),
    bookings_exceptions.DigitalExpenseLimitHasBeenReached: ("INSUFFICIENT_CREDIT", "insufficient credit"),
    bookings_exceptions.PhysicalExpenseLimitHasBeenReached: ("INSUFFICIENT_CREDIT", "insufficient credit"),
    # offer exceptions
    bookings_exceptions.OfferIsAlreadyBooked: ("ALREADY_BOOKED", "offer already booked"),
    bookings_exceptions.OfferCategoryNotBookableByUser: (
        "OFFER_CATEGORY_NOT_BOOKABLE_BY_USER",
        "category is not bookable by user",
    ),
    # stock exception
    bookings_exceptions.StockIsNotBookable: ("STOCK_NOT_BOOKABLE", "stock is not bookable"),
    # provider exceptions
    UnexpectedCinemaProvider: (
        "CINEMA_PROVIDER_ERROR",
        "cinema provider for the venue does not match the offer provider",
    ),
    InactiveProvider: ("CINEMA_PROVIDER_INACTIVE", "cinema provider is inactive"),
    external_bookings_exceptions.TimeoutException: ("PROVIDER_BOOKING_TIMEOUT", "request to provider timeout"),
    external_bookings_exceptions.ShowSoldOutException: ("PROVIDER_STOCK_NOT_ENOUGH_SEATS", "event show is sold out"),
    external_bookings_exceptions.ShowRemovedException: ("PROVIDER_SHOW_DOES_NOT_EXIST", "event show has been removed"),
    external_bookings_exceptions.ExternalBookingException: (
        "PROVIDER_BOOKING_FAILED",
        "booking external ticket failed",
    ),
}

_EXPECTED_BOOKING_EXCEPTIONS = tuple(_BOOKING_EXCEPTION_TO_CODE_MAPPING.keys())


@blueprint.native_route("/bookings", methods=["POST"])
@spectree_serialize(api=blueprint.api, response_model=BookOfferResponse, on_error_statuses=[400])
@authenticated_and_active_user_required
def book_offer(body: BookOfferRequest) -> BookOfferResponse:
    stock = db.session.get(Stock, body.stock_id)
    if not stock:
        logger.info(
            "Could not book offer: stock does not exist",
            extra={"stock_id": body.stock_id, "user_id": current_user.id},
        )
        raise ApiErrors({"stock": "stock introuvable"}, status_code=400)

    try:
        booking = bookings_api.book_offer(
            beneficiary=current_user,
            stock_id=body.stock_id,
            quantity=body.quantity,
        )
        logger.info(
            "Offer successfully booked",
            extra={
                "stock_id": stock.id,
                "offer_id": stock.offer.id,
                "venue_id": stock.offer.venueId,
                "provider_id": stock.offer.lastProviderId,
                "user_id": current_user.id,
                "booking_quantity": booking.quantity,
            },
            technical_message_id="native.bookings.book",
        )
        return BookOfferResponse(booking_id=booking.id)
    except _EXPECTED_BOOKING_EXCEPTIONS as e:
        code, log_message = _BOOKING_EXCEPTION_TO_CODE_MAPPING.get(e.__class__, ("BOOKING FAILED", "booking failed"))
        logger.warning(
            "Could not book offer: %s",
            log_message,
            extra={
                "stock_id": stock.id,
                "offer_id": stock.offer.id,
                "venue_id": stock.offer.venueId,
                "provider_id": stock.offer.lastProviderId,
                "user_id": current_user.id,
                "exception_class": e.__class__.__name__,
                "exception_message": str(e),
            },
            technical_message_id="native.bookings.book",
        )
        raise ApiErrors({"code": code})


@blueprint.native_route("/bookings", methods=["GET"])
@spectree_serialize(api=blueprint.api, response_model=BookingsResponse)
@authenticated_and_active_user_required
def get_bookings() -> BookingsResponse:
    individual_bookings = bookings_api.get_individual_bookings(current_user)
    ended_bookings, ongoing_bookings = bookings_api.classify_and_sort_bookings(individual_bookings)

    return BookingsResponse(
        ended_bookings=[BookingReponse.build(booking) for booking in ended_bookings],
        ongoing_bookings=[BookingReponse.build(booking) for booking in ongoing_bookings],
        hasBookingsAfter18=any(
            booking for booking in individual_bookings if bookings_api.is_booking_by_18_user(booking)
        ),
    )


_CANCELLATION_EXCEPTION_TO_CODE_MAPPING: dict[type[Exception], tuple[str, str]] = {
    bookings_exceptions.BookingIsAlreadyUsed: ("ALREADY_USED", "La réservation a déjà été utilisée."),
    bookings_exceptions.CannotCancelConfirmedBooking: (
        "CONFIRMED_BOOKING",
        "La date limite d'annulation est dépassée.",
    ),
    # provider exceptions
    UnexpectedCinemaProvider: ("FAILED_TO_CANCEL_EXTERNAL_BOOKING", "L'annulation de réservation a échoué."),
    InactiveProvider: ("FAILED_TO_CANCEL_EXTERNAL_BOOKING", "L'annulation de réservation a échoué."),
    external_bookings_exceptions.ExternalBookingException: (
        "FAILED_TO_CANCEL_EXTERNAL_BOOKING",
        "L'annulation de réservation a échoué.",
    ),
}

_EXPECTED_CANCELLATION_EXCEPTION = tuple(_CANCELLATION_EXCEPTION_TO_CODE_MAPPING)


@blueprint.native_route("/bookings/<int:booking_id>/cancel", methods=["POST"])
@spectree_serialize(api=blueprint.api, on_success_status=204, on_error_statuses=[400, 404])
@authenticated_and_active_user_required
def cancel_booking(booking_id: int) -> None:
    booking = first_or_404(
        db.session.query(Booking)
        .options(sa_orm.joinedload(Booking.stock).joinedload(Stock.offer))
        .filter(Booking.id == booking_id, Booking.userId == current_user.id)
    )
    try:
        bookings_api.cancel_booking_by_beneficiary(booking)
    except bookings_exceptions.BookingIsAlreadyCancelled:
        # Do not raise an error, to avoid showing an error in case double-click => double call
        # Booking is cancelled so a success status is ok
        return
    except _EXPECTED_CANCELLATION_EXCEPTION as e:
        logger.warning(
            "Booking cancellation failed",
            extra={
                "stock_id": booking.stock.id,
                "offer_id": booking.stock.offer.id,
                "venue_id": booking.stock.offer.venueId,
                "provider_id": booking.stock.offer.lastProviderId,
                "user_id": current_user.id,
                "exception_class": e.__class__.__name__,
                "exception_message": str(e),
            },
            technical_message_id="native.bookings.cancel",
        )
        code, message = _CANCELLATION_EXCEPTION_TO_CODE_MAPPING.get(
            e.__class__,
            ("CANCELATION_FAILED", "L'annulation de réservation a échoué."),
        )
        raise ApiErrors({"code": code, "message": message})


@blueprint.native_route("/bookings/<int:booking_id>/toggle_display", methods=["POST"])
@spectree_serialize(api=blueprint.api, on_success_status=204, on_error_statuses=[400])
@authenticated_and_active_user_required
def flag_booking_as_used(booking_id: int, body: BookingDisplayStatusRequest) -> None:
    booking = first_or_404(
        db.session.query(Booking).filter(Booking.userId == current_user.id, Booking.id == booking_id)
    )
    booking.displayAsEnded = body.ended
    db.session.add(booking)
    db.session.commit()

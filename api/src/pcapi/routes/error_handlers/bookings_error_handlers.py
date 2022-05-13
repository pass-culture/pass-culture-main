from flask import Response
from flask import current_app as app
from flask import jsonify

from pcapi.core.bookings import exceptions
from pcapi.domain.client_exceptions import ClientError
from pcapi.domain.users import UnauthorizedForAdminUser
from pcapi.models import api_errors


JsonResponse = tuple[Response, int]


@app.errorhandler(exceptions.OfferIsAlreadyBooked)  # type: ignore [arg-type]
@app.errorhandler(exceptions.QuantityIsInvalid)
@app.errorhandler(exceptions.StockIsNotBookable)
@app.errorhandler(exceptions.CannotBookFreeOffers)
@app.errorhandler(exceptions.UserHasInsufficientFunds)
@app.errorhandler(exceptions.PhysicalExpenseLimitHasBeenReached)
@app.errorhandler(exceptions.DigitalExpenseLimitHasBeenReached)
@app.errorhandler(exceptions.OfferCategoryNotBookableByUser)
def handle_book_an_offer(exception: ClientError) -> JsonResponse:
    return jsonify(exception.errors), 400


@app.errorhandler(UnauthorizedForAdminUser)
def handle_get_all_bookings_exceptions(exception: UnauthorizedForAdminUser) -> JsonResponse:
    return jsonify(exception.errors), 401


@app.errorhandler(exceptions.CannotCancelConfirmedBooking)
def handle_cancel_a_booking(exception: ClientError) -> JsonResponse:
    return jsonify(exception.errors), 400


@app.errorhandler(exceptions.BookingDoesntExist)
def handle_cancel_a_booking_not_found(exception: exceptions.BookingDoesntExist) -> JsonResponse:
    return jsonify(exception.errors), 404


@app.errorhandler(exceptions.BookingIsAlreadyRefunded)
def handle_booking_is_already_refunded(exception: exceptions.BookingIsAlreadyRefunded) -> JsonResponse:
    error = {"payment": ["Cette réservation a été remboursée"]}
    return jsonify(error), api_errors.ForbiddenError.status_code


@app.errorhandler(exceptions.BookingRefused)
def handle_booking_refused(exception: exceptions.BookingRefused) -> JsonResponse:
    error = {
        "educationalBooking": (
            "Cette réservation pour une offre éducationnelle a été refusée par le chef d'établissement"
        )
    }
    return jsonify(error), api_errors.ForbiddenError.status_code


@app.errorhandler(exceptions.BookingIsNotConfirmed)
def handle_booking_is_not_confirmed(exception: exceptions.BookingIsNotConfirmed) -> JsonResponse:
    error = {"booking": [str(exception)]}
    return jsonify(error), api_errors.ForbiddenError.status_code


@app.errorhandler(exceptions.BookingIsAlreadyUsed)
def handle_booking_is_already_used(exception: exceptions.BookingIsAlreadyUsed) -> JsonResponse:
    error = {"booking": ["Cette réservation a déjà été validée"]}
    return jsonify(error), api_errors.ResourceGoneError.status_code


@app.errorhandler(exceptions.BookingIsAlreadyCancelled)
def handle_booking_is_already_cancelled(exception: exceptions.BookingIsAlreadyCancelled) -> JsonResponse:
    error = {"booking_cancelled": ["Cette réservation a été annulée"]}
    return jsonify(error), api_errors.ResourceGoneError.status_code

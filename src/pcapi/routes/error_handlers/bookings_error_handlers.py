from flask import current_app as app
from flask import jsonify

from pcapi.core.bookings.exceptions import BookingDoesntExist
from pcapi.core.bookings.exceptions import BookingIsAlreadyUsed
from pcapi.core.bookings.exceptions import CannotBookFreeOffers
from pcapi.core.bookings.exceptions import CannotCancelConfirmedBooking
from pcapi.core.bookings.exceptions import DigitalExpenseLimitHasBeenReached
from pcapi.core.bookings.exceptions import OfferIsAlreadyBooked
from pcapi.core.bookings.exceptions import PhysicalExpenseLimitHasBeenReached
from pcapi.core.bookings.exceptions import QuantityIsInvalid
from pcapi.core.bookings.exceptions import StockIsNotBookable
from pcapi.core.bookings.exceptions import UserHasInsufficientFunds
from pcapi.domain.users import UnauthorizedForAdminUser


@app.errorhandler(OfferIsAlreadyBooked)
@app.errorhandler(QuantityIsInvalid)
@app.errorhandler(StockIsNotBookable)
@app.errorhandler(CannotBookFreeOffers)
@app.errorhandler(UserHasInsufficientFunds)
@app.errorhandler(PhysicalExpenseLimitHasBeenReached)
@app.errorhandler(DigitalExpenseLimitHasBeenReached)
def handle_book_an_offer(exception):
    return jsonify(exception.errors), 400


@app.errorhandler(UnauthorizedForAdminUser)
def handle_get_all_bookings_exceptions(exception):
    return jsonify(exception.errors), 401


@app.errorhandler(BookingIsAlreadyUsed)
@app.errorhandler(CannotCancelConfirmedBooking)
def handle_cancel_a_booking(exception):
    return jsonify(exception.errors), 400


@app.errorhandler(BookingDoesntExist)
def handle_cancel_a_booking_not_found(exception):
    return jsonify(exception.errors), 404

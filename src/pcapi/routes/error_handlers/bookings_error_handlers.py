from flask import current_app as app, jsonify

from pcapi.core.bookings.exceptions import OfferIsAlreadyBooked, QuantityIsInvalid, StockIsNotBookable, \
    CannotBookFreeOffers, PhysicalExpenseLimitHasBeenReached, UserHasInsufficientFunds, \
    DigitalExpenseLimitHasBeenReached, BookingIsAlreadyUsed, EventHappensInLessThan72Hours, BookingDoesntExist
from pcapi.domain.stock.stock_exceptions import StockDoesntExist
from pcapi.domain.users import UnauthorizedForAdminUser


@app.errorhandler(OfferIsAlreadyBooked)
@app.errorhandler(StockDoesntExist)
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
@app.errorhandler(EventHappensInLessThan72Hours)
def handle_cancel_a_booking(exception):
    return jsonify(exception.errors), 400


@app.errorhandler(BookingDoesntExist)
def handle_cancel_a_booking_not_found(exception):
    return jsonify(exception.errors), 404

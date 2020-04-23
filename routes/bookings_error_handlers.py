from flask import current_app as app, jsonify

from domain.booking.booking_exceptions import OfferIsAlreadyBooked, QuantityIsInvalid, StockIsNotBookable, \
    CannotBookFreeOffers, PhysicalExpenseLimitHasBeenReached, UserHasInsufficientFunds, \
    DigitalExpenseLimitHasBeenReached
from domain.users import UnauthorizedForAdminUser
from domain.stock.stock_exceptions import StockDoesntExist


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

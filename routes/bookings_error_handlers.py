from flask import current_app as app, jsonify

from domain.booking import OfferIsAlreadyBooked, StockDoesntExist, QuantityIsInvalid, StockIsNotBookable, \
    CannotBookFreeOffers, PhysicalExpenseLimitHasBeenReached, UserHasInsufficientFunds, \
    DigitalExpenseLimitHasBeenReached
from domain.users import UnauthorizedForAdminUser


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

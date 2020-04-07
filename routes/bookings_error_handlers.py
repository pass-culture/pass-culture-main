from flask import current_app as app, jsonify

from domain.booking import OfferIsAlreadyBooked, StockDoesntExist, QuantityIsInvalid, StockIsNotBookable, \
    CannotBookFreeOffers, PhysicalExpenseLimitHasBeenReached, UserHasInsufficientFunds, \
    DigitalExpenseLimitHasBeenReached


@app.errorhandler(OfferIsAlreadyBooked)
@app.errorhandler(StockDoesntExist)
@app.errorhandler(QuantityIsInvalid)
@app.errorhandler(StockIsNotBookable)
@app.errorhandler(CannotBookFreeOffers)
@app.errorhandler(UserHasInsufficientFunds)
@app.errorhandler(PhysicalExpenseLimitHasBeenReached)
@app.errorhandler(DigitalExpenseLimitHasBeenReached)
def handle_offer_is_already_booked(exception):
    return jsonify(exception.errors), 400

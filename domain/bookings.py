from datetime import datetime

from models import ApiErrors


def check_has_stock_id(stock_id):
    if stock_id is None:
        api_errors = ApiErrors()
        api_errors.addError('stockId', 'Vous devez préciser un identifiant d\'offre')
        raise api_errors


def check_existing_stock(stock):
    if stock is None:
        api_errors = ApiErrors()
        api_errors.addError('stockId', 'stockId ne correspond à aucun stock')
        raise api_errors


def check_can_book_free_offer(stock, user):
    if (user.canBookFreeOffers is False) and (stock.price == 0):
        api_errors = ApiErrors()
        api_errors.addError('cannotBookFreeOffers', 'L\'utilisateur n\'a pas le droit de réserver d\'offres gratuites')
        raise api_errors


def check_offer_is_active(stock, offerer):
    if not stock.isActive or not offerer.isActive or (stock.eventOccurrence and (not stock.eventOccurrence.isActive)):
        api_errors = ApiErrors()
        api_errors.addError('stockId', "Cette offre a été retirée. Elle n'est plus valable.")
        raise api_errors


def check_stock_booking_limit_date(stock):
    if stock.bookingLimitDatetime is not None and stock.bookingLimitDatetime < datetime.utcnow():
        api_errors = ApiErrors()
        api_errors.addError('global', 'La date limite de réservation de cette offre est dépassée')
        raise api_errors

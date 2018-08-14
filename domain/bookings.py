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


def check_expenses_limits(expenses, booking, stock):
    if stock.resolvedOffer.event:
        return None

    if stock.resolvedOffer.thing.isDigital:
        _check_digital_expense_limit(booking, expenses)
    else:
        _check_physical_expense_limit(booking, expenses)


def _check_physical_expense_limit(booking, expenses):
    new_actual_amount = expenses['physical']['actual'] + booking.amount * booking.quantity
    if new_actual_amount > expenses['physical']['max']:
        api_errors = ApiErrors()
        api_errors.addError('global', 'La limite de %s € pour les biens culturels ne vous permet pas ' \
                                      'de réserver' % expenses['physical']['max'])
        raise api_errors


def _check_digital_expense_limit(booking, expenses):
    new_actual_amount = expenses['digital']['actual'] + booking.amount * booking.quantity
    if new_actual_amount > expenses['digital']['max']:
        api_errors = ApiErrors()
        api_errors.addError('global', 'La limite de %s € pour les offres numériques ne vous permet pas ' \
                                      'de réserver' % expenses['digital']['max'])
        raise api_errors

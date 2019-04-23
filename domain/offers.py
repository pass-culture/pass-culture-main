from repository import thing_queries
from models.offer_type import ProductType


class InconsistentOffer(Exception):

    def __init__(self, message=''):
        self.message = message

    def __str__(self):
        return self.message


def check_digital_offer_consistency(offer, venue, find_thing=thing_queries.find_by_id):
    thing = find_thing(offer.thingId)

    if venue.isVirtual and not thing.url:
        raise InconsistentOffer('Offer.venue is virtual but Offer.thing does not have an URL')

    if not venue.isVirtual and thing.url:
        raise InconsistentOffer('Offer.venue is not virtual but Offer.thing has an URL')


# add another class ?
def _remove_soft_deleted_stocks(stocks):
    valid_stocks = [stock for stock in stocks if not stock.isSoftDeleted]
    return valid_stocks


def _offer_has_unlimited_stock_message():
    return "illimité"


def _offer_has_no_more_stock_at_all_message(thing_type):
    stock_alert_message = 'plus de stock' if thing_type else 'plus de places pour toutes les dates'
    return stock_alert_message


def _offer_has_remaining_stock_message(remaining_for_all_stocks, thing_type):

    remaining_stock_word = 'places' if remaining_for_all_stocks > 1 and not thing_type else 'place'

    stock_alert_message = f'encore {remaining_for_all_stocks} en stock' if thing_type else f'encore {remaining_for_all_stocks} {remaining_stock_word}'

    return stock_alert_message


def _offer_has_no_stocks_yet_message(thing_type):
    stock_alert_message = 'pas encore de stock' if thing_type else 'pas encore de places'
    return stock_alert_message


def _offer_has_some_stock_empty_message(number_of_empty_stocks, thing_type):

    offer_word = 'offre' if number_of_empty_stocks == 1  else 'offres'

    stock_word = 'stock' if thing_type else 'places'

    stock_alert_message = f'plus de {stock_word} pour {number_of_empty_stocks} {offer_word}' if thing_type else f'plus de {stock_word} pour {number_of_empty_stocks} {offer_word}'
    return stock_alert_message


def _count_valid_bookinks(stock):
    total_bookings_by_stock = 0
    valid_bookings = [booking for booking in stock.bookings if not booking.isCancelled]
    for valid_booking in valid_bookings:
        total_bookings_by_stock += valid_booking.quantity
    return total_bookings_by_stock

def _add_zero_available_stock_as_empty_stock(stock, number_of_empty_stocks):
    if stock.available == 0:
        number_of_empty_stocks += 1
    return number_of_empty_stocks


def add_stock_alert_message_to_offer(offer):
    bookable_offer_stocks = _remove_soft_deleted_stocks(offer.stocks)
    stock_alert_message = ''

    if ProductType.is_thing(offer.type):
        thing_type = True
    else:
        thing_type = False

    TOTAL_NUMBER_STOCKS = len(bookable_offer_stocks)
    if TOTAL_NUMBER_STOCKS == 0:
        stock_alert_message = _offer_has_no_stocks_yet_message(thing_type)

    NUMBER_OF_UNLIMITED_PLACES_OR_STOCKS = len([stock for stock in bookable_offer_stocks if not stock.available and stock.available is not 0])

    if NUMBER_OF_UNLIMITED_PLACES_OR_STOCKS == TOTAL_NUMBER_STOCKS and TOTAL_NUMBER_STOCKS > 0:
        stock_alert_message = _offer_has_unlimited_stock_message()

    if TOTAL_NUMBER_STOCKS > 0:
        remaining_stock = 0
        remaining_for_all_stocks = 0
        number_of_empty_stocks = 0

    for stock in bookable_offer_stocks:
        total_bookings_by_stock = _count_valid_bookinks(stock)

        number_of_empty_stocks = _add_zero_available_stock_as_empty_stock(stock, number_of_empty_stocks)

        if stock.available:
            remaining_stock = stock.available - total_bookings_by_stock
            remaining_for_all_stocks += remaining_stock

            if remaining_stock == 0:
                number_of_empty_stocks += 1

        if number_of_empty_stocks >= 1:
            stock_alert_message = _offer_has_some_stock_empty_message( number_of_empty_stocks, thing_type)

        if number_of_empty_stocks == TOTAL_NUMBER_STOCKS:
            stock_alert_message = _offer_has_no_more_stock_at_all_message(thing_type)

        if remaining_stock > 0 and number_of_empty_stocks == 0:
            stock_alert_message = _offer_has_remaining_stock_message(remaining_for_all_stocks, thing_type)

    offer.stockAlertMessage = stock_alert_message

    return offer

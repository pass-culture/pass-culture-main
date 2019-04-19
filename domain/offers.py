from repository import thing_queries


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

def _offer_has_unlimited_stock():
        return "illimité"

def _offer_has_no_more_stock(stock_word, all_places_word):
        return f'plus de {stock_word} {all_places_word}'

def _offer_has_remaining_stock(remaining_for_all_stocks, remaining_stock_word):
    return f'encore {remaining_for_all_stocks} {remaining_stock_word}'

def _offer_has_no_stocks_yet(thing_type):
    stock_alert_message = 'pas encore de stock' if thing_type else 'pas encore de places'
    return stock_alert_message

def _offer_has_some_stock_empty(stock_word, empty_stocks, mot_offre):
    return f'plus de {stock_word} pour {empty_stocks} {mot_offre}'

def _count_valid_bookinks(stock):
    total_bookings_by_stock = 0
    valid_bookings = [booking for booking in stock.bookings if not booking.isCancelled]
    for valid_booking in valid_bookings:
        total_bookings_by_stock += valid_booking.quantity
    return total_bookings_by_stock

def addStockAlertMessageToOffer(offer):
    stocks = offer.stocks
    offer_stocks =_remove_soft_deleted_stocks(stocks)

    # wording
    stock_alert_message = ''
    offre_au_singulier = "offre"
    offre_au_pluriel = "offres"

    if offer.thingId:
        thing_type = True
        stock_word = "stock"
        remaining_stock_word = "en stock"
        all_places_word = ''
    else:
        thing_type = False
        stock_word = "places"
        all_places_word = 'pour toutes les dates'
        remaining_stock_word = "place"
        pluralized_remaining_stock_word = "places"

    TOTAL_NUMBER_STOCKS = len(offer_stocks)
    if TOTAL_NUMBER_STOCKS == 0:
        stock_alert_message = _offer_has_no_stocks_yet(thing_type)

    NUMBER_OF_UNLIMITED_PLACES_OR_STOCKS = len([stock for stock in offer_stocks if not stock.available and stock.available is not 0])

    if NUMBER_OF_UNLIMITED_PLACES_OR_STOCKS == TOTAL_NUMBER_STOCKS and TOTAL_NUMBER_STOCKS > 0:
        stock_alert_message = _offer_has_unlimited_stock()

    if TOTAL_NUMBER_STOCKS > 0:
        remaining_stock = 0
        remaining_for_all_stocks = 0
        empty_stocks = 0

    for stock in offer_stocks:
        total_bookings_by_stock = _count_valid_bookinks(stock)

        if stock.available == 0:
            empty_stocks += 1

        if stock.available:
            remaining_stock = stock.available - total_bookings_by_stock
            remaining_for_all_stocks += remaining_stock

            if remaining_stock == 0:
                empty_stocks += 1

        if empty_stocks >= 1:
            mot_offre = offre_au_singulier if empty_stocks == 1 else offre_au_pluriel
            stock_alert_message = _offer_has_some_stock_empty(stock_word, empty_stocks, mot_offre)

        if empty_stocks == TOTAL_NUMBER_STOCKS:
            stock_alert_message = _offer_has_no_more_stock(stock_word, all_places_word)

        if remaining_stock > 0 and empty_stocks == 0:

            if remaining_for_all_stocks > 1 and not thing_type:
                remaining_stock_word = pluralized_remaining_stock_word

            stock_alert_message = _offer_has_remaining_stock(remaining_for_all_stocks, remaining_stock_word)

    offer.stockAlertMessage = stock_alert_message

    return offer

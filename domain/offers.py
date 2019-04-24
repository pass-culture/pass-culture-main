from typing import List

from models import Stock, Offer
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


def _remove_soft_deleted_stocks(stocks: List[Stock]) -> List[Stock]:
    valid_stocks = [stock for stock in stocks if not stock.isSoftDeleted]
    return valid_stocks


def _offer_has_unlimited_stock_message() -> str:
    return "illimité"


def _offer_has_no_more_stock_at_all_message(is_thing: bool) -> str:
    stock_alert_message = 'plus de stock' if is_thing else 'plus de places pour toutes les dates'
    return stock_alert_message


def _offer_has_remaining_stock_message(remaining_for_all_stocks: int, is_thing: bool) -> str:

    remaining_stock_word = 'places' if remaining_for_all_stocks > 1 else 'place'

    stock_alert_message = f'encore {remaining_for_all_stocks} en stock' if is_thing else f'encore {remaining_for_all_stocks} {remaining_stock_word}'

    return stock_alert_message


def _offer_has_no_stocks_yet_message(is_thing: bool) -> str:
    stock_alert_message = 'pas encore de stock' if is_thing else 'pas encore de places'
    return stock_alert_message


def _offer_has_some_stock_empty_message(number_of_empty_stocks: int, is_thing: bool) -> str:

    offer_word = 'offre' if number_of_empty_stocks == 1  else 'offres'

    stock_word = 'stock' if is_thing else 'places'

    stock_alert_message = f'plus de {stock_word} pour {number_of_empty_stocks} {offer_word}' if is_thing else f'plus de {stock_word} pour {number_of_empty_stocks} {offer_word}'
    return stock_alert_message


def _count_valid_bookings(stock: Stock) -> int:
    total_bookings_by_stock = 0
    valid_bookings = [booking for booking in stock.bookings if not booking.isCancelled]
    for valid_booking in valid_bookings:
        total_bookings_by_stock += valid_booking.quantity
    return total_bookings_by_stock

def _increment_number_of_empty_stocks_if_not_available(stock: Stock, number_of_empty_stocks: int) -> int:
    if stock.available == 0:
        number_of_empty_stocks += 1
    return number_of_empty_stocks


def add_stock_alert_message_to_offer(offer: Offer) -> Offer:
    BOOKABLE_OFFER_STOCKS = _remove_soft_deleted_stocks(offer.stocks)

    TOTAL_NUMBER_STOCKS = len(BOOKABLE_OFFER_STOCKS)
    NUMBER_OF_UNLIMITED_PLACES_OR_STOCKS = len([stock for stock in BOOKABLE_OFFER_STOCKS if not stock.available and stock.available is not 0])

    IS_THING = ProductType.is_thing(offer.type)


    if TOTAL_NUMBER_STOCKS == 0:
        offer.stockAlertMessage = _offer_has_no_stocks_yet_message(IS_THING)
        return offer


    if NUMBER_OF_UNLIMITED_PLACES_OR_STOCKS == TOTAL_NUMBER_STOCKS:
        offer.stockAlertMessage = _offer_has_unlimited_stock_message()
        return offer


    stock_alert_message = _offer_with_limited_stock_alert_messagepar(BOOKABLE_OFFER_STOCKS, IS_THING,
                                                                     TOTAL_NUMBER_STOCKS)

    offer.stockAlertMessage = stock_alert_message

    return offer


def _offer_with_limited_stock_alert_messagepar(bookable_offer_stocks: List[Stock], is_thing: bool, total_number_stocks: int) -> str:
    remaining_for_all_stocks = 0
    number_of_empty_stocks = 0

    for stock in bookable_offer_stocks:
        total_bookings_by_stock = _count_valid_bookings(stock)

        number_of_empty_stocks = _increment_number_of_empty_stocks_if_not_available(stock, number_of_empty_stocks)

        if stock.available:
            remaining_stock = stock.available - total_bookings_by_stock
            remaining_for_all_stocks += remaining_stock

            if remaining_stock == 0:
                number_of_empty_stocks += 1

    if number_of_empty_stocks == total_number_stocks:
        return _offer_has_no_more_stock_at_all_message(is_thing)

    if number_of_empty_stocks >= 1:
        return _offer_has_some_stock_empty_message(number_of_empty_stocks, is_thing)

    if number_of_empty_stocks == 0:
        return _offer_has_remaining_stock_message(remaining_for_all_stocks, is_thing)

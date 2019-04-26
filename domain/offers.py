from typing import List

from models import Stock, Offer
from repository import thing_queries
from models.offer_type import ProductType


class InconsistentOffer(Exception):

    def __init__(self, message=''):
        self.message = message

    def __str__(self):
        return self.message


def check_digital_offer_consistency(offer, venue, find_thing_product=thing_queries.find_by_id):
    thing_product = find_thing_product(offer.thingId)

    if venue.isVirtual and not thing_product.url:
        raise InconsistentOffer('Offer.venue is virtual but Offer.product does not have an URL')

    if not venue.isVirtual and thing_product.url:
        raise InconsistentOffer('Offer.venue is not virtual but Offer.product has an URL')


def _filter_out_deleted_stocks(stocks: List[Stock]) -> List[Stock]:
    valid_stocks = [stock for stock in stocks if not stock.isSoftDeleted]
    return valid_stocks


def _increment_number_of_empty_stocks_if_not_available(stock: Stock, number_of_empty_stocks: int) -> int:
    if stock.available == 0:
        number_of_empty_stocks += 1
    return number_of_empty_stocks


def _count_valid_bookings(stock: Stock) -> int:
    total_bookings_by_stock = sum(b.quantity for b in stock.bookings if not b.isCancelled)
    return total_bookings_by_stock


def _offer_has_unlimited_stock_message() -> str:
    return "illimité"


def _offer_has_no_more_stock_at_all_message(is_thing: bool) -> str:
    if is_thing:
        stock_alert_message = 'plus de stock'
    else:
        stock_alert_message = 'plus de places pour toutes les dates'
    return stock_alert_message


def _offer_has_remaining_stock_message(remaining_for_all_stocks: int, is_thing: bool) -> str:
    remaining_stock_word = 'places' if remaining_for_all_stocks > 1 else 'place'

    if is_thing:
        stock_alert_message = f'encore {remaining_for_all_stocks} en stock'
    else:
        stock_alert_message = f'encore {remaining_for_all_stocks} {remaining_stock_word}'
    return stock_alert_message


def _offer_has_no_stocks_yet_message(is_thing: bool) -> str:
    if is_thing:
        stock_alert_message = 'pas encore de stock'
    else:
        stock_alert_message = 'pas encore de places'
    return stock_alert_message


def _offer_has_some_stock_empty_message(number_of_empty_stocks: int, is_thing: bool) -> str:
    offer_word = 'offre' if number_of_empty_stocks == 1 else 'offres'

    if is_thing:
        stock_alert_message = f'plus de stock pour {number_of_empty_stocks} {offer_word}'
    else:
        stock_alert_message = f'plus de places pour {number_of_empty_stocks} {offer_word}'
    return stock_alert_message


def _offer_with_limited_stock_alert_message(non_deleted_stocks: List[Stock], is_thing: bool, total_number_stocks: int) -> str:
    remaining_for_all_stocks = 0
    number_of_empty_stocks = 0

    for stock in non_deleted_stocks:
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


def add_stock_alert_message_to_offer(offer: Offer) -> Offer:
    non_deleted_stocks = _filter_out_deleted_stocks(offer.stocks)

    total_number_stocks = len(non_deleted_stocks)
    number_of_unlimited_places_or_stocks = len([stock for stock in non_deleted_stocks if not stock.available and stock.available is not 0])

    is_thing = offer.isThing

    if total_number_stocks == 0:
        offer.stockAlertMessage = _offer_has_no_stocks_yet_message(is_thing)
        return offer

    if number_of_unlimited_places_or_stocks == total_number_stocks:
        offer.stockAlertMessage = _offer_has_unlimited_stock_message()
        return offer

    stock_alert_message = _offer_with_limited_stock_alert_message(non_deleted_stocks, is_thing,
                                                                     total_number_stocks)

    offer.stockAlertMessage = stock_alert_message

    return offer

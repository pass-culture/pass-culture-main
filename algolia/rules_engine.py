from datetime import datetime

from domain.offers import has_remaining_stocks, has_at_least_one_stock_in_the_future
from models import Offer


def is_eligible_for_indexing(offer: Offer) -> bool:
    if offer is None:
        return False

    venue = offer.venue
    offerer = venue.managingOfferer
    not_deleted_stocks = offer.notDeletedStocks

    if offerer.isActive \
            and offerer.validationToken is None \
            and offer.isActive \
            and has_remaining_stocks(not_deleted_stocks) \
            and has_at_least_one_stock_in_the_future(not_deleted_stocks) \
            and venue.validationToken is None:
        return True

    return False


def is_eligible_for_reindexing(offer: Offer, offer_details: dict) -> bool:
    offer_name = offer.name
    offer_date_range = list(map(str, offer.dateRange.datetimes))
    offer_dates = []
    stocks = offer.notDeletedStocks
    offer_prices = list(map(lambda stock: float(stock.price), stocks))
    if offer.isEvent:
        offer_dates = list(map(lambda stock: datetime.timestamp(stock.beginningDatetime), stocks))

    indexed_offer_name = offer_details['name']
    indexed_offer_date_range = offer_details['dateRange']
    indexed_offer_dates = offer_details['dates']
    indexed_offer_prices = offer_details['prices']

    offer_name_has_changed = offer_name != indexed_offer_name
    stocks_have_changed = offer_date_range != indexed_offer_date_range
    stocks_beginning_datetime_have_changed = offer_dates != indexed_offer_dates
    prices_have_changed = offer_prices != indexed_offer_prices

    return offer_name_has_changed \
           or stocks_have_changed \
           or stocks_beginning_datetime_have_changed \
           or prices_have_changed

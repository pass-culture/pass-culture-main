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
    indexed_offer_name = offer_details['name']
    indexed_offer_date_range = offer_details['dateRange']
    offer_name_has_changed = offer_name != indexed_offer_name
    stocks_have_changed = offer_date_range != indexed_offer_date_range

    return offer_name_has_changed or stocks_have_changed
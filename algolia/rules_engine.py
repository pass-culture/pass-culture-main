from algolia.eligibility import EligibilityRules
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
    name_has_changed = EligibilityRules.NAME_HAS_CHANGED.value.apply(offer=offer, offer_details=offer_details)
    date_range_has_changed = EligibilityRules.DATE_RANGE_HAS_CHANGED.value.apply(offer=offer, offer_details=offer_details)
    dates_have_changed = EligibilityRules.DATES_HAVE_CHANGED.value.apply(offer=offer, offer_details=offer_details)
    prices_have_changed = EligibilityRules.PRICES_HAVE_CHANGED.value.apply(offer=offer, offer_details=offer_details)

    return name_has_changed \
           or date_range_has_changed \
           or dates_have_changed \
           or prices_have_changed

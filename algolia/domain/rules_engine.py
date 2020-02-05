from algolia.domain.eligibility import EligibilityRules
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
    eligibility_rules = [rule.value for rule in EligibilityRules]

    for rule in eligibility_rules:
        offer_data_has_changed = rule.apply(offer=offer, offer_details=offer_details)
        if offer_data_has_changed:
            return True
    return False

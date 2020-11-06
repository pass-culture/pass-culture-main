from pcapi.algolia.domain.eligibility import EligibilityRules
from pcapi.models import Offer


def is_eligible_for_reindexing(offer: Offer, offer_details: dict) -> bool:
    eligibility_rules = [rule.value for rule in EligibilityRules]

    for rule in eligibility_rules:
        offer_data_has_changed = rule.apply(offer=offer, offer_details=offer_details)
        if offer_data_has_changed:
            return True
    return False

import collections
from typing import List, Dict, Tuple

from models import DiscoveryViewV3, Offer


def order_offers_by_diversified_types(offers: List[DiscoveryViewV3]) -> List[DiscoveryViewV3]:
    offers_by_type = _get_offers_grouped_by_type_and_onlineless(offers)

    offers_by_type_ordered_by_frequency = collections.OrderedDict(
        sorted(offers_by_type.items(), key=_get_number_of_offers_by_type, reverse=True))

    diversified_offers = []

    while len(diversified_offers) != len(offers):
        for type in offers_by_type_ordered_by_frequency.keys():
            if offers_by_type_ordered_by_frequency[type]:
                diversified_offers.append(offers_by_type_ordered_by_frequency[type].pop())

    return diversified_offers


def _get_offers_grouped_by_type_and_onlineless(offers: List[DiscoveryViewV3]) -> Dict:
    offers_by_type = dict()
    for offer in offers:
        offer_type_and_oneliness = _compute_offer_type_and_oneliness(offer)
        if offer_type_and_oneliness in offers_by_type.keys():
            offers_by_type[offer_type_and_oneliness].append(offer)
        else:
            offers_by_type[offer_type_and_oneliness] = [offer]
    return offers_by_type


def _get_number_of_offers_by_type(type_and_offers: Tuple) -> int:
    return len(type_and_offers[1])


def _compute_offer_type_and_oneliness(offer: Offer) -> str:
    return str(offer.type) + '_DIGITAL' if offer.url else str(offer.type) + '_PHYSICAL'

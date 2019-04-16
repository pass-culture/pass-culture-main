""" recommendations stocks """
from itertools import cycle

from datetime import datetime
from random import randint
from sqlalchemy.orm import aliased
from typing import Optional, List, Tuple

from domain.departments import get_departement_codes_from_user
from models import Offer, Stock, Product
from models.offer_type import ProductType
from repository.offer_queries import get_active_offers_by_type
from utils.logger import logger

roundrobin_predicates = [
    lambda offer: ProductType.is_thing(offer.type),
    lambda offer: ProductType.is_event(offer.type)
]


def roundrobin(offers: List[Offer], limit: int) -> List[Offer]:
    result = []
    for predicate in cycle(roundrobin_predicates):
        if (len(result) == limit) \
                or (len(offers) == 0):
            return result
        for index, offer in enumerate(offers):
            if predicate(offer):
                result.append(offer)
                offers.pop(index)
                break
    return result


def make_score_tuples(offers: List[Offer]) -> List[Tuple[Offer, int]]:
    if len(offers) == 0:
        return []
    scored_offers = list(map(lambda o: (o, score_offer(o)), offers))
    logger.debug(lambda: '(reco) scored offers' + str([(so[0], so[1]) for so in scored_offers]))
    return scored_offers


def sort_by_score(offers: List[Offer]) -> List[Offer]:
    offer_tuples = make_score_tuples(offers)
    return list(_extract_offer(offer_tuples))


def score_offer(offer: Offer) -> Optional[int]:
    common_score = 0

    if offer.hasActiveMediation:
        common_score += 20
    elif offer.product.thumbCount == 0:
        # we don't want to recommend offers that have neither their own
        # image nor a mediation
        return None

    # a bit of randomness so we don't always return the same offers
    common_score += randint(0, 10)

    specific_score = None
    if ProductType.is_event(offer.type):
        specific_score = specific_score_event(offer.product)
    elif ProductType.is_thing(offer.type):
        specific_score = specific_score_thing(offer.product)

    if specific_score is None:
        return None

    return common_score + specific_score


def specific_score_event(product: Product) -> Optional[int]:
    score = 0
    next_occurrence_stock = Stock.query \
        .join(aliased(Offer)) \
        .filter((Offer.product == product) & (Stock.beginningDatetime > datetime.utcnow())) \
        .first()

    if next_occurrence_stock is None:
        return None

    # If the next occurrence of an event is less than 10 days away,
    # it gets one more point for each day closer it is to now
    score += max(0, 10 - (next_occurrence_stock.beginningDatetime - datetime.utcnow()).days)

    return score


def specific_score_thing(thing: Product) -> Optional[int]:
    score = 0
    return score


def remove_duplicate_things_or_events(offers: List[Offer]) -> List[Offer]:
    seen_product_ids = {}
    result = []
    for offer in offers:
        if offer.productId not in seen_product_ids:
            seen_product_ids[offer.productId] = True
            result.append(offer)
    return result


def get_offers_for_recommendations_discovery(limit=3, user=None, coords=None) -> List[Offer]:
    if not user or not user.is_authenticated():
        return []

    departement_codes = get_departement_codes_from_user(user)

    event_offers = get_active_offers_by_type(user=user, departement_codes=departement_codes)
    logger.debug(lambda: '(reco) event_offers count (%i)', len(event_offers))

    thing_offers = get_active_offers_by_type(user=user, departement_codes=departement_codes)
    logger.debug(lambda: '(reco) thing_offers count (%i)', len(thing_offers))

    offers = sort_by_score(event_offers + thing_offers)
    offers = remove_duplicate_things_or_events(offers)
    logger.debug(lambda: '(reco) final offers (events + things) count (%i)', len(offers))

    return roundrobin(offers, limit)


def _extract_offer(offer_tuples):
    return map(
        lambda st: st[0],
        _sort_by_score_desc(offer_tuples)
    )


def _sort_by_score_desc(offer_tuples):
    return sorted(
        _remove_none_scores(offer_tuples),
        key=lambda st: st[1],
        reverse=True
    )


def _remove_none_scores(offer_tuples):
    return filter(
        lambda st: st[1] is not None,
        offer_tuples
    )

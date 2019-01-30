""" recommendations stocks """
from datetime import datetime
from itertools import cycle
from random import randint
from typing import Optional, List, Tuple

from sqlalchemy.orm import aliased

from models import Event, EventOccurrence, Offer, Thing
from repository.offer_queries import get_active_offers_by_type
from utils.config import ILE_DE_FRANCE_DEPT_CODES
from utils.logger import logger

roundrobin_predicates = [
    lambda offer: offer.thingId,
    lambda offer: offer.eventId
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
    elif offer.eventOrThing.thumbCount == 0:
        # we don't want to recommend offers that have neither their own
        # image nor a mediation
        return None

    # a bit of randomness so we don't always return the same offers
    common_score += randint(0, 10)

    if isinstance(offer.eventOrThing, Event):
        specific_score = specific_score_event(offer.eventOrThing)
    else:
        specific_score = specific_score_thing(offer.eventOrThing)

    if specific_score is None:
        return None

    return common_score + specific_score


def specific_score_event(event: Event) -> Optional[int]:
    score = 0

    next_occurrence = EventOccurrence.query \
        .join(aliased(Offer)) \
        .filter((Offer.event == event) & (EventOccurrence.beginningDatetime > datetime.utcnow())) \
        .first()

    if next_occurrence is None:
        return None

    # If the next occurrence of an event is less than 10 days away,
    # it gets one more point for each day closer it is to now
    score += max(0, 10 - (next_occurrence.beginningDatetime - datetime.utcnow()).days)

    return score


def specific_score_thing(thing: Thing) -> Optional[int]:
    score = 0
    return score


def remove_duplicate_things_or_events(offers: List[Offer]) -> List[Offer]:
    seen_thing_ids = {}
    seen_event_ids = {}
    result = []
    for offer in offers:
        if offer.thingId not in seen_thing_ids and offer.eventId not in seen_event_ids:
            if offer.thingId:
                seen_thing_ids[offer.thingId] = True
            else:
                seen_event_ids[offer.eventId] = True
            result.append(offer)
    return result

def get_departement_codes_from_user(user):
    departement_codes = ILE_DE_FRANCE_DEPT_CODES \
        if user.departementCode == '93' \
        else [user.departementCode]
    return departement_codes

def get_offers_for_recommendations_discovery(limit=3, user=None, coords=None) -> List[Offer]:
    if not user or not user.is_authenticated():
        return []

    departement_codes = get_departement_codes_from_user(user)

    event_offers = get_active_offers_by_type(Event, user=user, departement_codes=departement_codes)
    logger.debug(lambda: '(reco) event_offers count (%i)', len(event_offers))

    thing_offers = get_active_offers_by_type(Thing, user=user, departement_codes=departement_codes)
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

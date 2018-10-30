""" recommendations stocks """
from datetime import datetime
from itertools import cycle
from random import randint

from sqlalchemy.orm import aliased

from models import Event, EventOccurrence, Offer, Thing
from repository.offer_queries import get_active_offers_by_type
from utils.config import ILE_DE_FRANCE_DEPT_CODES
from utils.logger import logger

roundrobin_predicates = [
    lambda offer: offer.thingId,
    lambda offer: offer.eventId
]


def roundrobin(offers, limit):
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


def make_score_tuples(offers, departement_codes):
    if len(offers) == 0:
        return []
    scored_offers = list(map(lambda o: (o, score_offer(o)), offers))
    logger.debug(lambda: '(reco) scored offers' + str([(so[0], so[1]) for so in scored_offers]))
    return scored_offers


def sort_by_score(offers, departement_codes):
    offer_tuples = make_score_tuples(offers, departement_codes)
    return list(_extract_offer(offer_tuples))


def score_offer(offer):
    common_score = 0

    if len(offer.mediations) > 0:
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


def specific_score_event(event):
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


def specific_score_thing(thing):
    score = 0
    return score


def remove_duplicate_things_or_events(offers):
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


def get_offers_for_recommendations_discovery(limit=3, user=None, coords=None):
    if not user or not user.is_authenticated():
        return []

    departement_codes = ILE_DE_FRANCE_DEPT_CODES \
        if user.departementCode == '93' \
        else [user.departementCode]

    event_offers = get_active_offers_by_type(Event, user=user, departement_codes=departement_codes)
    logger.info('(reco) event_offers count (%i)',
                len(event_offers))

    thing_offers = get_active_offers_by_type(Thing, user=user, departement_codes=departement_codes)
    logger.info('(reco) thing_offers count (%i)',
                len(thing_offers))

    offers = sort_by_score(event_offers + thing_offers, departement_codes)
    offers = remove_duplicate_things_or_events(offers)
    logger.info('(reco) final offers (events + things) count (%i)',
                len(offers))

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

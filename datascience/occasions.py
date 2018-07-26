""" recommendations offers """
from datetime import datetime
from flask import current_app as app
from itertools import cycle
from random import randint
from sqlalchemy.orm import aliased

from repository.occasion_queries import get_occasions_by_type
from models import Event, EventOccurence, Occasion, Thing
from utils.config import ILE_DE_FRANCE_DEPT_CODES
from utils.logger import logger


roundrobin_predicates = [
                          lambda occasion: occasion.thingId,
                          lambda occasion: occasion.eventId
                        ]


def roundrobin(occasions, limit):
    result = []
    for predicate in cycle(roundrobin_predicates):
        if (len(result) == limit)\
           or (len(occasions) == 0):
            return result
        for index, occasion in enumerate(occasions):
            if predicate(occasion):
                result.append(occasion)
                occasions.pop(index)
                break
    return result


def make_score_tuples(occasions, departement_codes):
    if len(occasions) == 0:
        return []
    scored_occasions = list(map(lambda o: (o, score_occasion(o, departement_codes)),
                                occasions))
    logger.debug(lambda: '(reco) scored occasions' + str([(so[0], so[1]) for so in scored_occasions]))
    return scored_occasions


def sort_by_score(occasions, departement_codes):
    occasion_tuples = make_score_tuples(occasions, departement_codes)
    return list(map(lambda st: st[0],
                    sorted(filter(lambda st: st[1] is not None, occasion_tuples),
                           key=lambda st: st[1],
                           reverse=True)))


def score_occasion(occasion, departement_codes):
    common_score = 0

    if len(occasion.mediations) > 0:
        common_score += 20
    elif occasion.thing_or_event.thumbCount == 0:
        # we don't want to recommend occasions that have neither their own
        # image nor a mediation
        return None

    # a bit of randomness so we don't always return the same occasions
    common_score += randint(0, 10)

    if isinstance(occasion, Event):
        specific_score = specific_score_event(occasion, departement_codes)
    else:
        specific_score = specific_score_thing(occasion, departement_codes)

    return common_score + specific_score


def specific_score_event(event, departement_codes):
    score = 0

    next_occurence = EventOccurence.query \
        .join(aliased(Occasion)) \
        .filter((Occasion.event == event) & (EventOccurence.beginningDatetime > datetime.utcnow())) \
        .first()

    if next_occurence is None:
        return None

    # If the next occurence of an event is less than 10 days away,
    # it gets one more point for each day closer it is to now
    score += max(0, 10 - (next_occurence.beginningDatetime - datetime.utcnow()).days)

    return score


def specific_score_thing(thing, departement_codes):
    score = 0
    return score


def remove_duplicate_things_or_events(occasions):
    seen_thing_ids = {}
    seen_event_ids = {}
    result = []
    for occasion in occasions:
        if occasion.thingId not in seen_thing_ids\
           and occasion.eventId not in seen_event_ids:
            if occasion.thingId:
                seen_thing_ids[occasion.thingId] = True
            else:
                seen_event_ids[occasion.eventId] = True
            result.append(occasion)
    return result


def get_occasions(limit=3, user=None, coords=None):
    if not user or not user.is_authenticated():
        return []

    departement_codes = ILE_DE_FRANCE_DEPT_CODES\
                          if user.departementCode == '93'\
                          else [user.departementCode]

    event_occasions = get_occasions_by_type(Event,
                                            user=user,
                                            coords=coords,
                                            departement_codes=departement_codes)
    thing_occasions = get_occasions_by_type(Thing,
                                            user=user,
                                            coords=coords,
                                            departement_codes=departement_codes)
    occasions = sort_by_score(event_occasions + thing_occasions,
                              departement_codes)
    occasions = remove_duplicate_things_or_events(occasions)

    logger.info('(reco) final occasions (events + things) count (%i)',
                len(occasions))

    return roundrobin(occasions, limit)

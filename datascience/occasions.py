""" recommendations offers """
from datetime import datetime
from flask import current_app as app
from random import randint
from sqlalchemy import func
from sqlalchemy.orm import aliased

from utils.config import IS_DEV
from utils.human_ids import dehumanize
from utils.compose import compose
from utils.content import get_mediation, get_source
from utils.distance import distance
from utils.includes import RECOMMENDATIONS_INCLUDES

Booking = app.model.Booking
Event = app.model.Event
EventOccurence = app.model.EventOccurence
Mediation = app.model.Mediation
Offer = app.model.Offer
Recommendation = app.model.Recommendation
Thing = app.model.Thing
Venue = app.model.Venue


def print_dev(*args):
    if IS_DEV:
        print(*args)


# --- SCORING ---

def make_score_tuples(occasions, departement_codes):
    if len(occasions) == 0:
        return []
    sort_function = score_event if isinstance(occasions[0], Event)\
                                else score_thing
    scored_occasions = list(map(lambda e: (e, sort_function(e, departement_codes)),
                                occasions))
    print_dev('(reco) scored occasions', [(se[0], se[1]) for se in scored_occasions])
    return scored_occasions


def sort_by_score(score_tuples):
    return list(map(lambda st: st[0],
                    sorted(filter(lambda st: st[1] is not None, score_tuples),
                           key=lambda st: st[1],
                           reverse=True)))


def score_event(event, departement_codes):
    score = 0

    app.db.session.query(Mediation.query.filter(Mediation.event == event).exists())

    if len(event.mediations) > 0:
        score += 20

    next_occurence = EventOccurence.query.filter((EventOccurence.event == event) &
                                                 (EventOccurence.beginningDatetime > datetime.now())).first()
    if next_occurence is None:
        return None
    
    # If the next occurence of an event is less than 10 days away,
    # it gets one more point for each day closer it is to now
    score += max(0, 10 - (next_occurence.beginningDatetime - datetime.now()).days)

    # a bit of randomness so we don't always return the same events
    score += randint(0, 10)

    return score


def score_thing(thing, departement_codes):
    score = 0

    # a bit of randomness so we don't always return the same events
    score += randint(0, 10)

    return score


# --- FILTERING ---

def departement_occasions(query, occasion_type, departement_codes):
    if occasion_type == Event:
        join_table = EventOccurence
    else:
        join_table = aliased(Offer)

    query = query.join(join_table)\
                 .join(Venue)\
                 .filter(Venue.departementCode.in_(departement_codes))\
                 .distinct(occasion_type.id)
    print_dev('(reco) departement occasions.count', query.count())
    return query


def bookable_occasions(query, occasion_type):
    # remove events for which all occurences are in the past
    # (crude filter to limit joins before the more complete one below)
    if occasion_type == Event:
        query = query.filter(Event.occurences.any(EventOccurence.beginningDatetime > datetime.now()))
        print_dev('(reco) future events.count', query.count())

    bo_Offer = aliased(Offer)
    query = query.join(bo_Offer)\
                 .filter(((bo_Offer.bookingLimitDatetime == None)
                          | (bo_Offer.bookingLimitDatetime > datetime.now()))
                         & ((bo_Offer.available == None) |
                            (bo_Offer.available > Booking.query.filter(Booking.offerId == bo_Offer.id).count())))\
                 .distinct(occasion_type.id)
    print_dev('(reco) bookable events.count', query.count())
    return query


def not_yet_recommended_occasions(query, user):
    query = query.filter(~ ((Event.recommendations.any(Recommendation.userId == user.id))
                         | (Event.mediations.any(Mediation.recommendations.any(Recommendation.userId == user.id)))))
    print_dev('(reco) not already used occasions.count', query.count())
    return query


# --- MAIN ---

def get_occasions_by_type(occasion_type,
                          limit=3,
                          user=None,
                          coords=None,
                          departement_codes=None):
    query = occasion_type.query
    print_dev('(reco) all '+str(occasion_type)+'.count', query.count())

    query = departement_occasions(query, occasion_type, departement_codes)
    query = bookable_occasions(query, occasion_type)
    query = not_yet_recommended_occasions(query, user)

    return sort_by_score(make_score_tuples(query.all(),
                                           departement_codes))


def get_occasions(limit=3, user=None, coords=None):
    if not user or not user.is_authenticated():
        return []

    departement_codes = ['75', '78', '91', '94', '93', '95']\
                          if user.departementCode == '93'\
                          else [user.departementCode]

    occasions = get_occasions_by_type(Event,
                                      limit=limit,
                                      user=user,
                                      coords=coords,
                                      departement_codes=departement_codes)\
              + get_occasions_by_type(Thing,
                                      limit=limit,
                                      user=user,
                                      coords=coords,
                                      departement_codes=departement_codes)

    print('(reco) final occasions (events + things) count', len(occasions))
    return occasions[:limit]


app.datascience.get_occasions = get_occasions

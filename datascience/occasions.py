""" recommendations offers """
from datetime import datetime
from flask import current_app as app
from random import randint
from sqlalchemy import func

from utils.config import IS_DEV
from datascience.hoqs import with_event_deduplication, with_departement_codes,\
    with_event, with_event_mediation, with_thing, with_thing_mediation
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


def make_score_tuples(occasions, departement_codes):
    if len(occasions) == 0:
        return []
    sort_function = score_event if isinstance(occasions, Event) else score_thing
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


def bookable_occasions(query):
    query = query.join(Offer)\
                 .filter(((Offer.bookingLimitDatetime == None)
                          | (Offer.bookingLimitDatetime > datetime.now()))
                         & ((Offer.available == None) |
                            (Offer.available > Booking.query.filter(Booking.offerId == Offer.id).count())))\
                 .distinct()
    print_dev('(reco) bookable events.count', query.count())
    return query


def not_yet_recommended_occasions(query, user):
    query = query.filter(~ ((Event.recommendations.any(Recommendation.userId == user.id))
                         | (Event.mediations.any(Mediation.recommendations.any(Recommendation.userId == user.id)))))
    print_dev('(reco) not already used occasions.count', query.count())
    return query


def get_occasions(limit=3, user=None, coords=None):
    # CHECK USER
    if not user or not user.is_authenticated():
        return []

    departement_codes = ['75', '78', '91', '94', '93', '95']\
                          if user.departementCode == '93'\
                          else [user.departementCode]

    # ALL EVENTS
    event_query = Event.query
    print_dev('(reco) all events.count', event_query.count())

    # LIMIT TO EVENTS IN RELEVANT DEPARTEMENTS
    event_query = event_query.join(EventOccurence)\
                             .join(Venue)\
                             .filter(Venue.departementCode.in_(departement_codes))\
                             .distinct()
    print_dev('(reco) departement events.count', event_query.count())

    # REMOVE EVENTS FOR WHICH ALL OCCURENCES ARE IN THE PAST (CRUDE FILTER TO LIMIT JOINS BEFORE THE MORE COMPLETE ONE BELOW)
    event_query = event_query.filter(Event.occurences.any(EventOccurence.beginningDatetime > datetime.now()))
    print_dev('(reco) future events.count', event_query.count())

    event_query = bookable_occasions(event_query)
    event_query = not_yet_recommended_occasions(event_query, user)

    events = sort_by_score(make_score_tuples(event_query.all(),
                                             departement_codes))

    # ALL THINGS
#    thing_query = Thing.query
#    print_dev('(reco) all things.count', thing_query.count())
#
#    # LIMIT TO THINGS IN RELEVANT DEPARTEMENTS
#    thing_query = thing_query.join(Offer)\
#                             .join(Venue)\
#                             .filter(Venue.departementCode.in_(departement_codes))\
#                             .distinct()
#    print_dev('(reco) departement things.count', thing_query.count())
#
#    thing_query = bookable_occasions(thing_query)
#    thing_query = not_yet_recommended_occasions(thing_query, user)
#    things = sort_by_score(make_score_tuples(thing_query.all(),
#                           departement_codes))
    things = []

    final_occasions = events + things

    # RETURN
    print('(reco) final count', len(final_occasions))
    return final_occasions[:limit]

app.datascience.get_occasions = get_occasions

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
Venue = app.model.Venue


def print_dev(*args):
    if IS_DEV:
        print(*args)


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


def get_occasions(limit=3, user=None, coords=None):
    # CHECK USER
    if not user or not user.is_authenticated():
        return []

    departement_codes = ['75', '78', '91', '94', '93', '95']\
                          if user.departementCode == '93'\
                          else [user.departementCode]

    # ALL
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

    # REMOVE EVENTS FOR WHICH THERE ARE NO AVAILABLE EVENTS PAST THEIR BOOKING LIMIT DATE
    event_query = event_query.join(Offer)\
                             .filter(((Offer.bookingLimitDatetime == None)
                                      | (Offer.bookingLimitDatetime > datetime.now()))
                                     & ((Offer.available == None) |
                                        (Offer.available > Booking.query.filter(Booking.offerId == Offer.id).count())))
    print_dev('(reco) bookable events.count', event_query.count())

    # REMOVE EVENTS FOR WHICH THERE IS ALREADY A RECOMMENDATION FOR THIS USER
    event_query = event_query.filter(~ ((Event.recommendations.any(Recommendation.userId == user.id))
                                        | (Event.mediations.any(Mediation.recommendations.any(Recommendation.userId == user.id)))))
    print_dev('(reco) not already used offers.count', event_query.count())

    scored_events = map(lambda e: (e, score_event(e, departement_codes)), event_query.all())
    events = list(map(lambda se: se[0],
                      sorted(filter(lambda se: se[1] is not None, scored_events),
                             key=lambda se: se[1],
                             reverse=True)))

#    thing_query = Things.query
#    print_dev('(reco) all things.count', thing_query.count())
    #TODO

    # PREPARE FINAL OFFERS (TODO: ALTERNATE THINGS AND EVENTS ?)
    final_occasions = events

    # RETURN
    print('(reco) final count', len(final_occasions))
    return final_occasions[0:min(limit, len(final_occasions))]

app.datascience.get_occasions = get_occasions

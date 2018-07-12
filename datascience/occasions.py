""" recommendations offers """
from datetime import datetime
from flask import current_app as app
from itertools import cycle, islice
from random import randint
from sqlalchemy import func
from sqlalchemy.orm import aliased

from utils.config import IS_DEV
from utils.human_ids import dehumanize
from utils.compose import compose
from utils.content import get_mediation, get_source
from utils.distance import distance
from utils.includes import RECOMMENDATION_INCLUDES

Booking = app.model.Booking
Event = app.model.Event
EventOccurence = app.model.EventOccurence
Mediation = app.model.Mediation
Offer = app.model.Offer
Offerer = app.model.Offerer
Recommendation = app.model.Recommendation
Thing = app.model.Thing
Venue = app.model.Venue

log = app.log



# --- SCORING ---


def roundrobin(*iterables):
    "roundrobin('ABC', 'D', 'EF') --> A D E B F C"
    # Recipe credited to George Sakkis
    pending = len(iterables)
    nexts = cycle(iter(it).__next__ for it in iterables)
    while pending:
        try:
            for next in nexts:
                yield next()
        except StopIteration:
            pending -= 1
            nexts = cycle(islice(nexts, pending))


def make_score_tuples(occasions, departement_codes):
    if len(occasions) == 0:
        return []
    scored_occasions = list(map(lambda e: (e, score_occasion(e, departement_codes)),
                                occasions))
    log.debug(lambda: '(reco) scored occasions'+str([(se[0], se[1]) for se in scored_occasions]))
    return scored_occasions


def sort_by_score(score_tuples):
    return list(map(lambda st: st[0],
                    sorted(filter(lambda st: st[1] is not None, score_tuples),
                           key=lambda st: st[1],
                           reverse=True)))


def score_occasion(occasion, departement_codes):
    common_score = 0

    if len(occasion.mediations) > 0:
        common_score += 20
    elif occasion.thumbCount == 0:
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

    next_occurence = EventOccurence.query.filter((EventOccurence.event == event) &
                                                 (EventOccurence.beginningDatetime > datetime.utcnow())).first()
    if next_occurence is None:
        return None

    # If the next occurence of an event is less than 10 days away,
    # it gets one more point for each day closer it is to now
    score += max(0, 10 - (next_occurence.beginningDatetime - datetime.utcnow()).days)

    return score


def specific_score_thing(thing, departement_codes):
    score = 0
    return score


# --- FILTERING ---

def aliased_join_table(occasion_type):
    if occasion_type == Event:
        return aliased(EventOccurence)
    else:
        return aliased(Offer)


def departement_or_national_occasions(query, occasion_type, departement_codes):
    join_table = aliased_join_table(occasion_type)
    condition = Venue.departementCode.in_(departement_codes)
    if occasion_type == Event:
        condition = (condition | (Event.isNational == True))
    query = query.join(join_table)\
                 .join(Venue)\
                 .filter(condition)\
                 .distinct(occasion_type.id)
    log.debug(lambda: '(reco) departement '+str(occasion_type)+'.count '+str(query.count()))
    return query


def bookable_occasions(query, occasion_type):
    # remove events for which all occurences are in the past
    # (crude filter to limit joins before the more complete one below)
    if occasion_type == Event:
        query = query.filter(Event.occurences.any(EventOccurence.beginningDatetime > datetime.utcnow()))
        log.debug(lambda: '(reco) future events.count '+str(query.count()))
        join_table = aliased_join_table(occasion_type)
        query = query.join(join_table)

    bo_Offer = aliased(Offer)
    query = query.join(bo_Offer)\
                 .filter((bo_Offer.isActive == True)
                         & ((bo_Offer.bookingLimitDatetime == None)
                            | (bo_Offer.bookingLimitDatetime > datetime.utcnow()))
                         & ((bo_Offer.available == None) |
                            (bo_Offer.available > Booking.query.filter(Booking.offerId == bo_Offer.id)
                                                         .statement.with_only_columns([func.coalesce(func.sum(Booking.quantity), 0)]))))\
                 .distinct(occasion_type.id)
    log.debug(lambda: '(reco) bookable '+str(occasion_type)+'.count '+str(query.count()))
    return query


def with_active_and_validated_offerer(query, occasion_type):
    query = query.join(Offerer)\
                 .filter((Offerer.isActive == True)
                         & (Offerer.validationToken == None))
    log.debug(lambda: '(reco) from active and validated offerer '+str(occasion_type)+'.count'+str(query.count()))
    return query


def not_currently_recommended_occasions(query, occasion_type, user):
    query = query.filter(~ ((occasion_type.recommendations.any((Recommendation.userId == user.id)
                                                               & (Recommendation.validUntilDate > datetime.utcnow())))
                            | (occasion_type.mediations.any(Mediation.recommendations.any((Recommendation.userId == user.id)
                                                                                          & (Recommendation.validUntilDate > datetime.utcnow()))))))
    log.debug(lambda: '(reco) not already used '+str(occasion_type)+'occasions.count '+str(query.count()))
    return query


# --- MAIN ---

def get_occasions_by_type(occasion_type,
                          limit=3,
                          user=None,
                          coords=None,
                          departement_codes=None,
                          occasion_id=None):
    query = occasion_type.query
    if occasion_id is not None:
        query = query.filter_by(id=occasion_id)
    log.debug(lambda: '(reco) all '+str(occasion_type)+'.count '+str(query.count()))

    query = departement_or_national_occasions(query, occasion_type, departement_codes)
    query = bookable_occasions(query, occasion_type)
    query = with_active_and_validated_offerer(query, occasion_type)
    query = not_currently_recommended_occasions(query, occasion_type, user)

    occasions = sort_by_score(make_score_tuples(query.all(),
                                                departement_codes))
    return occasions[:limit]


def get_occasions(limit=3, user=None, coords=None):
    if not user or not user.is_authenticated():
        return []

    departement_codes = ['75', '78', '91', '94', '93', '95']\
                          if user.departementCode == '93'\
                          else [user.departementCode]

    events = get_occasions_by_type(Event,
                                   limit=limit,
                                   user=user,
                                   coords=coords,
                                   departement_codes=departement_codes)
    things = get_occasions_by_type(Thing,
                                   limit=limit,
                                   user=user,
                                   coords=coords,
                                   departement_codes=departement_codes)

    log.info('(reco) final occasions (events + things) count (%i + %i)',
             len(events), len(things))
    return list(roundrobin(events, things))[:limit]


app.datascience.get_occasions = get_occasions
app.datascience.get_occasions_by_type = get_occasions_by_type

from datetime import datetime
from flask import current_app as app
from sqlalchemy import func
from sqlalchemy.orm import aliased

from models import Booking,\
                   Event,\
                   EventOccurrence,\
                   Occasion,\
                   Stock,\
                   Offerer,\
                   Recommendation,\
                   Venue
from utils.logger import logger


def departement_or_national_occasions(query, occasion_type, departement_codes):
    condition = Venue.departementCode.in_(departement_codes)
    if occasion_type == Event:
        condition = (condition | (Event.isNational == True))
    query = query.filter(condition)
    logger.debug(lambda: '(reco) departement .count ' + str(query.count()))
    return query


def bookable_occasions(query, occasion_type):
    # remove events for which all occurrences are in the past
    # (crude filter to limit joins before the more complete one below)
    query = query.reset_joinpoint()
    if occasion_type == Event:
        query = query.filter(Occasion.eventOccurrences.any(EventOccurrence.beginningDatetime > datetime.utcnow()))
        logger.debug(lambda: '(reco) future events.count ' + str(query.count()))

    query = query.filter((Stock.isActive == True)
                         & ((Stock.bookingLimitDatetime == None)
                            | (Stock.bookingLimitDatetime > datetime.utcnow()))
                         & ((Stock.available == None) |
                            (Stock.available > Booking.query.filter(Booking.stockId == Stock.id)
                             .statement.with_only_columns([func.coalesce(func.sum(Booking.quantity), 0)]))))
    logger.debug(lambda: '(reco) bookable .count ' + str(query.count()))
    return query


def with_active_and_validated_offerer(query):
    query = query.filter((Offerer.isActive == True)
                         & (Offerer.validationToken == None))
    logger.debug(lambda: '(reco) from active and validated offerer .count' + str(query.count()))
    return query


def not_currently_recommended_occasions(query, user):
    valid_recommendation_for_user = (Recommendation.userId == user.id) \
                                    & (Recommendation.validUntilDate > datetime.utcnow())

    query = query.filter(~(Occasion.recommendations.any(valid_recommendation_for_user)))

    logger.debug(lambda: '(reco) not already used occasions.count ' + str(query.count()))
    return query


def get_occasions_by_type(occasion_type,
                          user=None,
                          coords=None,
                          departement_codes=None,
                          occasion_id=None):
    query = Occasion.query
    if occasion_type == Event:
        query = query.join(aliased(EventOccurrence))
    query = query.join(Stock)\
                 .reset_joinpoint()\
                 .join(Venue)\
                 .join(Offerer)\
                 .reset_joinpoint()\
                 .join(occasion_type)
                 
    if occasion_id is not None:
        query = query.filter_by(id=occasion_id)
    logger.debug(lambda: '(reco) all ' + str(occasion_type) + '.count ' + str(query.count()))

    query = departement_or_national_occasions(query, occasion_type, departement_codes)
    query = bookable_occasions(query, occasion_type)
    query = with_active_and_validated_offerer(query)
    query = not_currently_recommended_occasions(query, user)
    query = query.distinct(occasion_type.id)
    return query.all()

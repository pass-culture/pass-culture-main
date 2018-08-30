from datetime import datetime
from flask import current_app as app
from sqlalchemy import func
from sqlalchemy.orm import aliased

from models import Booking,\
                   Event,\
                   EventOccurrence,\
                   Offer,\
                   Stock,\
                   Offerer,\
                   Recommendation,\
                   Venue
from utils.logger import logger


def departement_or_national_offers(query, offer_type, departement_codes):
    condition = Venue.departementCode.in_(departement_codes)
    if offer_type == Event:
        condition = (condition | (Event.isNational == True))
    query = query.filter(condition)
    logger.debug(lambda: '(reco) departement .count ' + str(query.count()))
    return query


def bookable_offers(query, offer_type):
    # remove events for which all occurrences are in the past
    # (crude filter to limit joins before the more complete one below)
    query = query.reset_joinpoint()
    if offer_type == Event:
        query = query.filter(Offer.eventOccurrences.any(EventOccurrence.beginningDatetime > datetime.utcnow()))
        logger.debug(lambda: '(reco) future events.count ' + str(query.count()))

    query = _filter_bookable_offers(query)
    logger.debug(lambda: '(reco) bookable .count ' + str(query.count()))
    return query


def _filter_bookable_offers(query):
    return query.filter((Stock.isSoftDeleted == False)
                        & ((Stock.bookingLimitDatetime == None)
                           | (Stock.bookingLimitDatetime > datetime.utcnow()))
                        & ((Stock.available == None) |
                           (Stock.available > Booking.query.filter(Booking.stockId == Stock.id)
                            .statement.with_only_columns([func.coalesce(func.sum(Booking.quantity), 0)]))))


def with_active_and_validated_offerer(query):
    query = query.filter((Offerer.isActive == True)
                         & (Offerer.validationToken == None))
    logger.debug(lambda: '(reco) from active and validated offerer .count' + str(query.count()))
    return query


def not_currently_recommended_offers(query, user):
    valid_recommendation_for_user = (Recommendation.userId == user.id) \
                                    & (Recommendation.validUntilDate > datetime.utcnow())

    query = query.filter(~(Offer.recommendations.any(valid_recommendation_for_user)))

    logger.debug(lambda: '(reco) not already used offers.count ' + str(query.count()))
    return query


def get_offers_by_type(offer_type,
                          user=None,
                          coords=None,
                          departement_codes=None,
                          offer_id=None):
    query = Offer.query
    if offer_type == Event:
        query = query.join(aliased(EventOccurrence))
    query = query.join(Stock)\
        .filter_by(isSoftDeleted=False)\
        .reset_joinpoint()\
        .join(Venue)\
        .join(Offerer)\
        .reset_joinpoint()\
        .join(offer_type)
                 
    if offer_id is not None:
        query = query.filter_by(id=offer_id)
    logger.debug(lambda: '(reco) all ' + str(offer_type) + '.count ' + str(query.count()))

    query = departement_or_national_offers(query, offer_type, departement_codes)
    query = bookable_offers(query, offer_type)
    query = with_active_and_validated_offerer(query)
    query = not_currently_recommended_offers(query, user)
    query = query.distinct(offer_type.id)
    return query.all()

from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import aliased

from models import Booking, \
    Event, \
    EventOccurrence, \
    Offer, \
    Stock, \
    Offerer, \
    Recommendation, \
    Venue
from models import Thing
from models.db import db
from repository.user_offerer_queries import filter_query_where_user_is_user_offerer_and_is_validated
from utils.logger import logger
from utils.search import get_search_filter


def departement_or_national_offers(query, offer_type, departement_codes):
    condition = Venue.departementCode.in_(departement_codes)
    if offer_type == Event:
        condition = (condition | (Event.isNational == True))
    if offer_type == Thing:
        condition = (condition | (Thing.isNational == True))
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


def get_offers_by_type(offer_type, user=None, departement_codes=None, offer_id=None):
    query = Offer.query.filter_by(isActive=True)
    if offer_type == Event:
        query = query.join(aliased(EventOccurrence))
    query = query.join(Stock) \
        .filter_by(isSoftDeleted=False) \
        .reset_joinpoint() \
        .join(Venue) \
        .join(Offerer) \
        .reset_joinpoint() \
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


def find_offers_in_date_range_for_given_venue_departement(date_max, date_min, department):

    query = db.session.query(Offer.id, Event.id, Event.name, EventOccurrence.beginningDatetime, Venue.departementCode,
                             Offerer.id, Offerer.name) \
        .join(Event) \
        .join(EventOccurrence) \
        .join(Venue) \
        .join(Offerer)
    if department:
        query = query.filter(Venue.departementCode == department)
    if date_min:
        query = query.filter(EventOccurrence.beginningDatetime >= date_min)
    if date_max:
        query = query.filter(EventOccurrence.beginningDatetime <= date_max)
    result = query.order_by(EventOccurrence.beginningDatetime) \
        .all()
    return result


def get_offers_for_recommendations_search(page=1, search=None):
    offer_query = _filter_out_offers_on_soft_deleted_stocks()
    if search is not None:
        offer_query = offer_query.outerjoin(Event)\
                                 .outerjoin(Thing)\
                                 .outerjoin(Venue)\
                                 .filter(get_search_filter([Event, Thing, Venue], search))

    offers = offer_query.paginate(int(page), per_page=10, error_out=False)\
                        .items

    return offers


def find_by_venue_id_or_offerer_id_and_search_terms_offers_where_user_has_rights(offerer_id, venue, venue_id, user,
                                                                                 request):
    query = Offer.query
    if venue_id is not None:
        query = query.filter_by(venue=venue)
    elif offerer_id is not None:
        query = query.join(Venue) \
            .join(Offerer) \
            .filter_by(id=offerer_id)
    elif not user.isAdmin:
        query = query.join(Venue) \
            .join(Offerer)
        query = filter_query_where_user_is_user_offerer_and_is_validated(query, user)
    search = request.args.get('search')
    if search is not None:
        query = query.outerjoin(Event) \
            .outerjoin(Thing) \
            .filter(get_search_filter([Event, Thing], search))
    return query


def _filter_out_offers_on_soft_deleted_stocks():
    join_on_stocks = Offer.query.filter_by(isActive=True) \
        .join(Stock) \
        .filter_by(isSoftDeleted=False)

    join_on_event_occurrences = Offer.query.filter_by(isActive=True) \
        .join(EventOccurrence) \
        .join(Stock) \
        .filter_by(isSoftDeleted=False)

    return join_on_stocks.union_all(join_on_event_occurrences)

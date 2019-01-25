from datetime import datetime
from typing import List

from sqlalchemy import func, and_, or_
from sqlalchemy.orm import aliased

from domain.keywords import create_filter_matching_all_keywords_in_any_model, \
                            create_get_filter_matching_ts_query_in_any_model, \
                            get_first_matching_keywords_string_at_column
from models import Booking, \
    Event, \
    EventOccurrence, \
    Offer, \
    Offerer, \
    Stock, \
    Offerer, \
    Recommendation, \
    Venue, EventType
from models import Thing
from models.db import db
from repository.user_offerer_queries import filter_query_where_user_is_user_offerer_and_is_validated
from utils.config import ILE_DE_FRANCE_DEPT_CODES
from utils.distance import get_sql_geo_distance_in_kilometers
from utils.logger import logger

get_filter_matching_ts_query_for_offer = create_get_filter_matching_ts_query_in_any_model(
    Event,
    Thing,
    Venue,
    Offerer
)

def departement_or_national_offers(query, offer_type, departement_codes):
    if '00' in departement_codes:
        return query
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
    if offer_type == Event:
        query = query.filter(Offer.eventOccurrences.any(EventOccurrence.beginningDatetime > datetime.utcnow()))
        logger.debug(lambda: '(reco) future events.count ' + str(query.count()))

    query = _filter_bookable_offers(query)
    logger.debug(lambda: '(reco) bookable .count ' + str(query.count()))
    return query


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


def get_active_offers_by_type(offer_type, user=None, departement_codes=None, offer_id=None):
    query = Offer.query.filter_by(isActive=True)
    if offer_type == Event:
        query = query.join(EventOccurrence)
        query = query.join(Stock, and_(EventOccurrence.id == Stock.eventOccurrenceId))
    else:
        query = query.join(Stock, and_(Offer.id == Stock.offerId))
    logger.info('(reco) ' + offer_type.__name__ + ' offers with stock count (%i)', query.count())

    query = query.join(Venue, and_(Offer.venueId == Venue.id))
    query = query.filter(Venue.validationToken == None)
    query = query.join(Offerer)
    if offer_type == Event:
        query = query.join(Event, and_(Offer.eventId == Event.id))
    else:
        query = query.join(Thing, and_(Offer.thingId == Thing.id))
    logger.info('(reco) ' + offer_type.__name__ + ' offers with venue offerer (%i)', query.count())

    if offer_id is not None:
        query = query.filter(Offer.id == offer_id)
    logger.debug(lambda: '(reco) all ' + str(offer_type) + '.count ' + str(query.count()))

    query = departement_or_national_offers(query, offer_type, departement_codes)
    logger.info('(reco) departement or national ' + offer_type.__name__ + ' (%i) in ' + str(departement_codes), query.count())
    query = bookable_offers(query, offer_type)
    logger.info('(reco) bookable_offers ' + offer_type.__name__ + ' (%i)', query.count())
    query = with_active_and_validated_offerer(query)
    logger.info('(reco) active and validated ' + offer_type.__name__ + ' (%i)', query.count())
    query = not_currently_recommended_offers(query, user)
    query = query.distinct(offer_type.id)
    logger.info('(reco) distinct ' + offer_type.__name__ + ' (%i)', query.count())
    return query.all()


def _date_interval_to_filter(date_interval):
    return ((EventOccurrence.beginningDatetime >= date_interval[0]) & \
            (EventOccurrence.beginningDatetime <= date_interval[1]))

def get_offer_join_query_for_keywords(query):
    query = query.outerjoin(Event) \
                 .outerjoin(Thing) \
                 .join(Venue) \
                 .join(Offerer)
    return query

def filter_offers_with_keywords_string(query, keywords_string):
    keywords_filter = create_filter_matching_all_keywords_in_any_model(
        get_filter_matching_ts_query_for_offer,
        keywords_string
    )

    query = get_offer_join_query_for_keywords(query)

    query = query.filter(keywords_filter)

    return query

def get_is_offer_selected_by_keywords_string_at_column(offer, keywords_string, column):
    query = offer.__class__.query.filter_by(id=offer.id)

    query = get_offer_join_query_for_keywords(query)

    return get_first_matching_keywords_string_at_column(
        query,
        keywords_string,
        column
    ) is not None

def get_is_offer_selected_by_keywords_string_at_column(offer, keywords_string, column):
    query = offer.__class__.query.filter_by(id=offer.id)\
                         .outerjoin(Event) \
                         .outerjoin(Thing) \
                         .join(Venue) \
                         .join(Offerer)

    return get_first_matching_keywords_string_at_column(
        query,
        keywords_string,
        column
    ) is not None

def get_offers_for_recommendations_search(
        date=None,
        page=1,
        keywords_string=None,
        type_values=None,
        latitude=None,
        longitude=None,
        max_distance=None,
        days_intervals=None):
    # NOTE: filter_out_offers_on_soft_deleted_stocks filter then
    # the offer with event that has NO event occurrence
    # Do we exactly want this ?

    query = _filter_recommendable_offers()

    if max_distance is not None and latitude is not None and longitude is not None:
        distance_instrument = get_sql_geo_distance_in_kilometers(
            Venue.latitude,
            Venue.longitude,
            latitude,
            longitude
        )
        query = query.join(Venue) \
                     .filter(distance_instrument < max_distance) \
                     .reset_joinpoint()

    if days_intervals is not None:
        event_beginningdate_in_interval_filter = or_(*map(
            _date_interval_to_filter, days_intervals))
        query = query.outerjoin(EventOccurrence) \
                     .filter(
                        event_beginningdate_in_interval_filter |\
                        (Offer.thing != None))\
                     .reset_joinpoint()

    if keywords_string is not None:
        query = filter_offers_with_keywords_string(query, keywords_string)

    if type_values is not None:
        event_query = query.from_self() \
                           .outerjoin(Event) \
                           .filter(Event.type.in_(type_values))

        thing_query = query.from_self() \
                           .outerjoin(Thing) \
                           .filter(Thing.type.in_(type_values))

        query = event_query.union_all(thing_query)

    if page is not None:
        offers = query.paginate(page, per_page=10, error_out=False) \
                     .items
    else:
        offers = query.all()

    return offers

def find_offers_with_filter_parameters(
        user,
        offerer_id=None,
        venue_id=None,
        keywords_string=None
):
    query = Offer.query

    if venue_id is not None:
        query = query.filter_by(venueId=venue_id)

    if keywords_string is not None:
        query = filter_offers_with_keywords_string(
            query,
            keywords_string
        )
    else:
        query = query.join(Venue).join(Offerer)

    if offerer_id is not None:
        query = query.filter_by(managingOffererId=offerer_id)

    if not user.isAdmin:
        query = filter_query_where_user_is_user_offerer_and_is_validated(
            query,
            user
        )

    return query

def find_searchable_offer(offer_id):
    return Offer.query.filter_by(id=offer_id)\
                      .join(Venue)\
                      .filter(Venue.validationToken == None)\
                      .first()

def _filter_recommendable_offers():
    join_on_stocks = Offer.query.filter_by(isActive=True) \
        .join(Stock) \
        .filter_by(isSoftDeleted=False)

    join_on_event_occurrences = Offer.query.filter_by(isActive=True) \
        .join(EventOccurrence) \
        .join(Stock) \
        .filter_by(isSoftDeleted=False)

    return join_on_stocks.union_all(join_on_event_occurrences)


def find_activation_offers(departement_code: str) -> List[Offer]:
    departement_codes = ILE_DE_FRANCE_DEPT_CODES if departement_code == '93' else [departement_code]
    match_department_or_is_national = or_(Venue.departementCode.in_(departement_codes), Event.isNational == True,
                                          Thing.isNational == True)
    join_on_stock = and_(or_(Offer.id == Stock.offerId, Stock.eventOccurrenceId == EventOccurrence.id))
    join_on_event_occurrence = and_(Offer.id == EventOccurrence.offerId)
    join_on_event = and_(Event.id == Offer.eventId)

    query = Offer.query \
        .outerjoin(Thing) \
        .outerjoin(Event, join_on_event) \
        .outerjoin(EventOccurrence, join_on_event_occurrence) \
        .join(Venue) \
        .join(Stock, join_on_stock) \
        .filter(Event.type == str(EventType.ACTIVATION)) \
        .filter(match_department_or_is_national)

    query = _filter_bookable_offers(query)

    return query


def _filter_bookable_offers(query):
    return query.filter((Stock.isSoftDeleted == False)
                        & ((Stock.bookingLimitDatetime == None)
                           | (Stock.bookingLimitDatetime > datetime.utcnow()))
                        & ((Stock.available == None) |
                           (Stock.available > Booking.query.filter(Booking.stockId == Stock.id)
                            .statement.with_only_columns([func.coalesce(func.sum(Booking.quantity), 0)]))))


def count_offers_for_things_only_by_venue_id(venue_id):
    offer_count = Offer.query \
        .filter_by(venueId=venue_id) \
        .filter(Offer.thing is not None) \
        .count()
    return offer_count


def find_offer_for_venue_id_and_specific_thing(venue_id, thing):
    offer = Offer.query \
        .filter_by(venueId=venue_id) \
        .filter_by(thing=thing) \
        .one_or_none()
    return offer


def find_offer_by_id(offer_id):
    return Offer.query \
        .filter(Offer.id == offer_id) \
        .first()

from datetime import datetime
from typing import List

from sqlalchemy import func, and_, or_

from models import Booking, \
    Event, \
    EventOccurrence, \
    Offer, \
    Stock, \
    Offerer, \
    Recommendation, \
    Venue, ThingType, EventType
from models import Thing
from models.db import db
from repository.user_offerer_queries import filter_query_where_user_is_user_offerer_and_is_validated
from utils.config import ILE_DE_FRANCE_DEPT_CODES
from utils.distance import get_sql_geo_distance_in_kilometers
from utils.logger import logger
from utils.search import get_keywords_filter


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
    query = query.filter(Stock.isSoftDeleted == False)
    query = query.join(Venue, and_(Offer.venueId == Venue.id))
    query = query.filter(Venue.validationToken == None)
    query = query.join(Offerer)
    if offer_type == Event:
        query = query.join(Event, and_(Offer.eventId == Event.id))
    else:
        query = query.join(Thing, and_(Offer.thingId == Thing.id))
    if offer_id is not None:
        query = query.filter(Offer.id == offer_id)
    logger.debug(lambda: '(reco) all ' + str(offer_type) + '.count ' + str(query.count()))

    query = departement_or_national_offers(query, offer_type, departement_codes)
    query = bookable_offers(query, offer_type)
    query = with_active_and_validated_offerer(query)
    query = not_currently_recommended_offers(query, user)
    query = query.distinct(offer_type.id)
    return query.all()


def find_offers_in_date_range_for_given_venue_departement(date_max, date_min, department):
    query = db.session.query(Offer.id,
                             Event.id,
                             Event.name,
                             EventOccurrence.beginningDatetime,
                             Venue.departementCode,
                             Offerer.id,
                             Offerer.name) \
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
    result = query.order_by(EventOccurrence.beginningDatetime).all()
    return result


def get_offers_for_recommendations_search(
        page=1,
        keywords=None,
        type_values=None,
        latitude=None,
        longitude=None,
        max_distance=None,
        days_intervals=None):
    # NOTE: filter_out_offers_on_soft_deleted_stocks filter then
    # the offer with event that has NO event occurrence
    # Do we exactly want this ?
    offer_query = _filter_recommendable_offers()

    # NOTE: which order of the filters is the best for minimal time computation ?
    # Question à 500 patates.

    if max_distance is not None and latitude is not None and longitude is not None:
        distance_instrument = get_sql_geo_distance_in_kilometers(
            Venue.latitude,
            Venue.longitude,
            latitude,
            longitude
        )
        offer_query = offer_query.join(Venue) \
            .filter(distance_instrument < max_distance)

    if days_intervals is not None:
        for days in days_intervals:
            date_offer_query = offer_query.from_self() \
                .join(Stock) \
                .outerjoin(EventOccurrence) \
                .filter(
                (
                        (Stock.bookingLimitDatetime >= days[0]) & \
                        (Stock.bookingLimitDatetime <= days[1])
                )
            )
            offer_query = offer_query.union_all(date_offer_query)

    if keywords is not None:
        offer_query = offer_query.from_self() \
            .outerjoin(Event) \
            .outerjoin(Thing) \
            .outerjoin(Venue) \
            .filter(get_keywords_filter([Event, Thing, Venue], keywords))

    if type_values is not None:
        event_offer_query = offer_query.from_self() \
            .outerjoin(Event) \
            .filter(Event.type.in_(type_values))

        thing_offer_query = offer_query.from_self() \
            .outerjoin(Thing) \
            .filter(Thing.type.in_(type_values))

        offer_query = event_offer_query.union_all(thing_offer_query)

    if page is not None:
        offers = offer_query.paginate(page, per_page=10, error_out=False) \
            .items
    else:
        offers = offer_query.all()

    return offers


def find_by_venue_id_or_offerer_id_and_search_terms_offers_where_user_has_rights(
        offerer_id,
        venue,
        venue_id,
        user,
        search
):
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
    if search is not None:
        query = query.outerjoin(Event) \
            .outerjoin(Thing) \
            .filter(get_keywords_filter([Event, Thing], search))
    return query


def find_searchable_offer(offer_id):
    return Offer.query.filter_by(id=offer_id).join(Venue).filter(Venue.validationToken == None).first()


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
    is_activation_offer = or_(Event.type == str(EventType.ACTIVATION), Thing.type == str(ThingType.ACTIVATION))

    join_on_stock = and_(or_(Offer.id == Stock.offerId, Stock.eventOccurrenceId == EventOccurrence.id))
    join_on_event_occurrence = and_(Offer.id == EventOccurrence.offerId)
    join_on_event = and_(Event.id == Offer.eventId)

    query = Offer.query \
        .outerjoin(Thing) \
        .outerjoin(Event, join_on_event) \
        .outerjoin(EventOccurrence, join_on_event_occurrence) \
        .join(Venue) \
        .join(Stock, join_on_stock) \
        .filter(is_activation_offer) \
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

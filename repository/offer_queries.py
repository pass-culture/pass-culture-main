from datetime import datetime, timedelta
from typing import List

from flask_sqlalchemy import BaseQuery
from sqlalchemy import desc, func, or_
from sqlalchemy.orm import aliased
from sqlalchemy.orm.query import Query
from sqlalchemy.sql.elements import BinaryExpression

from domain.departments import ILE_DE_FRANCE_DEPT_CODES
from domain.keywords import create_filter_matching_all_keywords_in_any_model, \
    create_get_filter_matching_ts_query_in_any_model
from models import EventType, \
    Mediation, \
    Offer, \
    Offerer, \
    Stock, \
    ThingType, \
    Venue, \
    Product, Favorite, Booking, \
    RecoView
from models.db import Model
from models.feature import FeatureToggle
from repository import feature_queries
from repository.user_offerer_queries import filter_query_where_user_is_user_offerer_and_is_validated
from utils.distance import get_sql_geo_distance_in_kilometers
from utils.logger import logger


def build_offer_search_base_query():
    return Offer.query.outerjoin(Product) \
        .join(Venue) \
        .join(Offerer)


def department_or_national_offers(query, departement_codes):
    if '00' in departement_codes:
        return query

    query = query.filter(
        Venue.departementCode.in_(departement_codes) | (Offer.isNational == True)
    )

    logger.debug(lambda: '(reco) departement .count ' + str(query.count()))
    return query


def _bookable_offers(offers_query: Query) -> Query:
    stocks_query = Stock.query.filter(Stock.offerId == Offer.id)
    stocks_query = _filter_bookable_stocks_for_discovery(stocks_query)
    offers_query = offers_query.filter(stocks_query.exists())
    return offers_query


def _has_active_and_validated_offerer() -> BinaryExpression:
    return (Offerer.isActive == True) & (Offerer.validationToken == None)


def _with_active_and_validated_offerer(query):
    query = query.join(Offerer, Offerer.id == Venue.managingOffererId) \
        .filter(_has_active_and_validated_offerer())
    logger.debug(lambda: '(reco) from active and validated offerer .count' + str(query.count()))
    return query


def _not_activation_offers(query):
    query = query.filter(Offer.type != str(EventType.ACTIVATION))
    return query.filter(Offer.type != str(ThingType.ACTIVATION))


def order_by_with_criteria():
    order_offers = _order_by_occurs_soon_or_is_thing_then_randomize()[:]
    order_by_criteria = desc(Offer.baseScore)
    order_offers.insert(-1, order_by_criteria)
    return order_offers


def _order_by_occurs_soon_or_is_thing_then_randomize():
    return [desc(_build_occurs_soon_or_is_thing_predicate()), func.random()]


def get_active_offers(user, pagination_params, departement_codes=None, offer_id=None, limit=None,
                      order_by=_order_by_occurs_soon_or_is_thing_then_randomize, seen_recommendation_ids=[]):
    # TODO: to optimize
    favorites = Favorite.query.filter_by(userId=user.id).all()
    favorite_ids = [favorite.offerId for favorite in favorites]

    # TODO: perf de merguez
    if '00' in departement_codes:
        venues = Venue.query.filter().all()
    else:
        venues = Venue.query.filter(Venue.departementCode.in_(departement_codes)).all()
    venue_ids = [venue.id for venue in venues]

    offers_booked = Offer.query.join(Stock).join(Booking).filter_by(userId=user.id).all()
    offer_booked_ids = [offer.id for offer in offers_booked]

    recos_query = RecoView.query \
        .filter(RecoView.id.notin_(favorite_ids)) \
        .filter(RecoView.id.notin_(seen_recommendation_ids)) \
        .filter(RecoView.id.notin_(offer_booked_ids)) \
        .filter(or_(RecoView.venueId.in_(venue_ids), RecoView.isNational == True)) \
        .order_by(RecoView.row_number)

    if limit:
        recos_query = recos_query.limit(limit)

    recos = recos_query.all()
    return recos


def _get_paginated_active_offers(limit, page, query):
    if page:
        query = query \
            .offset((int(page) - 1) * limit)
    query = query \
        .limit(limit)
    return query


def get_active_offers_ids_query(user, departement_codes=['00'], offer_id=None):
    active_offers_query = Offer.query.distinct(Offer.id)

    if offer_id is not None:
        active_offers_query = active_offers_query.filter(Offer.id == offer_id)
    logger.debug(lambda: '(reco) all offers count {}'.format(active_offers_query.count()))
    active_offers_query = active_offers_query.filter_by(isActive=True)
    logger.debug(lambda: '(reco) active offers count {}'.format(active_offers_query.count()))
    active_offers_query = _with_validated_venue(active_offers_query)
    logger.debug(lambda: '(reco) offers with venue count {}'.format(active_offers_query.count()))
    active_offers_query = _with_image(active_offers_query)
    logger.debug(lambda: '(reco) offers with image count {} '.format(active_offers_query.count()))
    active_offers_query = department_or_national_offers(active_offers_query, departement_codes)
    logger.debug(lambda:
                 '(reco) department or national {} in {}'.format(str(departement_codes),
                                                                 active_offers_query.count()))
    active_offers_query = _bookable_offers(active_offers_query)
    logger.debug(lambda: '(reco) bookable_offers {}'.format(active_offers_query.count()))
    active_offers_query = _with_active_and_validated_offerer(active_offers_query)
    logger.debug(lambda: '(reco) active and validated {}'.format(active_offers_query.count()))
    active_offers_query = _not_activation_offers(active_offers_query)
    logger.debug(lambda: '(reco) not_currently_recommended and not_activation {}'.format(active_offers_query.count()))
    if user:
        active_offers_query = _exclude_booked_and_favorite(active_offers_query, user)
    active_offer_ids = active_offers_query.with_entities(Offer.id).subquery()
    return active_offer_ids


def _exclude_booked_and_favorite(active_offers_query, user):
    booked_offer_ids = Booking.query.filter_by(userId=user.id).join(Stock).with_entities('stock."offerId"').subquery()
    favorite_offer_ids = Favorite.query.filter_by(userId=user.id).with_entities('"offerId"').subquery()
    not_booked_predicate = ~Offer.id.in_(booked_offer_ids)
    not_favorite_predicate = ~Offer.id.in_(favorite_offer_ids)

    active_offers_query = active_offers_query.filter(not_booked_predicate & not_favorite_predicate)

    return active_offers_query


def _round_robin_by_type_onlineness_and_criteria(order_by: List):
    return func.row_number() \
        .over(partition_by=[Offer.type, Offer.url == None],
              order_by=order_by())


def _with_image(offer_query):
    has_image_predicate = _build_has_active_mediation_predicate()
    return offer_query.filter(has_image_predicate)


def _with_validated_venue(offer_query):
    return offer_query.join(Venue, Offer.venueId == Venue.id) \
        .filter(Venue.validationToken == None)


def _build_occurs_soon_or_is_thing_predicate():
    return Stock.query.filter((Stock.offerId == Offer.id)
                              & ((Stock.beginningDatetime == None)
                                 | ((Stock.beginningDatetime > datetime.utcnow())
                                    & (Stock.beginningDatetime < (datetime.utcnow() + timedelta(days=10)))))) \
        .exists()


def _build_has_active_mediation_predicate():
    return Mediation.query.filter((Mediation.offerId == Offer.id)
                                  & Mediation.isActive) \
        .exists()


def _date_interval_to_filter(date_interval):
    return ((Stock.beginningDatetime >= date_interval[0]) &
            (Stock.beginningDatetime <= date_interval[1]))


def filter_offers_with_keywords_string_on_offer_only(query: BaseQuery, keywords_string: str) -> Query:
    return _build_query_using_keywords_on_model(keywords_string, query, Offer)


def filter_offers_with_keywords_string(query: BaseQuery, keywords_string: str) -> BaseQuery:
    query_on_offer_using_keywords = _build_query_using_keywords_on_model(keywords_string, query, Offer)
    query_on_offer_using_keywords = _order_by_offer_name_containing_keyword_string(keywords_string,
                                                                                   query_on_offer_using_keywords)

    query_on_venue_using_keywords = _build_query_using_keywords_on_model(keywords_string, query, Venue)

    query_on_offerer_using_keywords = _build_query_using_keywords_on_model(keywords_string, query, Offerer)

    return query_on_offer_using_keywords.union_all(
        query_on_venue_using_keywords,
        query_on_offerer_using_keywords
    )


def _build_query_using_keywords_on_model(keywords_string: str, query: BaseQuery, model: Model) -> BaseQuery:
    text_search_filters_on_model = create_get_filter_matching_ts_query_in_any_model(model)
    model_keywords_filter = create_filter_matching_all_keywords_in_any_model(
        text_search_filters_on_model, keywords_string
    )
    return query.filter(model_keywords_filter)


def _order_by_offer_name_containing_keyword_string(keywords_string: str, query: Query) -> Query:
    offer_alias = aliased(Offer)
    return query.order_by(
        desc(
            Offer.query
                .filter(Offer.id == offer_alias.id)
                .filter(Offer.name.op('@@')(func.plainto_tsquery(keywords_string)))
                .order_by(offer_alias.name)
                .exists()
        ),
        desc(Offer.id)
    )


def _offer_has_stocks_compatible_with_days_intervals(days_intervals):
    event_beginningdate_in_interval_filter = or_(*map(
        _date_interval_to_filter, days_intervals))
    stock_has_no_beginning_date_time = Stock.beginningDatetime == None
    return Stock.query \
        .filter(Stock.offerId == Offer.id) \
        .filter(
        event_beginningdate_in_interval_filter | \
        stock_has_no_beginning_date_time
    ).exists()


def get_offers_for_recommendations_search(
        page=1,
        page_size=10,
        keywords_string=None,
        type_values=None,
        latitude=None,
        longitude=None,
        max_distance=None,
        days_intervals=None):
    query = _filter_recommendable_offers_for_search(build_offer_search_base_query())

    if max_distance is not None and latitude is not None and longitude is not None:
        distance_instrument = get_sql_geo_distance_in_kilometers(
            Venue.latitude,
            Venue.longitude,
            latitude,
            longitude
        )
        query = query.filter(distance_instrument < max_distance) \
            .reset_joinpoint()

    if days_intervals is not None:
        query = query.filter(_offer_has_stocks_compatible_with_days_intervals(days_intervals)) \
            .reset_joinpoint()

    if keywords_string is not None:
        if feature_queries.is_active(FeatureToggle.FULL_OFFERS_SEARCH_WITH_OFFERER_AND_VENUE):
            query = filter_offers_with_keywords_string(query, keywords_string)
        else:
            query = filter_offers_with_keywords_string_on_offer_only(query, keywords_string)

    if type_values is not None:
        query = query.filter(Offer.type.in_(type_values))

    if page is not None:
        query = query \
            .offset((page - 1) * page_size) \
            .limit(page_size)
    offers = query.all()

    return offers


def find_offers_with_filter_parameters(
        user,
        offerer_id=None,
        venue_id=None,
        keywords_string=None
):
    query = build_offer_search_base_query()

    if venue_id is not None:
        query = query.filter(Offer.venueId == venue_id)

    if offerer_id is not None:
        query = query.filter(Venue.managingOffererId == offerer_id)

    if not user.isAdmin:
        query = filter_query_where_user_is_user_offerer_and_is_validated(
            query,
            user
        )

    if keywords_string is not None:
        query = filter_offers_with_keywords_string(
            query,
            keywords_string
        )
    else:
        query = query.order_by(Offer.id.desc())

    return query


def _has_remaining_stock():
    is_unlimited_stock = Stock.available == None
    has_remaining_stock = Stock.remainingQuantity > 0
    return is_unlimited_stock | has_remaining_stock


def find_searchable_offer(offer_id):
    return Offer.query.filter_by(id=offer_id) \
        .join(Venue) \
        .filter(Venue.validationToken == None) \
        .first()


def _offer_has_bookable_stocks():
    now = datetime.utcnow()
    stock_can_still_be_booked = (Stock.bookingLimitDatetime > now) | (Stock.bookingLimitDatetime == None)
    event_has_not_began_yet = (Stock.beginningDatetime != None) & (Stock.beginningDatetime > now)
    offer_is_on_a_thing = Stock.beginningDatetime == None
    return Stock.query \
        .filter(Stock.offerId == Offer.id) \
        .filter(Stock.isSoftDeleted == False) \
        .filter(stock_can_still_be_booked) \
        .filter(event_has_not_began_yet | offer_is_on_a_thing) \
        .filter(_has_remaining_stock()) \
        .exists()


def _filter_recommendable_offers_for_search(offer_query):
    offer_query = offer_query.reset_joinpoint() \
        .filter(Offer.isActive == True) \
        .filter(_has_active_and_validated_offerer()) \
        .filter(Venue.validationToken == None) \
        .filter(_offer_has_bookable_stocks())
    return offer_query


def find_activation_offers(departement_code: str) -> List[Offer]:
    departement_codes = ILE_DE_FRANCE_DEPT_CODES if departement_code == '93' else [departement_code]
    match_department_or_is_national = or_(Venue.departementCode.in_(departement_codes), Offer.isNational == True)

    query = Offer.query \
        .join(Venue) \
        .join(Stock, Stock.offerId == Offer.id) \
        .filter(Offer.type == str(EventType.ACTIVATION)) \
        .filter(match_department_or_is_national)

    query = _filter_bookable_stocks_for_discovery(query)

    return query


def _filter_bookable_stocks_for_discovery(stocks_query):
    beginning_date_is_in_the_future_predicate = (Stock.beginningDatetime > datetime.utcnow())
    booking_limit_date_is_in_the_future_predicate = (Stock.bookingLimitDatetime > datetime.utcnow())
    has_no_beginning_date_predicate = (Stock.beginningDatetime == None)
    has_no_booking_limit_date_predicate = (Stock.bookingLimitDatetime == None)
    is_not_soft_deleted_predicate = (Stock.isSoftDeleted == False)

    stocks_query = stocks_query.filter(is_not_soft_deleted_predicate
                                       & (beginning_date_is_in_the_future_predicate
                                          | has_no_beginning_date_predicate)
                                       & (booking_limit_date_is_in_the_future_predicate
                                          | has_no_booking_limit_date_predicate)
                                       & _has_remaining_stock())
    return stocks_query


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


def get_offer_by_id(offer_id: int):
    return Offer.query.get(offer_id)


def get_offers_by_venue_id(venue_id: int) -> List[Offer]:
    return Offer.query \
        .filter_by(venueId=venue_id) \
        .all()


def get_offers_by_product_id(product_id: int) -> List[Offer]:
    return Offer.query \
        .filter_by(productId=product_id) \
        .all()


def get_offers_by_ids(offer_ids: List[int]) -> List[Offer]:
    return Offer.query \
        .filter(Offer.id.in_(offer_ids)) \
        .all()


def get_paginated_offer_ids(limit: int, page: int) -> List[tuple]:
    return Offer.query \
        .with_entities(Offer.id) \
        .order_by(Offer.id) \
        .offset(page * limit) \
        .limit(limit) \
        .all()


def get_paginated_offer_ids_by_venue_id(venue_id: int, limit: int, page: int) -> List[tuple]:
    return Offer.query \
        .with_entities(Offer.id) \
        .filter(Offer.venueId == venue_id) \
        .order_by(Offer.id) \
        .offset(page * limit) \
        .limit(limit) \
        .all()


def get_paginated_offer_ids_by_venue_id_and_last_provider_id(last_provider_id: str,
                                                             limit: int,
                                                             page: int,
                                                             venue_id: int) -> List[tuple]:
    return Offer.query \
        .with_entities(Offer.id) \
        .filter(Offer.lastProviderId == last_provider_id) \
        .filter(Offer.venueId == venue_id) \
        .order_by(Offer.id) \
        .offset(page * limit) \
        .limit(limit) \
        .all()

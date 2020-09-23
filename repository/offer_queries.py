from datetime import datetime, timedelta
from typing import List, Optional

from flask_sqlalchemy import BaseQuery
from sqlalchemy import func, nullsfirst, or_
from sqlalchemy.orm import aliased, joinedload
from sqlalchemy.orm.query import Query
from sqlalchemy.sql import selectable
from sqlalchemy.sql.elements import BinaryExpression

from domain.departments import ILE_DE_FRANCE_DEPT_CODES
from models import BookingSQLEntity, DiscoveryView, DiscoveryViewV3, \
    EventType, FavoriteSQLEntity, MediationSQLEntity, OfferSQLEntity, Offerer, SeenOffer, StockSQLEntity, ThingType, \
    UserSQLEntity, VenueSQLEntity
from models.db import Model
from models.feature import FeatureToggle
from repository import feature_queries
from repository.booking_queries import get_only_offer_ids_from_bookings
from repository.favorite_queries import get_only_offer_ids_from_favorites
from repository.iris_venues_queries import find_venues_located_near_iris
from repository.venue_queries import get_only_venue_ids_for_department_codes
from use_cases.diversify_recommended_offers import order_offers_by_diversified_types
from utils.logger import logger

ALL_DEPARTMENTS_CODE = '00'


def department_or_national_offers(query, departement_codes):
    if ALL_DEPARTMENTS_CODE in departement_codes:
        return query.filter((VenueSQLEntity.departementCode != None) | (OfferSQLEntity.isNational == True))

    query = query.filter(
        VenueSQLEntity.departementCode.in_(departement_codes) | (OfferSQLEntity.isNational == True)
    )

    logger.debug(lambda: '(reco) departement .count ' + str(query.count()))
    return query


def _bookable_offers(offers_query: Query) -> Query:
    stocks_query = StockSQLEntity.query.filter(StockSQLEntity.offerId == OfferSQLEntity.id)
    stocks_query = _filter_bookable_stocks_for_discovery(stocks_query)
    offers_query = offers_query.filter(stocks_query.exists())
    return offers_query


def _has_active_and_validated_offerer() -> BinaryExpression:
    return (Offerer.isActive == True) & (Offerer.validationToken == None)


def _with_active_and_validated_offerer(query):
    query = query.join(Offerer, Offerer.id == VenueSQLEntity.managingOffererId) \
        .filter(_has_active_and_validated_offerer())
    logger.debug(lambda: '(reco) from active and validated offerer .count' + str(query.count()))
    return query


def _not_activation_offers(query):
    query = query.filter(OfferSQLEntity.type != str(EventType.ACTIVATION))
    return query.filter(OfferSQLEntity.type != str(ThingType.ACTIVATION))


def get_offers_for_recommendation(user: UserSQLEntity, departement_codes: List[str] = None, limit: int = None,
                                  sent_offers_ids: List[int] = []) -> List[DiscoveryView]:
    favorite_ids = get_only_offer_ids_from_favorites(user)

    offer_booked_ids = get_only_offer_ids_from_bookings(user)

    discovery_view_query = DiscoveryView.query \
        .filter(DiscoveryView.id.notin_(favorite_ids)) \
        .filter(DiscoveryView.id.notin_(sent_offers_ids)) \
        .filter(DiscoveryView.id.notin_(offer_booked_ids))

    if ALL_DEPARTMENTS_CODE not in departement_codes:
        venue_ids = get_only_venue_ids_for_department_codes(departement_codes)
        discovery_view_query = keep_only_offers_in_venues_or_national(discovery_view_query, venue_ids)

    if feature_queries.is_active(FeatureToggle.SAVE_SEEN_OFFERS):
        discovery_view_query = order_offers_by_unseen_offers_first(discovery_view_query, DiscoveryView, user)

    discovery_view_query = discovery_view_query.order_by(DiscoveryView.offerDiscoveryOrder)

    if limit:
        discovery_view_query = discovery_view_query.limit(limit)

    return order_offers_by_diversified_types(discovery_view_query.all())


def get_offers_for_recommendation_v3(user: UserSQLEntity, user_iris_id: Optional[int] = None,
                                     user_is_geolocated: bool = False, limit: Optional[int] = None,
                                     sent_offers_ids: List[int] = []) -> List[DiscoveryViewV3]:
    favorite_offers_ids = get_only_offer_ids_from_favorites(user)

    booked_offers_ids = get_only_offer_ids_from_bookings(user)

    discovery_view_query = DiscoveryViewV3.query \
        .filter(DiscoveryViewV3.id.notin_(favorite_offers_ids)) \
        .filter(DiscoveryViewV3.id.notin_(sent_offers_ids)) \
        .filter(DiscoveryViewV3.id.notin_(booked_offers_ids))

    if user_is_geolocated:
        venue_ids = find_venues_located_near_iris(user_iris_id)
        discovery_view_query = keep_only_offers_from_venues_located_near_to_user_or_national(discovery_view_query,
                                                                                             venue_ids)

    if feature_queries.is_active(FeatureToggle.SAVE_SEEN_OFFERS):
        discovery_view_query = order_offers_by_unseen_offers_first(discovery_view_query, DiscoveryViewV3, user)

    discovery_view_query = discovery_view_query.order_by(DiscoveryViewV3.offerDiscoveryOrder)

    if limit:
        discovery_view_query = discovery_view_query.limit(limit)

    return order_offers_by_diversified_types(discovery_view_query.all())


def order_offers_by_unseen_offers_first(query: BaseQuery, discovery_view_model: Model, user: UserSQLEntity):
    return query.outerjoin(SeenOffer, (SeenOffer.offerId == discovery_view_model.id) & (SeenOffer.userId == user.id)) \
        .order_by(nullsfirst(SeenOffer.dateSeen))


def keep_only_offers_from_venues_located_near_to_user_or_national(query: BaseQuery,
                                                                  venue_ids: List[int] = []) -> BaseQuery:
    return query.filter(or_(DiscoveryViewV3.venueId.in_(venue_ids), DiscoveryViewV3.isNational == True))


def keep_only_offers_in_venues_or_national(query: BaseQuery, venue_ids: selectable.Alias) -> BaseQuery:
    return query \
        .filter(or_(DiscoveryView.venueId.in_(venue_ids), DiscoveryView.isNational == True))


def get_active_offers_ids_query(user, departement_codes=[ALL_DEPARTMENTS_CODE], offer_id=None):
    active_offers_query = OfferSQLEntity.query.distinct(OfferSQLEntity.id)

    if offer_id is not None:
        active_offers_query = active_offers_query.filter(OfferSQLEntity.id == offer_id)
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
    active_offer_ids = active_offers_query.with_entities(OfferSQLEntity.id).subquery()
    return active_offer_ids


def _exclude_booked_and_favorite(active_offers_query, user):
    booked_offer_ids = BookingSQLEntity.query.filter_by(userId=user.id).join(StockSQLEntity).with_entities(
        'stock."offerId"').subquery()
    favorite_offer_ids = FavoriteSQLEntity.query.filter_by(userId=user.id).with_entities('"offerId"').subquery()
    not_booked_predicate = ~OfferSQLEntity.id.in_(booked_offer_ids)
    not_favorite_predicate = ~OfferSQLEntity.id.in_(favorite_offer_ids)

    active_offers_query = active_offers_query.filter(not_booked_predicate & not_favorite_predicate)

    return active_offers_query


def _with_image(offer_query):
    has_image_predicate = _build_has_active_mediation_predicate()
    return offer_query.filter(has_image_predicate)


def _with_validated_venue(offer_query):
    return offer_query.join(VenueSQLEntity, OfferSQLEntity.venueId == VenueSQLEntity.id) \
        .filter(VenueSQLEntity.validationToken == None)


def _build_has_active_mediation_predicate():
    return MediationSQLEntity.query.filter((MediationSQLEntity.offerId == OfferSQLEntity.id)
                                           & MediationSQLEntity.isActive) \
        .exists()


def find_searchable_offer(offer_id):
    return OfferSQLEntity.query.filter_by(id=offer_id) \
        .join(VenueSQLEntity) \
        .filter(VenueSQLEntity.validationToken == None) \
        .first()


def _offer_has_bookable_stocks():
    now = datetime.utcnow()
    stock_can_still_be_booked = (StockSQLEntity.bookingLimitDatetime > now) | (
            StockSQLEntity.bookingLimitDatetime == None)
    event_has_not_began_yet = (StockSQLEntity.beginningDatetime != None) & (StockSQLEntity.beginningDatetime > now)
    offer_is_on_a_thing = StockSQLEntity.beginningDatetime == None
    bookings_quantity = _build_bookings_quantity_subquery()

    return StockSQLEntity.query \
        .filter(StockSQLEntity.offerId == OfferSQLEntity.id) \
        .filter(StockSQLEntity.isSoftDeleted == False) \
        .filter(stock_can_still_be_booked) \
        .filter(event_has_not_began_yet | offer_is_on_a_thing) \
        .outerjoin(bookings_quantity, StockSQLEntity.id == bookings_quantity.c.stockId) \
        .filter((StockSQLEntity.quantity == None) | (
            (StockSQLEntity.quantity - func.coalesce(bookings_quantity.c.quantity, 0)) > 0)) \
        .exists()


def _build_bookings_quantity_subquery():
    stock_alias = aliased(StockSQLEntity)
    bookings_quantity = BookingSQLEntity.query \
        .join(stock_alias) \
        .filter(BookingSQLEntity.isCancelled == False) \
        .group_by(BookingSQLEntity.stockId) \
        .with_entities(func.sum(BookingSQLEntity.quantity).label('quantity'), BookingSQLEntity.stockId.label('stockId')) \
        .subquery()
    return bookings_quantity


def _filter_recommendable_offers_for_search(offer_query):
    offer_query = offer_query.reset_joinpoint() \
        .filter(OfferSQLEntity.isActive == True) \
        .filter(_has_active_and_validated_offerer()) \
        .filter(VenueSQLEntity.validationToken == None) \
        .filter(_offer_has_bookable_stocks())
    return offer_query


def find_activation_offers(departement_code: str) -> List[OfferSQLEntity]:
    departement_codes = ILE_DE_FRANCE_DEPT_CODES if departement_code == '93' else [departement_code]
    match_department_or_is_national = or_(VenueSQLEntity.departementCode.in_(departement_codes),
                                          OfferSQLEntity.isNational == True)

    query = OfferSQLEntity.query \
        .join(VenueSQLEntity) \
        .join(StockSQLEntity, StockSQLEntity.offerId == OfferSQLEntity.id) \
        .filter(OfferSQLEntity.type == str(EventType.ACTIVATION)) \
        .filter(match_department_or_is_national)

    query = _filter_bookable_stocks_for_discovery(query)

    return query


def _filter_bookable_stocks_for_discovery(stocks_query):
    beginning_date_is_in_the_future_predicate = (StockSQLEntity.beginningDatetime > datetime.utcnow())
    booking_limit_date_is_in_the_future_predicate = (StockSQLEntity.bookingLimitDatetime > datetime.utcnow())
    has_no_beginning_date_predicate = (StockSQLEntity.beginningDatetime == None)
    has_no_booking_limit_date_predicate = (StockSQLEntity.bookingLimitDatetime == None)
    is_not_soft_deleted_predicate = (StockSQLEntity.isSoftDeleted == False)
    bookings_quantity = _build_bookings_quantity_subquery()
    has_remaining_stock = (StockSQLEntity.quantity == None) | (
            (StockSQLEntity.quantity - func.coalesce(bookings_quantity.c.quantity, 0)) > 0)

    stocks_query = stocks_query.outerjoin(bookings_quantity, StockSQLEntity.id == bookings_quantity.c.stockId) \
        .filter(is_not_soft_deleted_predicate
                & (beginning_date_is_in_the_future_predicate
                   | has_no_beginning_date_predicate)
                & (booking_limit_date_is_in_the_future_predicate
                   | has_no_booking_limit_date_predicate)
                & has_remaining_stock)
    return stocks_query


def get_offer_by_id(offer_id: int):
    return OfferSQLEntity.query.get(offer_id)


def get_offers_by_venue_id(venue_id: int) -> List[OfferSQLEntity]:
    return OfferSQLEntity.query \
        .filter_by(venueId=venue_id) \
        .all()


def get_offers_by_product_id(product_id: int) -> List[OfferSQLEntity]:
    return OfferSQLEntity.query \
        .filter_by(productId=product_id) \
        .all()


def get_offers_by_ids(offer_ids: List[int]) -> List[OfferSQLEntity]:
    return OfferSQLEntity.query \
        .filter(OfferSQLEntity.id.in_(offer_ids)) \
        .options(joinedload('stocks')) \
        .all()


def get_paginated_active_offer_ids(limit: int, page: int) -> List[tuple]:
    return OfferSQLEntity.query \
        .with_entities(OfferSQLEntity.id) \
        .filter(OfferSQLEntity.isActive == True) \
        .order_by(OfferSQLEntity.id) \
        .offset(page * limit) \
        .limit(limit) \
        .all()


def get_paginated_offer_ids_by_venue_id(venue_id: int, limit: int, page: int) -> List[tuple]:
    return OfferSQLEntity.query \
        .with_entities(OfferSQLEntity.id) \
        .filter(OfferSQLEntity.venueId == venue_id) \
        .order_by(OfferSQLEntity.id) \
        .offset(page * limit) \
        .limit(limit) \
        .all()


def get_paginated_offer_ids_by_venue_id_and_last_provider_id(last_provider_id: str,
                                                             limit: int,
                                                             page: int,
                                                             venue_id: int) -> List[tuple]:
    return OfferSQLEntity.query \
        .with_entities(OfferSQLEntity.id) \
        .filter(OfferSQLEntity.lastProviderId == last_provider_id) \
        .filter(OfferSQLEntity.venueId == venue_id) \
        .order_by(OfferSQLEntity.id) \
        .offset(page * limit) \
        .limit(limit) \
        .all()


def get_paginated_expired_offer_ids(limit: int, page: int) -> List[tuple]:
    one_day_before_now = datetime.utcnow() - timedelta(days=1)
    two_days_before_now = datetime.utcnow() - timedelta(days=2)
    start_limit = two_days_before_now <= func.max(StockSQLEntity.bookingLimitDatetime)
    end_limit = func.max(StockSQLEntity.bookingLimitDatetime) <= one_day_before_now

    return OfferSQLEntity.query \
        .join(StockSQLEntity) \
        .with_entities(OfferSQLEntity.id) \
        .filter(OfferSQLEntity.isActive == True) \
        .filter(StockSQLEntity.bookingLimitDatetime is not None) \
        .having(start_limit) \
        .having(end_limit) \
        .group_by(OfferSQLEntity.id) \
        .order_by(OfferSQLEntity.id) \
        .offset(page * limit) \
        .limit(limit) \
        .all()

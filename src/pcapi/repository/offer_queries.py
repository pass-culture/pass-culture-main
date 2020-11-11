from datetime import datetime
from typing import List
from typing import Optional

from flask_sqlalchemy import BaseQuery
from sqlalchemy import func
from sqlalchemy import nullsfirst
from sqlalchemy import or_
from sqlalchemy.orm import aliased
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.query import Query
from sqlalchemy.sql import selectable
from sqlalchemy.sql.elements import BinaryExpression

from pcapi.core.bookings.repository import get_only_offer_ids_from_bookings
from pcapi.core.offers.repository import get_offers_by_filters
from pcapi.domain.departments import ILE_DE_FRANCE_DEPT_CODES
from pcapi.models import Booking
from pcapi.models import DiscoveryView
from pcapi.models import DiscoveryViewV3
from pcapi.models import EventType
from pcapi.models import FavoriteSQLEntity
from pcapi.models import MediationSQLEntity
from pcapi.models import Offer
from pcapi.models import Offerer
from pcapi.models import SeenOffer
from pcapi.models import StockSQLEntity
from pcapi.models import ThingType
from pcapi.models import UserSQLEntity
from pcapi.models import VenueSQLEntity
from pcapi.models.db import Model
from pcapi.models.db import db
from pcapi.models.feature import FeatureToggle
from pcapi.repository import feature_queries
from pcapi.repository.favorite_queries import get_only_offer_ids_from_favorites
from pcapi.repository.iris_venues_queries import find_venues_located_near_iris
from pcapi.repository.venue_queries import get_only_venue_ids_for_department_codes
from pcapi.use_cases.diversify_recommended_offers import order_offers_by_diversified_types
from pcapi.utils.converter import from_tuple_to_int


ALL_DEPARTMENTS_CODE = "00"


def department_or_national_offers(query, departement_codes):
    if ALL_DEPARTMENTS_CODE in departement_codes:
        return query.filter((VenueSQLEntity.departementCode != None) | (Offer.isNational == True))

    query = query.filter(VenueSQLEntity.departementCode.in_(departement_codes) | (Offer.isNational == True))

    return query


def _bookable_offers(offers_query: Query) -> Query:
    stocks_query = StockSQLEntity.query.filter(StockSQLEntity.offerId == Offer.id)
    stocks_query = _filter_bookable_stocks_for_discovery(stocks_query)
    offers_query = offers_query.filter(stocks_query.exists())
    return offers_query


def _has_active_and_validated_offerer() -> BinaryExpression:
    return (Offerer.isActive == True) & (Offerer.validationToken == None)


def _with_active_and_validated_offerer(query):
    query = query.join(Offerer, Offerer.id == VenueSQLEntity.managingOffererId).filter(
        _has_active_and_validated_offerer()
    )
    return query


def _not_activation_offers(query):
    query = query.filter(Offer.type != str(EventType.ACTIVATION))
    return query.filter(Offer.type != str(ThingType.ACTIVATION))


def get_offers_for_recommendation(
    user: UserSQLEntity, departement_codes: List[str] = None, limit: int = None, sent_offers_ids: List[int] = []
) -> List[DiscoveryView]:
    favorite_ids = get_only_offer_ids_from_favorites(user)

    offer_booked_ids = get_only_offer_ids_from_bookings(user)

    discovery_view_query = (
        DiscoveryView.query.filter(DiscoveryView.id.notin_(favorite_ids))
        .filter(DiscoveryView.id.notin_(sent_offers_ids))
        .filter(DiscoveryView.id.notin_(offer_booked_ids))
    )

    if ALL_DEPARTMENTS_CODE not in departement_codes:
        venue_ids = get_only_venue_ids_for_department_codes(departement_codes)
        discovery_view_query = keep_only_offers_in_venues_or_national(discovery_view_query, venue_ids)

    if feature_queries.is_active(FeatureToggle.SAVE_SEEN_OFFERS):
        discovery_view_query = order_offers_by_unseen_offers_first(discovery_view_query, DiscoveryView, user)

    discovery_view_query = discovery_view_query.order_by(DiscoveryView.offerDiscoveryOrder)

    if limit:
        discovery_view_query = discovery_view_query.limit(limit)

    return order_offers_by_diversified_types(discovery_view_query.all())


def get_offers_for_recommendation_v3(
    user: UserSQLEntity,
    user_iris_id: Optional[int] = None,
    user_is_geolocated: bool = False,
    limit: Optional[int] = None,
    sent_offers_ids: List[int] = [],
) -> List[DiscoveryViewV3]:
    favorite_offers_ids = get_only_offer_ids_from_favorites(user)

    booked_offers_ids = get_only_offer_ids_from_bookings(user)

    discovery_view_query = (
        DiscoveryViewV3.query.filter(DiscoveryViewV3.id.notin_(favorite_offers_ids))
        .filter(DiscoveryViewV3.id.notin_(sent_offers_ids))
        .filter(DiscoveryViewV3.id.notin_(booked_offers_ids))
    )

    if user_is_geolocated:
        venue_ids = find_venues_located_near_iris(user_iris_id)
        discovery_view_query = keep_only_offers_from_venues_located_near_to_user_or_national(
            discovery_view_query, venue_ids
        )

    if feature_queries.is_active(FeatureToggle.SAVE_SEEN_OFFERS):
        discovery_view_query = order_offers_by_unseen_offers_first(discovery_view_query, DiscoveryViewV3, user)

    discovery_view_query = discovery_view_query.order_by(DiscoveryViewV3.offerDiscoveryOrder)

    if limit:
        discovery_view_query = discovery_view_query.limit(limit)

    return order_offers_by_diversified_types(discovery_view_query.all())


def order_offers_by_unseen_offers_first(query: BaseQuery, discovery_view_model: Model, user: UserSQLEntity):
    return query.outerjoin(
        SeenOffer, (SeenOffer.offerId == discovery_view_model.id) & (SeenOffer.userId == user.id)
    ).order_by(nullsfirst(SeenOffer.dateSeen))


def keep_only_offers_from_venues_located_near_to_user_or_national(
    query: BaseQuery, venue_ids: List[int] = []
) -> BaseQuery:
    return query.filter(or_(DiscoveryViewV3.venueId.in_(venue_ids), DiscoveryViewV3.isNational == True))


def keep_only_offers_in_venues_or_national(query: BaseQuery, venue_ids: selectable.Alias) -> BaseQuery:
    return query.filter(or_(DiscoveryView.venueId.in_(venue_ids), DiscoveryView.isNational == True))


def get_active_offers_ids_query(user, departement_codes=[ALL_DEPARTMENTS_CODE], offer_id=None):
    active_offers_query = Offer.query.distinct(Offer.id)

    if offer_id is not None:
        active_offers_query = active_offers_query.filter(Offer.id == offer_id)
    active_offers_query = active_offers_query.filter_by(isActive=True)
    active_offers_query = _with_validated_venue(active_offers_query)
    active_offers_query = _with_image(active_offers_query)
    active_offers_query = department_or_national_offers(active_offers_query, departement_codes)
    active_offers_query = _bookable_offers(active_offers_query)
    active_offers_query = _with_active_and_validated_offerer(active_offers_query)
    active_offers_query = _not_activation_offers(active_offers_query)
    if user:
        active_offers_query = _exclude_booked_and_favorite(active_offers_query, user)
    active_offer_ids = active_offers_query.with_entities(Offer.id).subquery()
    return active_offer_ids


def _exclude_booked_and_favorite(active_offers_query, user):
    booked_offer_ids = (
        Booking.query.filter_by(userId=user.id).join(StockSQLEntity).with_entities('stock."offerId"').subquery()
    )
    favorite_offer_ids = FavoriteSQLEntity.query.filter_by(userId=user.id).with_entities('"offerId"').subquery()
    not_booked_predicate = ~Offer.id.in_(booked_offer_ids)
    not_favorite_predicate = ~Offer.id.in_(favorite_offer_ids)

    active_offers_query = active_offers_query.filter(not_booked_predicate & not_favorite_predicate)

    return active_offers_query


def _with_image(offer_query):
    has_image_predicate = _build_has_active_mediation_predicate()
    return offer_query.filter(has_image_predicate)


def _with_validated_venue(offer_query):
    return offer_query.join(VenueSQLEntity, Offer.venueId == VenueSQLEntity.id).filter(
        VenueSQLEntity.validationToken == None
    )


def _build_has_active_mediation_predicate():
    return MediationSQLEntity.query.filter(
        (MediationSQLEntity.offerId == Offer.id) & MediationSQLEntity.isActive
    ).exists()


def find_searchable_offer(offer_id):
    return (
        Offer.query.filter_by(id=offer_id).join(VenueSQLEntity).filter(VenueSQLEntity.validationToken == None).first()
    )


def _offer_has_bookable_stocks():
    now = datetime.utcnow()
    stock_can_still_be_booked = (StockSQLEntity.bookingLimitDatetime > now) | (
        StockSQLEntity.bookingLimitDatetime == None
    )
    event_has_not_began_yet = (StockSQLEntity.beginningDatetime != None) & (StockSQLEntity.beginningDatetime > now)
    offer_is_on_a_thing = StockSQLEntity.beginningDatetime == None
    bookings_quantity = _build_bookings_quantity_subquery()

    return (
        StockSQLEntity.query.filter(StockSQLEntity.offerId == Offer.id)
        .filter(StockSQLEntity.isSoftDeleted == False)
        .filter(stock_can_still_be_booked)
        .filter(event_has_not_began_yet | offer_is_on_a_thing)
        .outerjoin(bookings_quantity, StockSQLEntity.id == bookings_quantity.c.stockId)
        .filter(
            (StockSQLEntity.quantity == None)
            | ((StockSQLEntity.quantity - func.coalesce(bookings_quantity.c.quantity, 0)) > 0)
        )
        .exists()
    )


def _build_bookings_quantity_subquery():
    stock_alias = aliased(StockSQLEntity)
    bookings_quantity = (
        Booking.query.join(stock_alias)
        .filter(Booking.isCancelled == False)
        .group_by(Booking.stockId)
        .with_entities(func.sum(Booking.quantity).label("quantity"), Booking.stockId.label("stockId"))
        .subquery()
    )
    return bookings_quantity


def _filter_recommendable_offers_for_search(offer_query):
    offer_query = (
        offer_query.reset_joinpoint()
        .filter(Offer.isActive == True)
        .filter(_has_active_and_validated_offerer())
        .filter(VenueSQLEntity.validationToken == None)
        .filter(_offer_has_bookable_stocks())
    )
    return offer_query


def find_activation_offers(departement_code: str) -> List[Offer]:
    departement_codes = ILE_DE_FRANCE_DEPT_CODES if departement_code == "93" else [departement_code]
    match_department_or_is_national = or_(
        VenueSQLEntity.departementCode.in_(departement_codes), Offer.isNational == True
    )

    query = (
        Offer.query.join(VenueSQLEntity)
        .join(StockSQLEntity, StockSQLEntity.offerId == Offer.id)
        .filter(Offer.type == str(EventType.ACTIVATION))
        .filter(match_department_or_is_national)
    )

    query = _filter_bookable_stocks_for_discovery(query)

    return query


def _filter_bookable_stocks_for_discovery(stocks_query):
    beginning_date_is_in_the_future_predicate = StockSQLEntity.beginningDatetime > datetime.utcnow()
    booking_limit_date_is_in_the_future_predicate = StockSQLEntity.bookingLimitDatetime > datetime.utcnow()
    has_no_beginning_date_predicate = StockSQLEntity.beginningDatetime == None
    has_no_booking_limit_date_predicate = StockSQLEntity.bookingLimitDatetime == None
    is_not_soft_deleted_predicate = StockSQLEntity.isSoftDeleted == False
    bookings_quantity = _build_bookings_quantity_subquery()
    has_remaining_stock = (StockSQLEntity.quantity == None) | (
        (StockSQLEntity.quantity - func.coalesce(bookings_quantity.c.quantity, 0)) > 0
    )

    stocks_query = stocks_query.outerjoin(bookings_quantity, StockSQLEntity.id == bookings_quantity.c.stockId).filter(
        is_not_soft_deleted_predicate
        & (beginning_date_is_in_the_future_predicate | has_no_beginning_date_predicate)
        & (booking_limit_date_is_in_the_future_predicate | has_no_booking_limit_date_predicate)
        & has_remaining_stock
    )
    return stocks_query


def get_offer_by_id(offer_id: int):
    return Offer.query.get(offer_id)


def get_offers_by_venue_id(venue_id: int) -> List[Offer]:
    return Offer.query.filter_by(venueId=venue_id).all()


def get_offers_by_product_id(product_id: int) -> List[Offer]:
    return Offer.query.filter_by(productId=product_id).all()


def get_offers_by_ids(offer_ids: List[int]) -> List[Offer]:
    return Offer.query.filter(Offer.id.in_(offer_ids)).options(joinedload("stocks")).all()


def get_paginated_active_offer_ids(limit: int, page: int) -> List[tuple]:
    return (
        Offer.query.with_entities(Offer.id)
        .filter(Offer.isActive == True)
        .order_by(Offer.id)
        .offset(page * limit)
        .limit(limit)
        .all()
    )


def get_paginated_offer_ids_by_venue_id(venue_id: int, limit: int, page: int) -> List[tuple]:
    return (
        Offer.query.with_entities(Offer.id)
        .filter(Offer.venueId == venue_id)
        .order_by(Offer.id)
        .offset(page * limit)
        .limit(limit)
        .all()
    )


def get_paginated_offer_ids_by_venue_id_and_last_provider_id(
    last_provider_id: str, limit: int, page: int, venue_id: int
) -> List[tuple]:
    return (
        Offer.query.with_entities(Offer.id)
        .filter(Offer.lastProviderId == last_provider_id)
        .filter(Offer.venueId == venue_id)
        .order_by(Offer.id)
        .offset(page * limit)
        .limit(limit)
        .all()
    )


def get_paginated_offer_ids_given_booking_limit_datetime_interval(
    limit: int, page: int, from_date: datetime, to_date: datetime
) -> List[tuple]:
    start_limit = from_date <= func.max(StockSQLEntity.bookingLimitDatetime)
    end_limit = func.max(StockSQLEntity.bookingLimitDatetime) <= to_date

    return (
        Offer.query.join(StockSQLEntity)
        .with_entities(Offer.id)
        .filter(Offer.isActive == True)
        .filter(StockSQLEntity.isSoftDeleted == False)
        .filter(StockSQLEntity.bookingLimitDatetime is not None)
        .having(start_limit)
        .having(end_limit)
        .group_by(Offer.id)
        .order_by(Offer.id)
        .offset(page * limit)
        .limit(limit)
        .all()
    )


def update_offers_is_active_status(offers_id: [int], is_active: bool) -> None:
    Offer.query.filter(Offer.id.in_(offers_id)).update({"isActive": is_active}, synchronize_session=False)
    db.session.commit()


def get_all_offers_id_by_filters(
    user_id: int,
    user_is_admin: bool,
    offerer_id: Optional[int] = None,
    status: Optional[str] = None,
    venue_id: Optional[int] = None,
    type_id: Optional[str] = None,
    name_keywords: Optional[str] = None,
    creation_mode: Optional[str] = None,
) -> List[int]:
    query = get_offers_by_filters(
        user_id=user_id,
        user_is_admin=user_is_admin,
        offerer_id=offerer_id,
        status=status,
        venue_id=venue_id,
        type_id=type_id,
        name_keywords=name_keywords,
        creation_mode=creation_mode,
    ).with_entities(Offer.id)

    offer_ids_as_tuple = query.all()
    offer_ids_as_int = from_tuple_to_int(offer_ids_as_tuple)

    return offer_ids_as_int

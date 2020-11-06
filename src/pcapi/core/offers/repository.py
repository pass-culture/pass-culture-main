import math
from datetime import datetime
from typing import Optional

from sqlalchemy import or_, func, case, not_
from sqlalchemy.orm import joinedload, aliased, Query
from sqlalchemy.sql.functions import coalesce

from pcapi.core.bookings.models import Booking
from pcapi.domain.pro_offers.paginated_offers_recap import PaginatedOffersRecap
from pcapi.domain.ts_vector import create_filter_on_ts_vector_matching_all_keywords
from pcapi.infrastructure.repository.pro_offers.paginated_offers_recap_domain_converter import (
    to_domain,
)
from pcapi.models import Offerer, Offer, UserOfferer, VenueSQLEntity, StockSQLEntity

INACTIVE_STATUS = 'inactive'
EXPIRED_STATUS = 'expired'
SOLD_OUT_STATUS = 'soldOut'
ACTIVE_STATUS = 'active'


def get_paginated_offers_for_offerer_venue_and_keywords(
        user_id: int,
        user_is_admin: bool,
        page: Optional[int],
        offers_per_page: int,
        offerer_id: Optional[int] = None,
        requested_status: Optional[str] = None,
        venue_id: Optional[int] = None,
        type_id: Optional[str] = None,
        name_keywords: Optional[str] = None,
) -> PaginatedOffersRecap:
    query = get_offers_by_filters(
        user_id=user_id,
        user_is_admin=user_is_admin,
        offerer_id=offerer_id,
        requested_status=requested_status,
        venue_id=venue_id,
        type_id=type_id,
        name_keywords=name_keywords,
    )

    query = query \
        .options(
            joinedload(Offer.venue)
            .joinedload(VenueSQLEntity.managingOfferer)
        ) \
        .options(
            joinedload(Offer.stocks)
            .joinedload(StockSQLEntity.bookings)
        ) \
        .options(
            joinedload(Offer.mediations)
        ) \
        .options(
            joinedload(Offer.product)
        ) \
        .order_by(Offer.id.desc()) \
        .paginate(page, per_page=offers_per_page, error_out=False)

    total_offers = query.total
    total_pages = math.ceil(total_offers / offers_per_page)

    # FIXME (cgaunet, 2020-11-03): we should not have serialization logic in the repository
    return to_domain(
        offers=query.items,
        current_page=query.page,
        total_pages=total_pages,
        total_offers=total_offers,
    )


def get_offers_by_filters(
        user_id: int,
        user_is_admin: bool,
        offerer_id: Optional[int] = None,
        requested_status: Optional[str] = None,
        venue_id: Optional[int] = None,
        type_id: Optional[str] = None,
        name_keywords: Optional[str] = None,
):
    datetime_now = datetime.utcnow()
    query = Offer.query

    if requested_status is not None:
        query = _filter_by_status(query, user_id, datetime_now, requested_status)
    if venue_id is not None:
        query = query.filter(Offer.venueId == venue_id)
    if type_id is not None:
        query = query.filter(Offer.type == type_id)
    if offerer_id is not None:
        venue_alias = aliased(VenueSQLEntity)
        query = query \
            .join(venue_alias) \
            .filter(venue_alias.managingOffererId == offerer_id)
    if not user_is_admin:
        query = (
            query.join(VenueSQLEntity)
                .join(Offerer)
                .join(UserOfferer)
                .filter(UserOfferer.userId == user_id)
                .filter(UserOfferer.validationToken == None)
        )
    if name_keywords is not None:
        name_keywords_filter = create_filter_on_ts_vector_matching_all_keywords(
            Offer.__name_ts_vector__, name_keywords
        )
        query = query.filter(name_keywords_filter)

    return query.distinct(Offer.id)


def _filter_by_status(query: Query, user_id: int, datetime_now: datetime, requested_status: str) -> Query:
    if requested_status == ACTIVE_STATUS:
        query = _filter_by_active_status(query, user_id, datetime_now)
    elif requested_status == SOLD_OUT_STATUS:
        query = _filter_by_sold_out_status(query, user_id, datetime_now)
    elif requested_status == EXPIRED_STATUS:
        query = query \
            .filter(Offer.isActive.is_(True)) \
            .join(StockSQLEntity) \
            .filter(StockSQLEntity.isSoftDeleted.is_(False)) \
            .group_by(Offer.id) \
            .having(func.max(StockSQLEntity.bookingLimitDatetime) < datetime_now)
    elif requested_status == INACTIVE_STATUS:
        query = query.filter(Offer.isActive.is_(False))
    return query


def _filter_by_sold_out_status(query, user_id, datetime_now):
    sold_out_offers = Offer.query \
        .filter(Offer.isActive.is_(True)) \
        .join(VenueSQLEntity) \
        .join(Offerer) \
        .join(UserOfferer) \
        .filter(UserOfferer.userId == user_id) \
        .filter(UserOfferer.validationToken == None) \
        .join(StockSQLEntity) \
        .filter(StockSQLEntity.isSoftDeleted.is_(False)) \
        .filter(or_(StockSQLEntity.beginningDatetime.is_(None), StockSQLEntity.bookingLimitDatetime >= datetime_now)) \
        .outerjoin(Booking, StockSQLEntity.id == Booking.stockId) \
        .group_by(Offer.id) \
        .having(func.sum(StockSQLEntity.quantity) == coalesce(func.sum(case([(Booking.isCancelled.is_(True), 0)], else_=Booking.quantity)), 0))
    query = query \
        .filter(Offer.isActive.is_(True)) \
        .filter(not_(Offer.stocks.any())) \
        .union_all(sold_out_offers)
    return query


def _filter_by_active_status(query, user_id, datetime_now):
    future_stocks_with_remaining_quantity = StockSQLEntity.query \
        .join(Offer) \
        .join(VenueSQLEntity) \
        .join(Offerer) \
        .join(UserOfferer) \
        .filter(UserOfferer.userId == user_id) \
        .filter(UserOfferer.validationToken == None) \
        .filter(StockSQLEntity.isSoftDeleted.is_(False)) \
        .filter(or_(StockSQLEntity.beginningDatetime.is_(None), StockSQLEntity.bookingLimitDatetime >= datetime_now)) \
        .outerjoin(Booking, StockSQLEntity.id == Booking.stockId) \
        .group_by(StockSQLEntity.id) \
        .having(or_(StockSQLEntity.quantity.is_(None), StockSQLEntity.quantity != coalesce(func.sum(case([(Booking.isCancelled.is_(True), 0)], else_=Booking.quantity)), 0))) \
        .subquery()
    query = query \
        .filter(Offer.isActive.is_(True)) \
        .join(future_stocks_with_remaining_quantity, Offer.id == future_stocks_with_remaining_quantity.c.offerId)
    return query

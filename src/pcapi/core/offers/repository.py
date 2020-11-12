from datetime import datetime
import math
from typing import Optional

from sqlalchemy import and_
from sqlalchemy import func
from sqlalchemy import not_
from sqlalchemy import or_
from sqlalchemy.orm import Query
from sqlalchemy.orm import aliased
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.functions import coalesce

from pcapi.core.bookings.models import Booking
from pcapi.domain.pro_offers.paginated_offers_recap import PaginatedOffersRecap
from pcapi.domain.ts_vector import create_filter_on_ts_vector_matching_all_keywords
from pcapi.infrastructure.repository.pro_offers.paginated_offers_recap_domain_converter import to_domain
from pcapi.models import Offer
from pcapi.models import Offerer
from pcapi.models import StockSQLEntity
from pcapi.models import UserOfferer
from pcapi.models import VenueSQLEntity


IMPORTED_CREATION_MODE = "imported"
MANUAL_CREATION_MODE = "manual"

INACTIVE_STATUS = "inactive"
EXPIRED_STATUS = "expired"
SOLD_OUT_STATUS = "soldOut"
ACTIVE_STATUS = "active"


def get_paginated_offers_for_offerer_venue_and_keywords(
    user_id: int,
    user_is_admin: bool,
    page: Optional[int],
    offers_per_page: int,
    offerer_id: Optional[int] = None,
    status: Optional[str] = None,
    venue_id: Optional[int] = None,
    type_id: Optional[str] = None,
    name_keywords: Optional[str] = None,
    creation_mode: Optional[str] = None,
) -> PaginatedOffersRecap:
    query = get_offers_by_filters(
        user_id=user_id,
        user_is_admin=user_is_admin,
        offerer_id=offerer_id,
        status=status,
        venue_id=venue_id,
        type_id=type_id,
        name_keywords=name_keywords,
        creation_mode=creation_mode,
    )

    query = (
        query.options(joinedload(Offer.venue).joinedload(VenueSQLEntity.managingOfferer))
        .options(joinedload(Offer.stocks).joinedload(StockSQLEntity.bookings))
        .options(joinedload(Offer.mediations))
        .options(joinedload(Offer.product))
        .order_by(Offer.id.desc())
        .paginate(page, per_page=offers_per_page, error_out=False)
    )

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
    status: Optional[str] = None,
    venue_id: Optional[int] = None,
    type_id: Optional[str] = None,
    name_keywords: Optional[str] = None,
    creation_mode: Optional[str] = None,
) -> Query:
    datetime_now = datetime.utcnow()
    query = Offer.query

    if not user_is_admin:
        query = (
            query.join(VenueSQLEntity)
            .join(Offerer)
            .join(UserOfferer)
            .filter(UserOfferer.userId == user_id)
            .filter(UserOfferer.validationToken == None)
        )
    if offerer_id is not None:
        venue_alias = aliased(VenueSQLEntity)
        query = query.join(venue_alias, Offer.venueId == venue_alias.id).filter(
            venue_alias.managingOffererId == offerer_id
        )
    if venue_id is not None:
        query = query.filter(Offer.venueId == venue_id)
    if creation_mode is not None:
        query = _filter_by_creation_mode(query, creation_mode)
    if type_id is not None:
        query = query.filter(Offer.type == type_id)
    if name_keywords is not None:
        name_keywords_filter = create_filter_on_ts_vector_matching_all_keywords(Offer.__name_ts_vector__, name_keywords)
        query = query.filter(name_keywords_filter)
    if status is not None:
        query = _filter_by_status(query, datetime_now, status)

    return query.distinct(Offer.id)


def _filter_by_creation_mode(query: Query, creation_mode: str) -> Query:
    if creation_mode == MANUAL_CREATION_MODE:
        query = query.filter(Offer.lastProviderId == None)
    if creation_mode == IMPORTED_CREATION_MODE:
        query = query.filter(Offer.lastProviderId != None)

    return query


def _filter_by_status(query: Query, datetime_now: datetime, status: str) -> Query:
    if status == ACTIVE_STATUS:
        query = (
            query.filter(Offer.isActive.is_(True))
            .join(StockSQLEntity)
            .filter(StockSQLEntity.isSoftDeleted.is_(False))
            .filter(
                or_(StockSQLEntity.beginningDatetime.is_(None), StockSQLEntity.bookingLimitDatetime >= datetime_now)
            )
            .outerjoin(Booking, and_(StockSQLEntity.id == Booking.stockId, Booking.isCancelled.is_(False)))
            .group_by(Offer.id, StockSQLEntity.id)
            .having(
                or_(
                    StockSQLEntity.quantity.is_(None),
                    StockSQLEntity.quantity != coalesce(func.sum(Booking.quantity), 0),
                )
            )
        )
    elif status == SOLD_OUT_STATUS:
        query = (
            query.filter(Offer.isActive.is_(True))
            .outerjoin(
                StockSQLEntity, and_(Offer.id == StockSQLEntity.offerId, not_(StockSQLEntity.isSoftDeleted.is_(True)))
            )
            .filter(
                or_(StockSQLEntity.beginningDatetime.is_(None), StockSQLEntity.bookingLimitDatetime >= datetime_now)
            )
            .filter(not_(and_(not_(StockSQLEntity.id.is_(None)), StockSQLEntity.quantity.is_(None))))
            .outerjoin(Booking, and_(StockSQLEntity.id == Booking.stockId, Booking.isCancelled.is_(False)))
            .group_by(Offer.id)
            .having(coalesce(func.sum(StockSQLEntity.quantity), 0) == coalesce(func.sum(Booking.quantity), 0))
        )
    elif status == EXPIRED_STATUS:
        query = (
            query.filter(Offer.isActive.is_(True))
            .join(StockSQLEntity)
            .filter(StockSQLEntity.isSoftDeleted.is_(False))
            .group_by(Offer.id)
            .having(func.max(StockSQLEntity.bookingLimitDatetime) < datetime_now)
        )
    elif status == INACTIVE_STATUS:
        query = query.filter(Offer.isActive.is_(False))
    return query

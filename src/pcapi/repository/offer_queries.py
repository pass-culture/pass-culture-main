from datetime import datetime
from typing import List

from sqlalchemy import func
from sqlalchemy.orm import aliased
from sqlalchemy.orm import joinedload

from pcapi.models import Booking
from pcapi.models import Offer
from pcapi.models import Stock


def _build_bookings_quantity_subquery():
    stock_alias = aliased(Stock)
    bookings_quantity = (
        Booking.query.join(stock_alias)
        .filter(Booking.isCancelled == False)
        .group_by(Booking.stockId)
        .with_entities(func.sum(Booking.quantity).label("quantity"), Booking.stockId.label("stockId"))
        .subquery()
    )
    return bookings_quantity


def filter_bookable_stocks_query(stocks_query):
    beginning_date_is_in_the_future_predicate = Stock.beginningDatetime > datetime.utcnow()
    booking_limit_date_is_in_the_future_predicate = Stock.bookingLimitDatetime > datetime.utcnow()
    has_no_beginning_date_predicate = Stock.beginningDatetime.is_(None)
    has_no_booking_limit_date_predicate = Stock.bookingLimitDatetime.is_(None)
    is_not_soft_deleted_predicate = Stock.isSoftDeleted.is_(False)
    bookings_quantity = _build_bookings_quantity_subquery()
    has_remaining_stock = (Stock.quantity.is_(None)) | (
        (Stock.quantity - func.coalesce(bookings_quantity.c.quantity, 0)) > 0
    )

    return stocks_query.outerjoin(bookings_quantity, Stock.id == bookings_quantity.c.stockId).filter(
        is_not_soft_deleted_predicate
        & (beginning_date_is_in_the_future_predicate | has_no_beginning_date_predicate)
        & (booking_limit_date_is_in_the_future_predicate | has_no_booking_limit_date_predicate)
        & has_remaining_stock
    )


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
        .filter(Offer.lastProviderId == last_provider_id)  # pylint: disable=comparison-with-callable
        .filter(Offer.venueId == venue_id)
        .order_by(Offer.id)
        .offset(page * limit)
        .limit(limit)
        .all()
    )


def get_paginated_offer_ids_given_booking_limit_datetime_interval(
    limit: int, page: int, from_date: datetime, to_date: datetime
) -> List[tuple]:
    start_limit = from_date <= func.max(Stock.bookingLimitDatetime)
    end_limit = func.max(Stock.bookingLimitDatetime) <= to_date

    return (
        Offer.query.join(Stock)
        .with_entities(Offer.id)
        .filter(Offer.isActive == True)
        .filter(Stock.isSoftDeleted == False)
        .filter(Stock.bookingLimitDatetime is not None)
        .having(start_limit)
        .having(end_limit)
        .group_by(Offer.id)
        .order_by(Offer.id)
        .offset(page * limit)
        .limit(limit)
        .all()
    )

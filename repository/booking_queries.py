from datetime import datetime
from typing import Set, List

from postgresql_audit.flask import versioning_manager
from sqlalchemy import and_, text, func

from domain.keywords import create_filter_matching_all_keywords_in_any_model, \
    create_get_filter_matching_ts_query_in_any_model
from domain.stocks import STOCK_DELETION_DELAY
from models import Booking, \
    Offer, \
    Stock, \
    User, \
    Product, \
    Venue, Offerer, ThingType, Payment
from models.api_errors import ResourceNotFound
from models.db import db
from utils.rest import query_with_order_by, check_order_by

get_filter_matching_ts_query_for_booking = create_get_filter_matching_ts_query_in_any_model(
    Product,
    Venue
)


def count_all_bookings() -> int:
    return Booking.query.count()


def count_bookings_by_departement(departement_code: str) -> int:
    return Booking.query \
        .join(User) \
        .filter(User.departementCode == departement_code) \
        .count()


def count_non_cancelled_bookings() -> int:
    return Booking.query.filter_by(isCancelled=False).count()


def count_non_cancelled_bookings_by_departement(departement_code: str) -> int:
    return Booking.query \
        .join(User) \
        .filter(Booking.isCancelled == False) \
        .filter(User.departementCode == departement_code) \
        .count()


def count_all_cancelled_bookings() -> int:
    return Booking.query.filter_by(isCancelled=True).count()


def count_all_cancelled_bookings_by_departement(departement_code: str) -> int:
    return Booking.query \
        .filter_by(isCancelled=True) \
        .join(User) \
        .filter(User.departementCode == departement_code) \
        .count()


def find_active_bookings_by_user_id(user_id) -> List[Booking]:
    return Booking.query \
        .filter_by(userId=user_id) \
        .filter_by(isCancelled=False) \
        .all()


def find_all_by_stock_id(stock) -> List[Booking]:
    return Booking.query.filter_by(stockId=stock.id).all()


def _filter_bookings_with_keywords_string(query, keywords_string):
    keywords_filter = create_filter_matching_all_keywords_in_any_model(
        get_filter_matching_ts_query_for_booking,
        keywords_string
    )
    query = query \
        .outerjoin(Product) \
        .outerjoin(Venue) \
        .filter(keywords_filter) \
        .reset_joinpoint()
    return query


def _filter_bookings_by_offerer_id(offerer_id):
    query = Booking.query.join(Stock) \
        .join(Offer) \
        .join(Venue) \
        .outerjoin(Product, and_(Offer.productId == Product.id)) \
        .filter(Venue.managingOffererId == offerer_id) \
        .reset_joinpoint()
    return query


def find_offerer_bookings_paginated(offerer_id, search=None, order_by=None, page=1):
    query = _filter_bookings_by_offerer_id(offerer_id)

    if search:
        query = _filter_bookings_with_keywords_string(query, search)

    if order_by:
        check_order_by(order_by)
        query = query_with_order_by(query, order_by)

    bookings = query.paginate(int(page), per_page=10, error_out=False) \
        .items

    return bookings


def find_all_offerer_bookings(offerer_id, venue_id=None, offer_id=None, date_from=None, date_to=None) -> List[Booking]:
    query = _filter_bookings_by_offerer_id(offerer_id)

    if venue_id:
        query = query.filter(Venue.id == venue_id)

    if offer_id:
        query = query.filter(Offer.id == offer_id)

        offer = Offer.query.filter(Offer.id == offer_id).first()

        if offer and offer.isEvent and date_from:
            query = query.filter(Stock.beginningDatetime == date_from)

        if offer and offer.isThing:
            if date_from:
                query = query.filter(Booking.dateCreated >= date_from)
            if date_to:
                query = query.filter(Booking.dateCreated <= date_to)

    bookings = query.all()

    return bookings


def find_all_digital_bookings_for_offerer(offerer_id, offer_id=None, date_from=None, date_to=None) -> List[Booking]:
    query = _filter_bookings_by_offerer_id(offerer_id)

    query = query.filter(Venue.isVirtual == True)

    if offer_id:
        query = query.filter(Offer.id == offer_id)

    if date_from:
        query = query.filter(Booking.dateCreated >= date_from)

    if date_to:
        query = query.filter(Booking.dateCreated <= date_to)

    return query.all()


def find_bookings_from_recommendation(reco, user) -> List[Booking]:
    booking_query = Booking.query \
        .join(Stock) \
        .join(Offer) \
        .filter(Booking.user == user) \
        .filter(Offer.id == reco.offerId)
    return booking_query.all()


def find_all_bookings_for_stock(stock) -> List[Booking]:
    return Booking.query.join(Stock).filter_by(id=stock.id).all()


def find_all_bookings_for_stock_and_user(stock, current_user) -> List[Booking]:
    return Booking.query \
        .filter_by(userId=current_user.id) \
        .filter_by(isCancelled=False) \
        .filter_by(stockId=stock.id) \
        .all()


def find_by(token: str, email: str = None, offer_id: int = None) -> Booking:
    query = Booking.query.filter_by(token=token)

    if email:
        query = query.join(User) \
            .filter(func.lower(User.email) == email.strip().lower())

    if offer_id:
        query_offer = Booking.query \
            .join(Stock) \
            .join(Offer) \
            .filter_by(id=offer_id)
        query = query.intersect_all(query_offer)

    booking = query.first()

    if booking is None:
        errors = ResourceNotFound()
        errors.add_error(
            'global',
            "Cette contremarque n'a pas été trouvée"
        )
        raise errors

    return booking


def find_by_id(booking_id) -> Booking:
    return Booking.query.filter_by(id=booking_id).first_or_404()


def find_all_ongoing_bookings_by_stock(stock) -> List[Booking]:
    return Booking.query.filter_by(stockId=stock.id, isCancelled=False, isUsed=False).all()


def _query_get_used_or_finished_bookings():
    booking_on_event_finished_more_than_two_days_ago = (datetime.utcnow() > Stock.endDatetime + STOCK_DELETION_DELAY)

    return Booking.query \
        .join(Stock) \
        .join(Offer) \
        .join(Venue) \
        .join(Offerer) \
        .filter(Booking.isCancelled == False) \
        .filter((Booking.isUsed == True) | booking_on_event_finished_more_than_two_days_ago)


def count_all_used_or_non_cancelled_bookings() -> int:
    query = _query_get_used_or_finished_bookings()

    return query \
        .count()


def count_all_used_or_finished_bookings_by_departement(departement_code: str) -> int:
    query = _query_get_used_or_finished_bookings() \
        .join(User).filter(User.departementCode == departement_code)

    return query \
        .count()


def find_final_offerer_bookings(offerer_id) -> List[Booking]:
    return _query_get_used_or_finished_bookings() \
        .filter(Offerer.id == offerer_id) \
        .reset_joinpoint() \
        .outerjoin(Payment) \
        .order_by(Payment.id, Booking.dateCreated.asc())


def find_eligible_bookings_for_offerer(offerer_id: int) -> List[Booking]:
    query = _query_get_used_or_finished_bookings()
    query = query \
        .filter(Offerer.id == offerer_id) \
        .reset_joinpoint() \
        .outerjoin(Payment) \
        .order_by(Payment.id, Booking.dateCreated.asc())

    return query.all()


def find_eligible_bookings_for_venue(venue_id: int) -> List[Booking]:
    query = _query_get_used_or_finished_bookings()
    query = query.filter(Venue.id == venue_id)
    return query.all()


def find_date_used(booking: Booking) -> datetime:
    Activity = versioning_manager.activity_cls
    find_by_id_and_is_used = "table_name='booking' " \
                             "AND verb='update' " \
                             "AND cast(old_data->>'id' AS INT) = %s " \
                             "AND cast(changed_data->>'isUsed' as boolean) = true" % booking.id

    activity = Activity.query.filter(text(find_by_id_and_is_used)).first()
    return activity.issued_at if activity else None


def find_user_activation_booking(user: User) -> User:
    return Booking.query \
        .join(User) \
        .join(Stock, Booking.stockId == Stock.id) \
        .join(Offer) \
        .join(Product) \
        .filter(Product.type == str(ThingType.ACTIVATION)) \
        .filter(User.id == user.id) \
        .first()


def get_existing_tokens() -> Set[str]:
    return set(map(lambda t: t[0], db.session.query(Booking.token).all()))

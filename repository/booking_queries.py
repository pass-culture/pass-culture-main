from datetime import datetime, timedelta
from typing import Set

from postgresql_audit.flask import versioning_manager
from sqlalchemy import and_, text, func
from sqlalchemy.orm import aliased

from domain.keywords import create_filter_matching_all_keywords_in_any_model, \
    create_get_filter_matching_ts_query_in_any_model
from models import ApiErrors, \
    Booking, \
    Event, \
    PcObject, \
    Offer, \
    Stock, \
    Thing, \
    User, \
    Venue, Offerer, ThingType
from models.api_errors import ResourceNotFound
from models.db import db
from utils.rest import query_with_order_by, check_order_by

get_filter_matching_ts_query_for_booking = create_get_filter_matching_ts_query_in_any_model(
    Event,
    Thing,
    Venue,
)


def find_active_bookings_by_user_id(user_id):
    return Booking.query \
        .filter_by(userId=user_id) \
        .filter_by(isCancelled=False) \
        .all()


def find_all_by_stock_id(stock):
    return Booking.query.filter_by(stockId=stock.id).all()


def filter_bookings_with_keywords_string(query, keywords_string):
    keywords_filter = create_filter_matching_all_keywords_in_any_model(
        get_filter_matching_ts_query_for_booking,
        keywords_string
    )
    query = query.outerjoin(Event) \
        .outerjoin(Thing) \
        .outerjoin(Venue) \
        .filter(keywords_filter) \
        .reset_joinpoint()
    return query


def find_offerer_bookings(offerer_id, search=None, order_by=None, page=1):
    query = Booking.query.join(Stock) \
        .join(Offer) \
        .join(Venue) \
        .outerjoin(Thing, and_(Offer.thingId == Thing.id)) \
        .outerjoin(Event, and_(Offer.eventId == Event.id)) \
        .filter(Venue.managingOffererId == offerer_id) \
        .reset_joinpoint()

    if search:
        query = filter_bookings_with_keywords_string(query, search)

    if order_by:
        check_order_by(order_by)
        query = query_with_order_by(query, order_by)

    bookings = query.paginate(int(page), per_page=10, error_out=False) \
        .items

    return bookings


def find_bookings_from_recommendation(reco, user):
    booking_query = Booking.query \
                           .join(Stock) \
                           .join(Offer) \
                           .filter(Booking.user == user) \
                           .filter(Offer.id == reco.offerId)
    return booking_query.all()


def find_all_bookings_for_stock(stock):
    return Booking.query.join(Stock).filter_by(id=stock.id).all()


def find_all_bookings_for_stock_and_user(stock, current_user):
    return Booking.query \
        .filter_by(userId=current_user.id) \
        .filter_by(isCancelled=False) \
        .filter_by(stockId=stock.id) \
        .all() \


def find_by(token: str, email: str = None, offer_id: int = None) -> Booking:
    query = Booking.query.filter_by(token=token)

    if email:
        query = query.join(User) \
            .filter(func.lower(User.email) == email.strip().lower())

    if offer_id:
        query_offer_1 = Booking.query.join(Stock) \
            .join(Offer) \
            .filter_by(id=offer_id)
        query_offer_2 = Booking.query.join(Stock) \
            .join(aliased(Offer)) \
            .filter_by(id=offer_id)
        query_offer = query_offer_1.union_all(query_offer_2)
        query = query.intersect_all(query_offer)

    booking = query.first()

    if booking is None:
        errors = ResourceNotFound()
        errors.addError(
            'global',
            "Cette contremarque n'a pas été trouvée"
        )
        raise errors

    return booking


def find_by_id(booking_id):
    return Booking.query.filter_by(id=booking_id).first_or_404()


def find_all_ongoing_bookings_by_stock(stock):
    return Booking.query.filter_by(stockId=stock.id, isCancelled=False, isUsed=False).all()


def find_final_offerer_bookings(offerer_id):
    booking_on_event_older_than_two_days = (datetime.utcnow() > Stock.beginningDatetime + timedelta(hours=48))

    return Booking.query \
        .join(Stock) \
        .join(Offer) \
        .join(Venue) \
        .join(Offerer) \
        .filter(Offerer.id == offerer_id) \
        .filter(Booking.isCancelled == False) \
        .filter((Booking.isUsed == True) | booking_on_event_older_than_two_days) \
        .all()


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
        .join(Thing) \
        .filter(Thing.type == str(ThingType.ACTIVATION)) \
        .filter(User.id == user.id) \
        .first()


def get_existing_tokens() -> Set[str]:
    return set(map(lambda t: t[0], db.session.query(Booking.token).all()))

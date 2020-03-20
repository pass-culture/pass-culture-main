from collections import namedtuple
from datetime import datetime, timedelta
from typing import List, Set, Union

from sqlalchemy import func
from sqlalchemy.orm import Query

from domain.stocks import STOCK_DELETION_DELAY
from models import Booking, EventType, Offer, Offerer, Payment, \
    Recommendation, Stock, ThingType, User, Venue
from models.api_errors import ResourceNotFoundError
from models.db import db
from repository import offer_queries


def _query_keep_on_non_activation_offers() -> Query:
    offer_types = ['ThingType.ACTIVATION', 'EventType.ACTIVATION']

    return Booking.query \
        .join(Stock) \
        .join(Offer) \
        .filter(~Offer.type.in_(offer_types))


def count() -> int:
    return _query_keep_on_non_activation_offers() \
        .count()


def count_by_departement(departement_code: str) -> int:
    return _query_keep_on_non_activation_offers() \
        .join(User, User.id == Booking.userId) \
        .filter(User.departementCode == departement_code) \
        .count()


def count_non_cancelled() -> int:
    return _query_non_cancelled_non_activation_bookings() \
        .count()


def count_non_cancelled_by_departement(departement_code: str) -> int:
    return _query_non_cancelled_non_activation_bookings() \
        .join(User, Booking.userId == User.id) \
        .filter(User.departementCode == departement_code) \
        .count()


def count_cancelled() -> int:
    return _query_cancelled_bookings_on_non_activation_offers() \
        .count()


def count_cancelled_by_departement(departement_code: str) -> int:
    return _query_cancelled_bookings_on_non_activation_offers() \
        .join(User) \
        .filter(User.departementCode == departement_code) \
        .count()


def _query_cancelled_bookings_on_non_activation_offers() -> Query:
    return _query_keep_on_non_activation_offers() \
        .filter(Booking.isCancelled == True)


def find_active_bookings_by_user_id(user_id: int) -> List[Booking]:
    return Booking.query \
        .filter_by(userId=user_id) \
        .filter_by(isCancelled=False) \
        .all()


def find_all_bookings_info(offerer_id: int,
                           venue_id: int = None,
                           offer_id: int = None,
                           date_from: Union[datetime, str] = None,
                           date_to: Union[datetime, str] = None,
                           only_digital_venues: bool = False) -> List[namedtuple]:
    query = _filter_bookings_by_offerer_id(offerer_id)

    if offer_id:
        query = query.filter(Offer.id == offer_id)
        offer = offer_queries.get_offer_by_id(offer_id)
        if offer and offer.isEvent and date_from:
            query = query.filter(Stock.beginningDatetime == date_from)

        if offer and offer.isThing:
            query = _filter_bookings_by_dates(query, date_from, date_to)

    if only_digital_venues:
        query = query.filter(Venue.isVirtual == True)
        query = _filter_bookings_by_dates(query, date_from, date_to)

    if venue_id:
        query = query.filter(Venue.id == venue_id)

    query = _select_only_needed_fields_for_bookings_info(query)
    return query.all()


def _filter_bookings_by_dates(query: Query, date_from: Union[datetime, str] = None,
                              date_to: Union[datetime, str] = None) -> Query:
    if date_from:
        query = query.filter(Booking.dateCreated >= date_from)
    if date_to:
        query = query.filter(Booking.dateCreated <= date_to)
    return query


def _select_only_needed_fields_for_bookings_info(query: Query) -> Query:
    return query.with_entities(Booking.id.label('id'),
                               Booking.dateCreated.label('date_created'),
                               Booking.quantity.label('quantity'),
                               Booking.amount.label('amount'),
                               Booking.isCancelled.label('isCancelled'),
                               Booking.isUsed.label('isUsed'),
                               Venue.name.label('venue_name'),
                               Offer.name.label('offer_name'),
                               User.lastName.label('user_lastname'),
                               User.firstName.label('user_firstname'),
                               User.email.label('user_email'))


def find_from_recommendation(recommendation: Recommendation, user: User) -> List[Booking]:
    return _query_keep_on_non_activation_offers() \
        .filter(Offer.id == recommendation.offerId) \
        .distinct(Booking.stockId) \
        .filter(Booking.userId == user.id) \
        .order_by(Booking.stockId, Booking.isCancelled, Booking.dateCreated.desc()) \
        .all()


def is_stock_already_booked_by_user(stock: Stock, current_user: User) -> bool:
    return Booking.query \
               .filter_by(userId=current_user.id) \
               .filter_by(isCancelled=False) \
               .filter_by(stockId=stock.id) \
               .count() > 0


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
        errors = ResourceNotFoundError()
        errors.add_error(
            'global',
            "Cette contremarque n'a pas été trouvée"
        )
        raise errors

    return booking


def find_by_id(booking_id: int) -> Booking:
    return Booking.query \
        .filter_by(id=booking_id) \
        .first_or_404()


def find_ongoing_bookings_by_stock(stock: Stock) -> List[Booking]:
    return Booking.query \
        .filter_by(stockId=stock.id, isCancelled=False, isUsed=False) \
        .all()


def find_eligible_bookings_for_offerer(offerer_id: int) -> List[Booking]:
    return _query_keep_only_used_or_finished_bookings_on_non_activation_offers() \
        .join(Offerer) \
        .filter(Offerer.id == offerer_id) \
        .reset_joinpoint() \
        .outerjoin(Payment) \
        .order_by(Payment.id, Booking.dateCreated.asc()) \
        .all()


def find_eligible_bookings_for_venue(venue_id: int) -> List[Booking]:
    return _query_keep_only_used_or_finished_bookings_on_non_activation_offers() \
        .filter(Venue.id == venue_id) \
        .reset_joinpoint() \
        .outerjoin(Payment) \
        .order_by(Payment.id, Booking.dateCreated.asc()) \
        .all()


def find_date_used(booking: Booking) -> datetime:
    return booking.dateUsed


def find_user_activation_booking(user: User) -> Booking:
    is_activation_offer = (Offer.type == str(ThingType.ACTIVATION)) | (
        Offer.type == str(EventType.ACTIVATION))

    return Booking.query \
        .join(User) \
        .join(Stock, Booking.stockId == Stock.id) \
        .join(Offer) \
        .filter(is_activation_offer) \
        .filter(User.id == user.id) \
        .first()


def find_existing_tokens() -> Set[str]:
    return set(map(lambda t: t[0], db.session.query(Booking.token).all()))


def _filter_bookings_by_offerer_id(offerer_id: int) -> Query:
    return Booking.query \
        .join(Stock) \
        .join(Offer) \
        .join(Venue) \
        .join(User) \
        .filter(Venue.managingOffererId == offerer_id) \
        .reset_joinpoint()


def _query_non_cancelled_non_activation_bookings() -> Query:
    return _query_keep_on_non_activation_offers() \
        .filter(Booking.isCancelled == False)


def _query_keep_only_used_or_finished_bookings_on_non_activation_offers() -> Query:
    booking_on_event_finished_more_than_two_days_ago = (
        datetime.utcnow() > Stock.endDatetime + STOCK_DELETION_DELAY)

    return _query_keep_on_non_activation_offers() \
        .join(Venue) \
        .filter(Booking.isCancelled == False) \
        .filter((Booking.isUsed == True) | booking_on_event_finished_more_than_two_days_ago)


def find_not_used_and_not_cancelled() -> List[Booking]:
    return Booking.query \
        .filter(Booking.isUsed == False) \
        .filter(Booking.isCancelled == False) \
        .all()


def find_for_my_bookings_page(user_id: int) -> List[Booking]:
    return _query_keep_on_non_activation_offers() \
        .distinct(Booking.stockId) \
        .filter(Booking.userId == user_id) \
        .order_by(Booking.stockId, Booking.isCancelled, Booking.dateCreated.desc()) \
        .all()


def get_only_offer_ids_from_bookings(user: User) -> List[int]:
    offers_booked = Offer.query \
        .join(Stock) \
        .join(Booking) \
        .filter_by(userId=user.id) \
        .with_entities(Offer.id) \
        .all()
    return [offer.id for offer in offers_booked]


def find_not_used_and_not_cancelled_bookings_associated_to_outdated_stock() -> List[Booking]:
    return Booking.query \
        .join(Stock) \
        .filter(Booking.isUsed == False) \
        .filter(Booking.isCancelled == False) \
        .filter(Stock.endDatetime + timedelta(hours=48) < datetime.utcnow()) \
        .all()


def find_used_by_token(token: str) -> Booking:
    return Booking.query \
        .filter_by(token=token) \
        .filter_by(isUsed=True) \
        .first()

def count_not_cancelled_bookings_quantity_by_stocks(stock_id: int) -> int:
    bookings =  Booking.query \
        .join(Stock) \
        .filter(Booking.isCancelled == False) \
        .filter(Booking.stockId == stock_id) \
        .all()

    return sum([booking.quantity for booking in bookings])


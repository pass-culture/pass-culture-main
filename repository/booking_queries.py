from collections import namedtuple
from datetime import datetime
from typing import List, Set, Union

from sqlalchemy import func
from sqlalchemy.orm import Query

from domain.booking_recap.booking_recap import BookingRecap, compute_booking_recap_status, compute_booking_recap_token
from models import UserOfferer
from models.api_errors import ResourceNotFoundError
from models.booking_sql_entity import BookingSQLEntity
from models.db import db
from models.offer import Offer
from models.offer_type import EventType, ThingType
from models.offerer import Offerer
from models.payment import Payment
from models.recommendation import Recommendation
from models.stock_sql_entity import StockSQLEntity, EVENT_AUTOMATIC_REFUND_DELAY
from models.user_sql_entity import UserSQLEntity
from models.venue import Venue
from repository import offer_queries

DUO_QUANTITY = 2


def _query_keep_on_non_activation_offers() -> Query:
    offer_types = ['ThingType.ACTIVATION', 'EventType.ACTIVATION']

    return BookingSQLEntity.query \
        .join(StockSQLEntity) \
        .join(Offer) \
        .filter(~Offer.type.in_(offer_types))


def count() -> int:
    return _query_keep_on_non_activation_offers() \
        .count()


def count_by_departement(departement_code: str) -> int:
    return _query_keep_on_non_activation_offers() \
        .join(UserSQLEntity, UserSQLEntity.id == BookingSQLEntity.userId) \
        .filter(UserSQLEntity.departementCode == departement_code) \
        .count()


def count_non_cancelled() -> int:
    return _query_non_cancelled_non_activation_bookings() \
        .count()


def count_non_cancelled_by_departement(departement_code: str) -> int:
    return _query_non_cancelled_non_activation_bookings() \
        .join(UserSQLEntity, BookingSQLEntity.userId == UserSQLEntity.id) \
        .filter(UserSQLEntity.departementCode == departement_code) \
        .count()


def count_cancelled() -> int:
    return _query_cancelled_bookings_on_non_activation_offers() \
        .count()


def count_cancelled_by_departement(departement_code: str) -> int:
    return _query_cancelled_bookings_on_non_activation_offers() \
        .join(UserSQLEntity) \
        .filter(UserSQLEntity.departementCode == departement_code) \
        .count()


def _query_cancelled_bookings_on_non_activation_offers() -> Query:
    return _query_keep_on_non_activation_offers() \
        .filter(BookingSQLEntity.isCancelled == True)


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
            query = query.filter(StockSQLEntity.beginningDatetime == date_from)

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
        query = query.filter(BookingSQLEntity.dateCreated >= date_from)
    if date_to:
        query = query.filter(BookingSQLEntity.dateCreated <= date_to)
    return query


def _select_only_needed_fields_for_bookings_info(query: Query) -> Query:
    return query.with_entities(BookingSQLEntity.id.label('id'),
                               BookingSQLEntity.dateCreated.label('date_created'),
                               BookingSQLEntity.quantity.label('quantity'),
                               BookingSQLEntity.amount.label('amount'),
                               BookingSQLEntity.isCancelled.label('isCancelled'),
                               BookingSQLEntity.isUsed.label('isUsed'),
                               Venue.name.label('venue_name'),
                               Offer.name.label('offer_name'),
                               UserSQLEntity.lastName.label('user_lastname'),
                               UserSQLEntity.firstName.label('user_firstname'),
                               UserSQLEntity.email.label('user_email'))


def find_from_recommendation(recommendation: Recommendation, user: UserSQLEntity) -> List[BookingSQLEntity]:
    return _query_keep_on_non_activation_offers() \
        .filter(Offer.id == recommendation.offerId) \
        .distinct(BookingSQLEntity.stockId) \
        .filter(BookingSQLEntity.userId == user.id) \
        .order_by(BookingSQLEntity.stockId, BookingSQLEntity.isCancelled, BookingSQLEntity.dateCreated.desc()) \
        .all()


def is_offer_already_booked_by_user(user_id: int, offer: Offer) -> bool:
    return BookingSQLEntity.query \
               .filter_by(userId=user_id) \
               .filter_by(isCancelled=False) \
               .join(StockSQLEntity) \
               .join(Offer) \
               .filter(Offer.id == offer.id) \
               .count() > 0


def find_by(token: str, email: str = None, offer_id: int = None) -> BookingSQLEntity:
    query = BookingSQLEntity.query.filter_by(token=token)

    if email:
        query = query.join(UserSQLEntity) \
            .filter(func.lower(UserSQLEntity.email) == email.strip().lower())

    if offer_id:
        query_offer = BookingSQLEntity.query \
            .join(StockSQLEntity) \
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


def find_by_id(booking_id: int) -> BookingSQLEntity:
    return BookingSQLEntity.query \
        .filter_by(id=booking_id) \
        .first_or_404()


def find_by_pro_user_id(user_id: int) -> List[BookingRecap]:
    bookings = BookingSQLEntity.query \
        .outerjoin(Payment) \
        .reset_joinpoint() \
        .join(UserSQLEntity) \
        .join(StockSQLEntity) \
        .join(Offer) \
        .join(Venue) \
        .join(Offerer) \
        .join(UserOfferer) \
        .filter(UserOfferer.userId == user_id) \
        .filter(UserOfferer.validationToken == None) \
        .with_entities(
            BookingSQLEntity.token.label("bookingToken"),
            Offer.name.label("offerName"),
            UserSQLEntity.firstName.label("beneficiaryFirstname"),
            UserSQLEntity.lastName.label("beneficiaryLastname"),
            UserSQLEntity.email.label("beneficiaryEmail"),
            BookingSQLEntity.dateCreated.label("bookingDate"),
            BookingSQLEntity.isCancelled.label("isCancelled"),
            BookingSQLEntity.isUsed.label("isUsed"),
            BookingSQLEntity.quantity.label("quantity"),
            Payment.currentStatus.label("paymentStatus"),
            Offer.type.label("offerType"),
    ).all()

    return _bookings_sql_entities_to_bookings_recap(bookings)


def _bookings_sql_entities_to_bookings_recap(bookings: List[object]) -> List[BookingRecap]:
    return [_serialize_booking_recap(booking) for booking in bookings]


def _bookings_sql_entities_to_bookings_recap(bookings: List[BookingSQLEntity]) -> List[BookingRecap]:
    return [_serialize_booking_recap(booking) for booking in bookings]


def _serialize_booking_recap(booking: object) -> BookingRecap:
    return BookingRecap(
        offer_name=booking.offerName,
        offer_type=booking.offerType,
        beneficiary_email=booking.beneficiaryEmail,
        beneficiary_firstname=booking.beneficiaryFirstname,
        beneficiary_lastname=booking.beneficiaryLastname,
        booking_token=compute_booking_recap_token(booking),
        booking_date=booking.bookingDate,
        booking_status=compute_booking_recap_status(booking),
        booking_is_duo=booking.quantity == DUO_QUANTITY,
    )


def find_ongoing_bookings_by_stock(stock: StockSQLEntity) -> List[BookingSQLEntity]:
    return BookingSQLEntity.query \
        .filter_by(stockId=stock.id, isCancelled=False, isUsed=False) \
        .all()


def find_not_cancelled_bookings_by_stock(stock: StockSQLEntity) -> List[BookingSQLEntity]:
    return BookingSQLEntity.query \
        .filter_by(stockId=stock.id, isCancelled=False) \
        .all()


def find_eligible_bookings_for_offerer(offerer_id: int) -> List[BookingSQLEntity]:
    return _query_keep_only_used_or_finished_bookings_on_non_activation_offers() \
        .join(Offerer) \
        .filter(Offerer.id == offerer_id) \
        .reset_joinpoint() \
        .outerjoin(Payment) \
        .order_by(Payment.id, BookingSQLEntity.dateCreated.asc()) \
        .all()


def find_eligible_bookings_for_venue(venue_id: int) -> List[BookingSQLEntity]:
    return _query_keep_only_used_or_finished_bookings_on_non_activation_offers() \
        .filter(Venue.id == venue_id) \
        .reset_joinpoint() \
        .outerjoin(Payment) \
        .order_by(Payment.id, BookingSQLEntity.dateCreated.asc()) \
        .all()


def find_date_used(booking: BookingSQLEntity) -> datetime:
    return booking.dateUsed


def find_user_activation_booking(user: UserSQLEntity) -> BookingSQLEntity:
    is_activation_offer = (Offer.type == str(ThingType.ACTIVATION)) | (
            Offer.type == str(EventType.ACTIVATION))

    return BookingSQLEntity.query \
        .join(UserSQLEntity) \
        .join(StockSQLEntity, BookingSQLEntity.stockId == StockSQLEntity.id) \
        .join(Offer) \
        .filter(is_activation_offer) \
        .filter(UserSQLEntity.id == user.id) \
        .first()


def find_existing_tokens() -> Set[str]:
    return set(map(lambda t: t[0], db.session.query(BookingSQLEntity.token).all()))


def _filter_bookings_by_offerer_id(offerer_id: int) -> Query:
    return BookingSQLEntity.query \
        .join(StockSQLEntity) \
        .join(Offer) \
        .join(Venue) \
        .join(UserSQLEntity) \
        .filter(Venue.managingOffererId == offerer_id) \
        .reset_joinpoint()


def _query_non_cancelled_non_activation_bookings() -> Query:
    return _query_keep_on_non_activation_offers() \
        .filter(BookingSQLEntity.isCancelled == False)


def _query_keep_only_used_or_finished_bookings_on_non_activation_offers() -> Query:
    return _query_keep_on_non_activation_offers() \
        .join(Venue) \
        .filter(BookingSQLEntity.isCancelled == False) \
        .filter(BookingSQLEntity.isUsed == True)


def find_not_used_and_not_cancelled() -> List[BookingSQLEntity]:
    return BookingSQLEntity.query \
        .filter(BookingSQLEntity.isUsed == False) \
        .filter(BookingSQLEntity.isCancelled == False) \
        .all()


def find_for_my_bookings_page(user_id: int) -> List[BookingSQLEntity]:
    return _query_keep_on_non_activation_offers() \
        .distinct(BookingSQLEntity.stockId) \
        .filter(BookingSQLEntity.userId == user_id) \
        .order_by(BookingSQLEntity.stockId, BookingSQLEntity.isCancelled, BookingSQLEntity.dateCreated.desc()) \
        .all()


def get_only_offer_ids_from_bookings(user: UserSQLEntity) -> List[int]:
    offers_booked = Offer.query \
        .join(StockSQLEntity) \
        .join(BookingSQLEntity) \
        .filter_by(userId=user.id) \
        .with_entities(Offer.id) \
        .all()
    return [offer.id for offer in offers_booked]


def find_not_used_and_not_cancelled_bookings_associated_to_outdated_stock() -> List[BookingSQLEntity]:
    booking_on_event_that_should_have_been_refunded = StockSQLEntity.beginningDatetime + EVENT_AUTOMATIC_REFUND_DELAY
    return BookingSQLEntity.query \
        .join(StockSQLEntity) \
        .filter(BookingSQLEntity.isUsed == False) \
        .filter(BookingSQLEntity.isCancelled == False) \
        .filter(booking_on_event_that_should_have_been_refunded < datetime.utcnow()) \
        .all()


def find_used_by_token(token: str) -> BookingSQLEntity:
    return BookingSQLEntity.query \
        .filter_by(token=token) \
        .filter_by(isUsed=True) \
        .first()


def count_not_cancelled_bookings_quantity_by_stock_id(stock_id: int) -> int:
    bookings = BookingSQLEntity.query \
        .join(StockSQLEntity) \
        .filter(BookingSQLEntity.isCancelled == False) \
        .filter(BookingSQLEntity.stockId == stock_id) \
        .all()

    return sum([booking.quantity for booking in bookings])

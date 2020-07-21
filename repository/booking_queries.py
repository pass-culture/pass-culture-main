import math
from collections import namedtuple
from datetime import datetime
from typing import List, Set, Union, Optional

from dateutil import tz
from sqlalchemy import func, desc, text
from sqlalchemy.orm import Query

from domain.booking_recap.booking_recap import BookingRecap, EventBookingRecap, ThingBookingRecap, BookBookingRecap
from domain.booking_recap.bookings_recap_paginated import BookingsRecapPaginated
from domain.postal_code.postal_code import PostalCode
from models import UserOfferer, BookingSQLEntity, StockSQLEntity, Offer
from models import VenueSQLEntity
from models.api_errors import ResourceNotFoundError
from models.booking_sql_entity import BookingSQLEntity
from models.db import db
from models.offer import Offer
from models.offer_type import EventType, ThingType
from models.offerer import Offerer
from models.payment import Payment
from models.payment_status import TransactionStatus
from models.recommendation import Recommendation
from models.stock_sql_entity import StockSQLEntity, EVENT_AUTOMATIC_REFUND_DELAY
from models.user_sql_entity import UserSQLEntity
from repository import offer_queries
from utils.date import get_department_timezone

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
        query = query.filter(VenueSQLEntity.isVirtual == True)
        query = _filter_bookings_by_dates(query, date_from, date_to)

    if venue_id:
        query = query.filter(VenueSQLEntity.id == venue_id)

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
                               VenueSQLEntity.name.label('venue_name'),
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


def find_by_pro_user_id(user_id: int, page: int = 1, per_page_limit: int = 1000) -> BookingsRecapPaginated:
    bookings_recap_query = _build_bookings_recap_query(user_id)
    bookings_recap_query_with_duplicates = _duplicate_booking_when_quantity_is_two(bookings_recap_query)

    total_bookings_recap = bookings_recap_query_with_duplicates.count()

    paginated_bookings = bookings_recap_query_with_duplicates \
        .order_by(text('"bookingDate" DESC')) \
        .offset((page - 1) * per_page_limit) \
        .limit(per_page_limit) \
        .all()

    return _paginated_bookings_sql_entities_to_bookings_recap(paginated_bookings=paginated_bookings,
                                                              page=page,
                                                              per_page_limit=per_page_limit,
                                                              total_bookings_recap=total_bookings_recap)


def _duplicate_booking_when_quantity_is_two(bookings_recap_query: Query) -> Query:
    return bookings_recap_query \
        .union_all(bookings_recap_query.filter(BookingSQLEntity.quantity == 2))


def _build_bookings_recap_query(user_id: int) -> Query:
    return BookingSQLEntity.query \
        .outerjoin(Payment) \
        .reset_joinpoint() \
        .join(UserSQLEntity) \
        .join(StockSQLEntity) \
        .join(Offer) \
        .join(VenueSQLEntity) \
        .join(Offerer) \
        .join(UserOfferer) \
        .filter(UserOfferer.userId == user_id) \
        .filter(UserOfferer.validationToken == None) \
        .with_entities(
            BookingSQLEntity.token.label("bookingToken"),
            BookingSQLEntity.dateCreated.label("bookingDate"),
            BookingSQLEntity.isCancelled.label("isCancelled"),
            BookingSQLEntity.isUsed.label("isUsed"),
            BookingSQLEntity.quantity.label("quantity"),
            BookingSQLEntity.amount.label("bookingAmount"),
            BookingSQLEntity.dateUsed.label("dateUsed"),
            BookingSQLEntity.cancellationDate.label("cancellationDate"),
            Offer.name.label("offerName"),
            Offer.id.label("offerId"),
            Offer.extraData.label("offerExtraData"),
            Payment.currentStatus.label("paymentStatus"),
            Payment.lastProcessedDate.label("paymentDate"),
            UserSQLEntity.firstName.label("beneficiaryFirstname"),
            UserSQLEntity.lastName.label("beneficiaryLastname"),
            UserSQLEntity.email.label("beneficiaryEmail"),
            StockSQLEntity.beginningDatetime.label('stockBeginningDatetime'),
            VenueSQLEntity.departementCode.label('venueDepartementCode'),
            Offerer.name.label('offererName'),
            Offerer.postalCode.label('offererPostalCode'),
            VenueSQLEntity.id.label('venueId'),
            VenueSQLEntity.name.label('venueName'),
            VenueSQLEntity.publicName.label('venuePublicName'),
            VenueSQLEntity.isVirtual.label('venueIsVirtual'),
        )


def _paginated_bookings_sql_entities_to_bookings_recap(paginated_bookings: List[object],
                                                       page: int,
                                                       per_page_limit: int,
                                                       total_bookings_recap: int) -> BookingsRecapPaginated:
    return BookingsRecapPaginated(
        bookings_recap=[_serialize_booking_recap(booking) for booking in paginated_bookings],
        page=page,
        pages=int(math.ceil(total_bookings_recap / per_page_limit)),
        total=total_bookings_recap,
    )


def _apply_departement_timezone(date: datetime, departement_code: str) -> datetime:
    return date.astimezone(tz.gettz(get_department_timezone(departement_code))) if date is not None else None


def _serialize_date_with_timezone(date_without_timezone: datetime, booking: object) -> datetime:
    if booking.venueDepartementCode:
        return _apply_departement_timezone(date=date_without_timezone,
                                           departement_code=booking.venueDepartementCode)
    offerer_department_code = PostalCode(booking.offererPostalCode).get_departement_code()
    return _apply_departement_timezone(date=date_without_timezone,
                                       departement_code=offerer_department_code)


def _serialize_booking_recap(booking: object) -> BookingRecap:
    if booking.stockBeginningDatetime:
        return _serialize_event_booking_recap(booking)

    if booking.offerExtraData and 'isbn' in booking.offerExtraData:
        return _serialize_book_booking_recap(booking)

    return _serialize_thing_booking_recap(booking)


def _serialize_thing_booking_recap(booking: object) -> ThingBookingRecap:
    return ThingBookingRecap(
        offer_identifier=booking.offerId,
        offer_name=booking.offerName,
        offerer_name=booking.offererName,
        beneficiary_email=booking.beneficiaryEmail,
        beneficiary_firstname=booking.beneficiaryFirstname,
        beneficiary_lastname=booking.beneficiaryLastname,
        booking_amount=booking.bookingAmount,
        booking_token=booking.bookingToken,
        booking_date=_serialize_date_with_timezone(date_without_timezone=booking.bookingDate, booking=booking),
        booking_is_used=booking.isUsed,
        booking_is_cancelled=booking.isCancelled,
        booking_is_reimbursed=booking.paymentStatus == TransactionStatus.SENT,
        booking_is_duo=booking.quantity == DUO_QUANTITY,
        venue_identifier=booking.venueId,
        date_used=_serialize_date_with_timezone(date_without_timezone=booking.dateUsed, booking=booking),
        payment_date=_serialize_date_with_timezone(date_without_timezone=booking.paymentDate, booking=booking),
        cancellation_date=_serialize_date_with_timezone(date_without_timezone=booking.cancellationDate, booking=booking),
        venue_name=booking.venuePublicName if booking.venuePublicName else booking.venueName,
        venue_is_virtual=booking.venueIsVirtual
    )


def _serialize_book_booking_recap(booking: object) -> BookBookingRecap:
    return BookBookingRecap(
        offer_identifier=booking.offerId,
        offer_name=booking.offerName,
        offerer_name=booking.offererName,
        offer_isbn=booking.offerExtraData['isbn'],
        beneficiary_email=booking.beneficiaryEmail,
        beneficiary_firstname=booking.beneficiaryFirstname,
        beneficiary_lastname=booking.beneficiaryLastname,
        booking_amount=booking.bookingAmount,
        booking_token=booking.bookingToken,
        booking_date=_serialize_date_with_timezone(date_without_timezone=booking.bookingDate, booking=booking),
        booking_is_used=booking.isUsed,
        booking_is_cancelled=booking.isCancelled,
        booking_is_reimbursed=booking.paymentStatus == TransactionStatus.SENT,
        booking_is_duo=booking.quantity == DUO_QUANTITY,
        venue_identifier=booking.venueId,
        date_used=_serialize_date_with_timezone(date_without_timezone=booking.dateUsed, booking=booking),
        payment_date=_serialize_date_with_timezone(date_without_timezone=booking.paymentDate, booking=booking),
        cancellation_date=_serialize_date_with_timezone(date_without_timezone=booking.cancellationDate, booking=booking),
        venue_name=booking.venuePublicName if booking.venuePublicName else booking.venueName,
        venue_is_virtual=booking.venueIsVirtual
    )


def _serialize_event_booking_recap(booking: object) -> EventBookingRecap:
    return EventBookingRecap(
        offer_identifier=booking.offerId,
        offer_name=booking.offerName,
        offerer_name=booking.offererName,
        beneficiary_email=booking.beneficiaryEmail,
        beneficiary_firstname=booking.beneficiaryFirstname,
        beneficiary_lastname=booking.beneficiaryLastname,
        booking_amount=booking.bookingAmount,
        booking_token=booking.bookingToken,
        booking_date=_serialize_date_with_timezone(date_without_timezone=booking.bookingDate, booking=booking),
        booking_is_used=booking.isUsed,
        booking_is_cancelled=booking.isCancelled,
        booking_is_reimbursed=booking.paymentStatus == TransactionStatus.SENT,
        booking_is_duo=booking.quantity == DUO_QUANTITY,
        event_beginning_datetime=_apply_departement_timezone(
            date=booking.stockBeginningDatetime,
            departement_code=booking.venueDepartementCode
        ),
        date_used=_serialize_date_with_timezone(date_without_timezone=booking.dateUsed, booking=booking),
        payment_date=_serialize_date_with_timezone(date_without_timezone=booking.paymentDate, booking=booking),
        cancellation_date=_serialize_date_with_timezone(date_without_timezone=booking.cancellationDate, booking=booking),
        venue_identifier=booking.venueId,
        venue_name=booking.venuePublicName if booking.venuePublicName else booking.venueName,
        venue_is_virtual=booking.venueIsVirtual
    )


def find_ongoing_bookings_by_stock(stock_id: int) -> List[BookingSQLEntity]:
    return BookingSQLEntity.query \
        .filter_by(stockId=stock_id, isCancelled=False, isUsed=False) \
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
        .filter(VenueSQLEntity.id == venue_id) \
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
        .join(VenueSQLEntity) \
        .join(UserSQLEntity) \
        .filter(VenueSQLEntity.managingOffererId == offerer_id) \
        .reset_joinpoint()


def _query_non_cancelled_non_activation_bookings() -> Query:
    return _query_keep_on_non_activation_offers() \
        .filter(BookingSQLEntity.isCancelled == False)


def _query_keep_only_used_or_finished_bookings_on_non_activation_offers() -> Query:
    return _query_keep_on_non_activation_offers() \
        .join(VenueSQLEntity) \
        .filter(BookingSQLEntity.isCancelled == False) \
        .filter(BookingSQLEntity.isUsed == True)


def find_not_used_and_not_cancelled() -> List[BookingSQLEntity]:
    return BookingSQLEntity.query \
        .filter(BookingSQLEntity.isUsed == False) \
        .filter(BookingSQLEntity.isCancelled == False) \
        .all()


def find_for_my_bookings_page(user_id: int) -> List[BookingSQLEntity]:
    offer_types = ['ThingType.ACTIVATION', 'EventType.ACTIVATION']
    return BookingSQLEntity.query \
        .join(StockSQLEntity) \
        .join(Offer) \
        .filter(~Offer.type.in_(offer_types)) \
        .distinct(BookingSQLEntity.stockId) \
        .filter(BookingSQLEntity.userId == user_id) \
        .order_by(BookingSQLEntity.stockId,
                  BookingSQLEntity.isCancelled,
                  BookingSQLEntity.dateCreated.desc()
                  ) \
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


def find_first_matching_from_offer_by_user(offer_id: int, user_id: int) -> Optional[BookingSQLEntity]:
    return BookingSQLEntity.query \
        .filter_by(userId=user_id) \
        .join(StockSQLEntity) \
        .filter(StockSQLEntity.offerId == offer_id) \
        .order_by(desc(BookingSQLEntity.dateCreated)) \
        .first()

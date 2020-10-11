from datetime import datetime
import math
from typing import List, Optional, Set

from dateutil import tz
from sqlalchemy import desc, func, text
from sqlalchemy.orm import Query, joinedload, selectinload

from pcapi.domain.booking_recap.booking_recap import BookBookingRecap, BookingRecap, EventBookingRecap, ThingBookingRecap
from pcapi.domain.booking_recap.bookings_recap_paginated import BookingsRecapPaginated
import pcapi.domain.expenses
from pcapi.domain.postal_code.postal_code import PostalCode
from pcapi.models import UserOfferer, VenueSQLEntity
from pcapi.models.api_errors import ResourceNotFoundError
from pcapi.core.bookings.models import BookingSQLEntity
from pcapi.models.db import db
from pcapi.models.offer_sql_entity import OfferSQLEntity
from pcapi.models.offer_type import EventType, ThingType
from pcapi.models.offerer import Offerer
from pcapi.models.payment import Payment
from pcapi.models.payment_status import TransactionStatus
from pcapi.models.recommendation import Recommendation
from pcapi.models.stock_sql_entity import StockSQLEntity
from pcapi.models.user_sql_entity import UserSQLEntity
from pcapi.utils.date import get_department_timezone

DUO_QUANTITY = 2


def _query_keep_on_non_activation_offers() -> Query:
    offer_types = ['ThingType.ACTIVATION', 'EventType.ACTIVATION']

    return BookingSQLEntity.query \
        .join(StockSQLEntity) \
        .join(OfferSQLEntity) \
        .filter(~OfferSQLEntity.type.in_(offer_types))


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


def find_from_recommendation(recommendation: Recommendation, user_id: int) -> List[BookingSQLEntity]:
    return _build_find_ordered_user_bookings(user_id=user_id) \
        .filter(OfferSQLEntity.id == recommendation.offerId) \
        .all()


def is_offer_already_booked_by_user(user_id: int, offer: OfferSQLEntity) -> bool:
    return BookingSQLEntity.query \
               .filter_by(userId=user_id) \
               .filter_by(isCancelled=False) \
               .join(StockSQLEntity) \
               .join(OfferSQLEntity) \
               .filter(OfferSQLEntity.id == offer.id) \
               .count() > 0


def find_by(token: str, email: str = None, offer_id: int = None) -> BookingSQLEntity:
    query = BookingSQLEntity.query.filter_by(token=token)

    if email:
        query = query.join(UserSQLEntity) \
            .filter(func.lower(UserSQLEntity.email) == email.strip().lower())

    if offer_id:
        query_offer = BookingSQLEntity.query \
            .join(StockSQLEntity) \
            .join(OfferSQLEntity) \
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
        .join(OfferSQLEntity) \
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
        OfferSQLEntity.name.label("offerName"),
        OfferSQLEntity.id.label("offerId"),
        OfferSQLEntity.extraData.label("offerExtraData"),
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
        cancellation_date=_serialize_date_with_timezone(date_without_timezone=booking.cancellationDate,
                                                        booking=booking),
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
        cancellation_date=_serialize_date_with_timezone(date_without_timezone=booking.cancellationDate,
                                                        booking=booking),
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
        cancellation_date=_serialize_date_with_timezone(date_without_timezone=booking.cancellationDate,
                                                        booking=booking),
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
    is_activation_offer = (OfferSQLEntity.type == str(ThingType.ACTIVATION)) | (
            OfferSQLEntity.type == str(EventType.ACTIVATION))

    return BookingSQLEntity.query \
        .join(UserSQLEntity) \
        .join(StockSQLEntity, BookingSQLEntity.stockId == StockSQLEntity.id) \
        .join(OfferSQLEntity) \
        .filter(is_activation_offer) \
        .filter(UserSQLEntity.id == user.id) \
        .first()


def find_existing_tokens() -> Set[str]:
    return set(map(lambda t: t[0], db.session.query(BookingSQLEntity.token).all()))


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


def find_user_bookings_for_recommendation(user_id: int) -> List[BookingSQLEntity]:
    return _build_find_ordered_user_bookings(user_id) \
        .all()


def get_only_offer_ids_from_bookings(user: UserSQLEntity) -> List[int]:
    offers_booked = OfferSQLEntity.query \
        .join(StockSQLEntity) \
        .join(BookingSQLEntity) \
        .filter_by(userId=user.id) \
        .with_entities(OfferSQLEntity.id) \
        .all()
    return [offer.id for offer in offers_booked]


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


def _build_find_ordered_user_bookings(user_id: int) -> Query:
    return BookingSQLEntity.query \
        .join(StockSQLEntity) \
        .join(OfferSQLEntity) \
        .distinct(BookingSQLEntity.stockId) \
        .filter(BookingSQLEntity.userId == user_id) \
        .order_by(BookingSQLEntity.stockId, BookingSQLEntity.isCancelled, BookingSQLEntity.dateCreated.desc()) \
        .options(
        selectinload(BookingSQLEntity.stock)
    )


def get_user_expenses(user: UserSQLEntity) -> dict:
    bookings = (
        BookingSQLEntity.query
        .filter_by(user=user)
        .filter_by(isCancelled=False)
        .options(
            joinedload(BookingSQLEntity.stock).
            joinedload(StockSQLEntity.offer)
        )
        .all()
    )
    return pcapi.domain.expenses.get_expenses(bookings)

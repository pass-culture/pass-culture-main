import csv
from datetime import date
from datetime import datetime
from datetime import time
from io import StringIO
import math
from typing import Callable
from typing import Iterable
from typing import Optional

from dateutil import tz
from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import case
from sqlalchemy import cast
from sqlalchemy import func
from sqlalchemy import or_
from sqlalchemy import text
from sqlalchemy.orm import Query
from sqlalchemy.orm import contains_eager
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.sql.functions import coalesce
from sqlalchemy.util._collections import AbstractKeyedTuple

from pcapi.core.bookings import constants
from pcapi.core.bookings.models import BookingCancellationReasons
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.bookings.models import IndividualBooking
from pcapi.core.categories import subcategories
from pcapi.core.educational.models import EducationalBooking
from pcapi.core.educational.models import EducationalRedactor
from pcapi.core.offerers.models import Offerer
from pcapi.core.users.models import User
from pcapi.core.users.utils import sanitize_email
from pcapi.domain.booking_recap.booking_recap import BookingRecap
from pcapi.domain.booking_recap.booking_recap import BookingRecapLegacy
from pcapi.domain.booking_recap.bookings_recap_paginated import BookingsRecapPaginated
from pcapi.domain.postal_code.postal_code import PostalCode
from pcapi.models import Booking
from pcapi.models import Offer
from pcapi.models import Stock
from pcapi.models import UserOfferer
from pcapi.models import Venue
from pcapi.models.api_errors import ResourceNotFoundError
from pcapi.models.db import db
from pcapi.models.feature import FeatureToggle
from pcapi.models.payment import Payment
from pcapi.models.payment_status import TransactionStatus
from pcapi.utils.date import get_department_timezone
from pcapi.utils.db import get_batches
from pcapi.utils.token import random_token


DUO_QUANTITY = 2


BOOKING_STATUS_LABELS = {
    BookingStatus.PENDING: "réservé",
    BookingStatus.CONFIRMED: "confirmé",
    BookingStatus.CANCELLED: "annulé",
    BookingStatus.USED: "validé",
    BookingStatus.REIMBURSED: "remboursé",
}


def find_by(token: str, email: str = None, offer_id: int = None) -> Booking:
    query = Booking.query.filter_by(token=token.upper())
    offer_is_educational = query.join(Stock).join(Offer).with_entities(Offer.isEducational).scalar()

    if email:
        # FIXME (dbaty, 2021-05-02): remove call to `func.lower()` once
        # all emails have been sanitized in the database.
        if not offer_is_educational:
            query = (
                query.join(IndividualBooking)
                .join(IndividualBooking.user)
                .filter(func.lower(User.email) == sanitize_email(email))
            )
        elif offer_is_educational:
            query = (
                query.join(EducationalBooking)
                .join(EducationalBooking.educationalRedactor)
                .filter(func.lower(EducationalBooking.educationalRedactor.email) == sanitize_email(email))
            )

    if offer_id:
        query = query.join(Stock).join(Offer).filter(Offer.id == offer_id)

    booking = query.one_or_none()

    if booking is None:
        errors = ResourceNotFoundError()
        errors.add_error("global", "Cette contremarque n'a pas été trouvée")
        raise errors

    return booking


def find_by_pro_user(
    user: User,
    booking_period: tuple[date, date],
    event_date: Optional[datetime] = None,
    venue_id: Optional[int] = None,
    page: int = 1,
    per_page_limit: int = 1000,
) -> BookingsRecapPaginated:
    # TODO: remove this block when IMPROVE_BOOKINGS_PERF is definitely adopted
    if not FeatureToggle.IMPROVE_BOOKINGS_PERF.is_active():
        sorted_booking_period = sorted(booking_period)
        bookings_recap_subquery = _filter_bookings_recap_subquery(user, sorted_booking_period, event_date, venue_id)

        if page == 1:
            total_bookings_recap = db.session.query(
                func.coalesce(func.sum(bookings_recap_subquery.c.quantity), 0)
            ).scalar()
        else:
            total_bookings_recap = 0

        bookings_recap_query = _build_bookings_recap_query(bookings_recap_subquery)
        bookings_recap_query_with_duplicates = _duplicate_booking_when_quantity_is_two_legacy(
            bookings_recap_query, bookings_recap_subquery
        )
        paginated_bookings = (
            bookings_recap_query_with_duplicates.order_by(text('"bookingDate" DESC'))
            .offset((page - 1) * per_page_limit)
            .limit(per_page_limit)
            .all()
        )

        return _paginated_bookings_sql_entities_to_bookings_recap(
            paginated_bookings=paginated_bookings,
            page=page,
            per_page_limit=per_page_limit,
            total_bookings_recap=total_bookings_recap,
            serializer=_serialize_booking_recap_legacy,
        )

    total_bookings_recap = _get_filtered_bookings_count(user, booking_period, event_date, venue_id)

    bookings_query = _get_filtered_booking_pro(
        pro_user=user,
        period=booking_period,
        event_date=event_date,
        venue_id=venue_id,
    )
    bookings_query = _duplicate_booking_when_quantity_is_two(bookings_query)
    bookings_page = (
        bookings_query.order_by(text('"bookedAt" DESC')).offset((page - 1) * per_page_limit).limit(per_page_limit).all()
    )

    return _paginated_bookings_sql_entities_to_bookings_recap(
        paginated_bookings=bookings_page,
        page=page,
        per_page_limit=per_page_limit,
        total_bookings_recap=total_bookings_recap,
    )


def find_ongoing_bookings_by_stock(stock_id: int) -> list[Booking]:
    return Booking.query.filter_by(stockId=stock_id, isCancelled=False, isUsed=False).all()


def find_not_cancelled_bookings_by_stock(stock: Stock) -> list[Booking]:
    return Booking.query.filter_by(stockId=stock.id, isCancelled=False).all()


def find_bookings_eligible_for_payment_for_venue(venue_id: int, cutoff_date: datetime) -> list[Booking]:
    bookings = Booking.query
    # There should not be any booking that is both cancelled and used,
    # but here we want to be extra cautious.
    bookings = bookings.filter_by(isCancelled=False, isUsed=True)
    bookings = bookings.filter_by(venueId=venue_id)
    # fmt: off
    bookings = (
        bookings
        .filter(Booking.dateUsed < cutoff_date, Booking.amount > 0)
        .join(Stock)
        .filter(
            Stock.beginningDatetime.is_(None)
            | (cast(Stock.beginningDatetime, Date) < date.today())
        )
    )
    # fmt: on
    return (
        bookings.outerjoin(Payment)
        .options(contains_eager(Booking.stock).joinedload(Stock.offer).joinedload(Offer.product))
        # FIXME (dbaty, 2021-08-18): `create_payment_for_booking` goes
        # through `Booking.venue.iban` to access the IBAN of the
        # venue. Could there be a way to avoid the JOIN on venue?
        # (Unfortunately, The JOIN on offerer is necessary, since
        # `create_payment_for_booking()` uses `Offerer.name` and
        # `Offerer.siren`.) Also, the two lines below make 2 distinct
        # JOIN on `bank_information`.
        .options(joinedload(Booking.venue).joinedload(Venue.bankInformation))
        .options(joinedload(Booking.offerer).joinedload(Offerer.bankInformation))
        .options(joinedload(Booking.payments))
        .order_by(Payment.id, Booking.dateUsed.asc())
        .all()
    )


def token_exists(token: str) -> bool:
    return db.session.query(Booking.query.filter_by(token=token.upper()).exists()).scalar()


def find_not_used_and_not_cancelled() -> list[Booking]:
    return Booking.query.filter_by(isUsed=False, isCancelled=False).all()


def find_used_by_token(token: str) -> Booking:
    return Booking.query.filter_by(token=token.upper(), isUsed=True).one_or_none()


def find_expiring_individual_bookings_query() -> Query:
    today_at_midnight = datetime.combine(date.today(), time(0, 0))
    return (
        IndividualBooking.query.join(Booking)
        .join(Stock)
        .join(Offer)
        .filter(
            ~Booking.isCancelled,
            ~Booking.isUsed,
            Offer.canExpire,
            case(
                [
                    (
                        Offer.subcategoryId == subcategories.LIVRE_PAPIER.id,
                        (Booking.dateCreated + constants.BOOKS_BOOKINGS_AUTO_EXPIRY_DELAY) <= today_at_midnight,
                    ),
                ],
                else_=((Booking.dateCreated + constants.BOOKINGS_AUTO_EXPIRY_DELAY) <= today_at_midnight),
            ),
        )
    )


def find_expiring_educational_bookings_query() -> Query:
    today_at_midnight = datetime.combine(date.today(), time(0, 0))

    return EducationalBooking.query.join(Booking).filter(
        Booking.status == BookingStatus.PENDING,
        EducationalBooking.confirmationLimitDate <= today_at_midnight,
    )


def find_expiring_booking_ids_from_query(query: Query) -> Query:
    return query.order_by(Booking.id).with_entities(Booking.id)


def find_soon_to_be_expiring_individual_bookings_ordered_by_user(given_date: date = None) -> Query:
    given_date = given_date or date.today()
    books_expiring_date = datetime.combine(given_date, time(0, 0)) + constants.BOOKS_BOOKINGS_EXPIRY_NOTIFICATION_DELAY
    other_expiring_date = datetime.combine(given_date, time(0, 0)) + constants.BOOKINGS_EXPIRY_NOTIFICATION_DELAY
    books_window = (
        datetime.combine(books_expiring_date, time(0, 0)),
        datetime.combine(books_expiring_date, time(23, 59, 59)),
    )
    rest_window = (
        datetime.combine(other_expiring_date, time(0, 0)),
        datetime.combine(other_expiring_date, time(23, 59, 59)),
    )

    return (
        IndividualBooking.query.join(Booking)
        .join(Stock)
        .join(Offer)
        .filter(
            ~Booking.isCancelled,
            ~Booking.isUsed,
            Offer.canExpire,
            case(
                [
                    (
                        Offer.subcategoryId == subcategories.LIVRE_PAPIER.id,
                        ((Booking.dateCreated + constants.BOOKS_BOOKINGS_AUTO_EXPIRY_DELAY).between(*books_window)),
                    )
                ],
                else_=(Booking.dateCreated + constants.BOOKINGS_AUTO_EXPIRY_DELAY).between(*rest_window),
            ),
        )
        .order_by(IndividualBooking.userId)
    )


def generate_booking_token() -> str:
    for _i in range(100):
        token = random_token()
        if not token_exists(token):
            return token
    raise ValueError("Could not generate new booking token")


def find_expired_individual_bookings_ordered_by_user(expired_on: date = None) -> list[IndividualBooking]:
    expired_on = expired_on or date.today()
    return (
        IndividualBooking.query.join(Booking)
        .filter(Booking.isCancelled.is_(True))
        .filter(cast(Booking.cancellationDate, Date) == expired_on)
        .filter(Booking.cancellationReason == BookingCancellationReasons.EXPIRED)
        .order_by(IndividualBooking.userId)
        .all()
    )


def find_expired_individual_bookings_ordered_by_offerer(expired_on: date = None) -> list[IndividualBooking]:
    expired_on = expired_on or date.today()
    return (
        IndividualBooking.query.join(Booking)
        .filter(Booking.isCancelled.is_(True))
        .filter(cast(Booking.cancellationDate, Date) == expired_on)
        .filter(Booking.cancellationReason == BookingCancellationReasons.EXPIRED)
        .order_by(Booking.offererId)
        .all()
    )


def get_active_bookings_quantity_for_offerer(offerer_id: int) -> dict:
    return dict(
        Booking.query.filter(
            offerer_id == Booking.offererId,
            Booking.isUsed.is_(False),
            Booking.isCancelled.is_(False),
            Booking.isConfirmed.is_(False),
        )
        .with_entities(Booking.venueId, coalesce(func.sum(Booking.quantity), 0))
        .group_by(Booking.venueId)
        .all()
    )


def get_legacy_active_bookings_quantity_for_venue(venue_id: int) -> int:
    # Stock.dnBookedQuantity cannot be used here because we exclude used/confirmed bookings.
    return (
        Booking.query.filter(
            Booking.venueId == venue_id,
            Booking.isUsed.is_(False),
            Booking.isCancelled.is_(False),
            Booking.isConfirmed.is_(False),
        )
        .with_entities(coalesce(func.sum(Booking.quantity), 0))
        .one()[0]
    )


def get_validated_bookings_quantity_for_offerer(offerer_id: int) -> dict:
    return dict(
        Booking.query.filter(Booking.isCancelled.is_(False), offerer_id == Booking.offererId)
        .filter(or_(Booking.isUsed.is_(True), Booking.isConfirmed.is_(True)))
        .with_entities(Booking.venueId, coalesce(func.sum(Booking.quantity), 0))
        .group_by(Booking.venueId)
        .all()
    )


def get_legacy_validated_bookings_quantity_for_venue(venue_id: int) -> int:
    return (
        Booking.query.filter(
            Booking.venueId == venue_id,
            Booking.isCancelled.is_(False),
            or_(Booking.isUsed.is_(True), Booking.isConfirmed.is_(True)),
        )
        .with_entities(coalesce(func.sum(Booking.quantity), 0))
        .one()[0]
    )


def find_offers_booked_by_beneficiaries(users: list[User]) -> list[Offer]:
    return (
        Offer.query.distinct(Offer.id)
        .join(Stock)
        .join(Booking)
        .join(IndividualBooking)
        .filter(IndividualBooking.userId.in_(user.id for user in users))
        .all()
    )


def find_cancellable_bookings_by_beneficiaries(users: list[User]) -> list[Booking]:
    return (
        Booking.query.join(IndividualBooking)
        .filter(IndividualBooking.userId.in_(user.id for user in users))
        .filter(Booking.isCancelled.is_(False))
        .filter(Booking.isUsed.is_(False))
        .all()
    )


def find_cancellable_bookings_by_offerer(offerer_id: int) -> list[Booking]:
    return Booking.query.filter(
        Booking.offererId == offerer_id,
        Booking.isCancelled.is_(False),
        Booking.isUsed.is_(False),
    ).all()


def get_bookings_from_deposit(deposit_id: int) -> list[Booking]:
    return (
        Booking.query.join(Booking.individualBooking)
        .filter(
            IndividualBooking.depositId == deposit_id,
            or_(Booking.status != BookingStatus.CANCELLED, Booking.status == None),
        )
        .options(joinedload(Booking.stock).joinedload(Stock.offer))
        .all()
    )


def get_csv_report(
    user: User, booking_period: tuple[date, date], event_date: Optional[datetime] = None, venue_id: Optional[int] = None
) -> str:
    bookings_query = _get_filtered_booking_report(
        pro_user=user,
        period=booking_period,
        event_date=event_date,
        venue_id=venue_id,
    )
    bookings_query = _duplicate_booking_when_quantity_is_two(bookings_query)
    return _serialize_csv_report(bookings_query)


def _field_to_venue_timezone(field: InstrumentedAttribute) -> cast:
    return cast(func.timezone(Venue.timezone, func.timezone("UTC", field)), Date)


def _get_filtered_bookings_query(
    pro_user: User,
    period: tuple[date, date],
    event_date: Optional[date] = None,
    venue_id: Optional[int] = None,
    extra_joins: Optional[Iterable[Column]] = None,
) -> Query:
    extra_joins = extra_joins or tuple()

    bookings_query = (
        Booking.query.join(Booking.offerer)
        .join(Offerer.UserOfferers)
        .join(Booking.stock)
        .join(Booking.venue, isouter=True)
    )
    for join_key in extra_joins:
        bookings_query = bookings_query.join(join_key, isouter=True)

    if not pro_user.has_admin_role:
        bookings_query = bookings_query.filter(UserOfferer.user == pro_user)

    bookings_query = bookings_query.filter(UserOfferer.validationToken.is_(None)).filter(
        _field_to_venue_timezone(Booking.dateCreated).between(*period, symmetric=True)
    )

    if venue_id is not None:
        bookings_query = bookings_query.filter(Booking.venueId == venue_id)

    if event_date:
        bookings_query = bookings_query.filter(_field_to_venue_timezone(Stock.beginningDatetime) == event_date)

    return bookings_query


def _get_filtered_bookings_count(
    pro_user: User,
    period: tuple[date, date],
    event_date: Optional[date] = None,
    venue_id: Optional[int] = None,
) -> int:
    bookings = (
        _get_filtered_bookings_query(pro_user, period, event_date, venue_id)
        .with_entities(Booking.id, Booking.quantity)
        .distinct(Booking.id)
    ).cte()
    # We really want total quantities here (and not the number of bookings),
    # since we'll build two rows for each "duo" bookings later.
    bookings_count = db.session.query(func.coalesce(func.sum(bookings.c.quantity), 0))
    return bookings_count.scalar()


def _get_filtered_booking_report(
    pro_user: User, period: tuple[date, date], event_date: Optional[datetime] = None, venue_id: Optional[int] = None
) -> str:
    bookings_query = (
        _get_filtered_bookings_query(
            pro_user,
            period,
            event_date,
            venue_id,
            extra_joins=(Stock.offer, Booking.user),
        )
        .with_entities(
            func.coalesce(Venue.publicName, Venue.name).label("venueName"),
            Venue.departementCode.label("venueDepartmentCode"),
            Offerer.postalCode.label("offererPostalCode"),
            Offer.name.label("offerName"),
            Stock.beginningDatetime.label("stockBeginningDatetime"),
            Stock.offerId,
            Offer.extraData["isbn"].label("isbn"),
            User.firstName.label("beneficiaryFirstName"),
            User.lastName.label("beneficiaryLastName"),
            User.email.label("beneficiaryEmail"),
            User.phoneNumber.label("beneficiaryPhoneNumber"),
            Booking.id,
            Booking.token,
            Booking.amount,
            Booking.quantity,
            Booking.status,
            Booking.dateCreated.label("bookedAt"),
            Booking.dateUsed.label("usedAt"),
            Booking.reimbursementDate.label("reimbursedAt"),
            Booking.cancellationDate.label("cancelledAt"),
            # `get_batch` function needs a field called exactly `id` to work,
            # the label prevents SA from using a bad (prefixed) label for this field
            Booking.id.label("id"),
            Booking.userId,
        )
        .distinct(Booking.id)
    )

    return bookings_query


def _get_filtered_booking_pro(
    pro_user: User, period: tuple[date, date], event_date: Optional[datetime] = None, venue_id: Optional[int] = None
) -> Query:
    bookings_query = (
        _get_filtered_bookings_query(
            pro_user,
            period,
            event_date,
            venue_id,
            extra_joins=(
                Stock.offer,
                Booking.individualBooking,
                IndividualBooking.user,
                Booking.educationalBooking,
                EducationalBooking.educationalRedactor,
            ),
        )
        .with_entities(
            Booking.token.label("bookingToken"),
            Booking.dateCreated.label("bookedAt"),
            Booking.quantity,
            Booking.amount.label("bookingAmount"),
            Booking.dateUsed.label("usedAt"),
            Booking.cancellationDate.label("cancelledAt"),
            Booking.cancellationLimitDate.label("cancellationLimitDate"),
            Booking.status,
            Booking.reimbursementDate.label("reimbursedAt"),
            Booking.educationalBookingId.label("educationalBookingId"),
            EducationalRedactor.firstName.label("redactorFirstname"),
            EducationalRedactor.lastName.label("redactorLastname"),
            EducationalRedactor.email.label("redactorEmail"),
            Offer.name.label("offerName"),
            Offer.id.label("offerId"),
            Offer.extraData["isbn"].label("offerIsbn"),
            User.firstName.label("beneficiaryFirstname"),
            User.lastName.label("beneficiaryLastname"),
            User.email.label("beneficiaryEmail"),
            User.phoneNumber.label("beneficiaryPhoneNumber"),
            Stock.beginningDatetime.label("stockBeginningDatetime"),
            Venue.departementCode.label("venueDepartmentCode"),
            Offerer.postalCode.label("offererPostalCode"),
        )
        .distinct(Booking.id)
    )

    return bookings_query


# TODO: to be removed when IMPROVE_BOOKINGS_PERF feature flag is definitely adopted
def _filter_bookings_recap_subquery(
    user: User,
    booking_period: tuple[date, date],
    event_date: Optional[date],
    venue_id: Optional[int],
) -> Query:
    booking_date = _field_to_venue_timezone(Booking.dateCreated)
    filter_subquery = (
        db.session.query(
            Booking.id,
            Booking.stockId,
            Booking.individualBookingId,
            Booking.educationalBookingId,
            Booking.token.label("bookingToken"),
            Booking.dateCreated.label("bookingDate"),
            Booking.isCancelled.label("isCancelled"),
            Booking.isUsed.label("isUsed"),
            Booking.quantity.label("quantity"),
            Booking.amount.label("bookingAmount"),
            Booking.dateUsed.label("dateUsed"),
            Booking.cancellationDate.label("cancellationDate"),
            Booking.cancellationLimitDate.label("cancellationLimitDate"),
            Booking.reimbursementDate.label("reimbursementDate"),
            Booking.isConfirmed.label("isConfirmed"),
        )
        .select_from(Booking)
        .join(Venue, Venue.id == Booking.venueId)
        .join(Offerer)
        .join(UserOfferer)
        .group_by(Booking.id)
    )

    if not user.has_admin_role:
        filter_subquery = filter_subquery.filter(UserOfferer.userId == user.id)

    filter_subquery = filter_subquery.filter(UserOfferer.validationToken.is_(None)).filter(
        booking_date.between(*booking_period)
    )

    if venue_id:
        filter_subquery = filter_subquery.filter(Venue.id == venue_id)

    if event_date:
        filter_subquery = filter_subquery.join(Stock).filter(
            _field_to_venue_timezone(Stock.beginningDatetime) == event_date
        )

    if venue_id is not None:
        filter_subquery.filter(Venue.id == venue_id)

    filter_subquery = filter_subquery.cte("filter_bookings")

    return filter_subquery


def _duplicate_booking_when_quantity_is_two_legacy(bookings_recap_query: Query, bookings_recap_subquery) -> Query:
    return bookings_recap_query.union_all(bookings_recap_query.filter(bookings_recap_subquery.c.quantity == 2))


def _duplicate_booking_when_quantity_is_two(bookings_recap_query: Query) -> Query:
    return bookings_recap_query.union_all(bookings_recap_query.filter(Booking.quantity == 2))


# TODO: to be removed when IMPROVE_BOOKINGS_PERF feature flag is definitely adopted
def _build_bookings_recap_query(bookings_recap_subquery: Query) -> Query:
    return (
        db.session.query(bookings_recap_subquery)
        .distinct(bookings_recap_subquery.c.id)
        .outerjoin(Payment, Payment.bookingId == bookings_recap_subquery.c.id)
        .reset_joinpoint()
        .outerjoin(IndividualBooking, IndividualBooking.id == bookings_recap_subquery.c.individualBookingId)
        .outerjoin(User, User.id == IndividualBooking.userId)
        .outerjoin(EducationalBooking, EducationalBooking.id == bookings_recap_subquery.c.educationalBookingId)
        .outerjoin(EducationalRedactor)
        .join(Stock, Stock.id == bookings_recap_subquery.c.stockId)
        .join(Offer)
        .join(Venue)
        .join(Offerer)
        .join(UserOfferer)
        .with_entities(
            bookings_recap_subquery.c.bookingToken.label("bookingToken"),
            bookings_recap_subquery.c.bookingDate.label("bookingDate"),
            bookings_recap_subquery.c.isCancelled,
            bookings_recap_subquery.c.isUsed,
            bookings_recap_subquery.c.quantity,
            bookings_recap_subquery.c.bookingAmount.label("bookingAmount"),
            bookings_recap_subquery.c.dateUsed.label("dateUsed"),
            bookings_recap_subquery.c.cancellationDate.label("cancellationDate"),
            bookings_recap_subquery.c.cancellationLimitDate.label("cancellationLimitDate"),
            bookings_recap_subquery.c.isConfirmed.label("isConfirmed"),
            bookings_recap_subquery.c.educationalBookingId,
            Offer.name.label("offerName"),
            Offer.id.label("offerId"),
            Offer.extraData.label("offerExtraData"),
            Payment.currentStatus.label("paymentStatus"),
            Payment.lastProcessedDate.label("paymentDate"),
            User.firstName.label("beneficiaryFirstname"),
            User.lastName.label("beneficiaryLastname"),
            User.email.label("beneficiaryEmail"),
            User.phoneNumber.label("beneficiaryPhoneNumber"),
            EducationalRedactor.firstName.label("redactorFirstname"),
            EducationalRedactor.lastName.label("redactorLastname"),
            EducationalRedactor.email.label("redactorEmail"),
            Stock.beginningDatetime.label("stockBeginningDatetime"),
            Venue.departementCode.label("venueDepartmentCode"),
            Offerer.name.label("offererName"),
            Offerer.postalCode.label("offererPostalCode"),
            Venue.id.label("venueId"),
            Venue.name.label("venueName"),
            Venue.publicName.label("venuePublicName"),
            Venue.isVirtual.label("venueIsVirtual"),
        )
    )


def _serialize_booking_recap(booking: AbstractKeyedTuple) -> BookingRecap:
    return BookingRecap(
        offer_identifier=booking.offerId,
        offer_name=booking.offerName,
        beneficiary_email=booking.beneficiaryEmail,
        beneficiary_phonenumber=booking.beneficiaryPhoneNumber,
        beneficiary_firstname=booking.beneficiaryFirstname,
        beneficiary_lastname=booking.beneficiaryLastname,
        booking_amount=booking.bookingAmount,
        booking_token=booking.bookingToken,
        booking_date=_serialize_date_with_timezone(booking.bookedAt, booking),
        booking_is_used=booking.status in (BookingStatus.USED, BookingStatus.REIMBURSED),
        booking_is_cancelled=booking.status == BookingStatus.CANCELLED,
        booking_is_reimbursed=booking.status == BookingStatus.REIMBURSED,
        booking_is_confirmed=booking.status
        in (
            BookingStatus.CONFIRMED,
            BookingStatus.USED,
            BookingStatus.REIMBURSED,
        ),
        booking_is_duo=booking.quantity == DUO_QUANTITY,
        booking_is_educational=booking.educationalBookingId is not None,
        redactor_email=booking.redactorEmail,
        redactor_firstname=booking.redactorFirstname,
        redactor_lastname=booking.redactorLastname,
        date_used=_serialize_date_with_timezone(booking.usedAt, booking),
        payment_date=_serialize_date_with_timezone(booking.reimbursedAt, booking),
        cancellation_date=_serialize_date_with_timezone(booking.cancelledAt, booking=booking),
        cancellation_limit_date=_serialize_date_with_timezone(booking.cancellationLimitDate, booking),
        event_beginning_datetime=(
            _apply_departement_timezone(booking.stockBeginningDatetime, booking.venueDepartmentCode)
            if booking.stockBeginningDatetime
            else None
        ),
        offer_isbn=booking.offerIsbn,
    )


# TODO: serializer parameter can be removed
#  and its usage replaced by _serialize_booking_recap function
#  when IMPROVE_BOOKINGS_PERF is definitely adopted
def _paginated_bookings_sql_entities_to_bookings_recap(
    paginated_bookings: list[object],
    page: int,
    per_page_limit: int,
    total_bookings_recap: int,
    serializer: Callable = _serialize_booking_recap,
) -> BookingsRecapPaginated:
    return BookingsRecapPaginated(
        bookings_recap=[serializer(booking) for booking in paginated_bookings],
        page=page,
        pages=int(math.ceil(total_bookings_recap / per_page_limit)),
        total=total_bookings_recap,
    )


def _apply_departement_timezone(naive_datetime: datetime, departement_code: str) -> datetime:
    return (
        naive_datetime.astimezone(tz.gettz(get_department_timezone(departement_code)))
        if naive_datetime is not None
        else None
    )


def _serialize_date_with_timezone(date_without_timezone: datetime, booking: AbstractKeyedTuple) -> datetime:
    if booking.venueDepartmentCode:
        return _apply_departement_timezone(
            naive_datetime=date_without_timezone, departement_code=booking.venueDepartmentCode
        )
    offerer_department_code = PostalCode(booking.offererPostalCode).get_departement_code()
    return _apply_departement_timezone(naive_datetime=date_without_timezone, departement_code=offerer_department_code)


def _serialize_booking_recap_legacy(booking: AbstractKeyedTuple) -> BookingRecapLegacy:
    return BookingRecapLegacy(
        offer_identifier=booking.offerId,
        offer_name=booking.offerName,
        offerer_name=booking.offererName,
        beneficiary_email=booking.beneficiaryEmail,
        beneficiary_phonenumber=booking.beneficiaryPhoneNumber,
        beneficiary_firstname=booking.beneficiaryFirstname,
        beneficiary_lastname=booking.beneficiaryLastname,
        booking_amount=booking.bookingAmount,
        booking_token=booking.bookingToken,
        booking_date=_serialize_date_with_timezone(booking.bookingDate, booking),
        booking_is_used=booking.isUsed,
        booking_is_cancelled=booking.isCancelled,
        booking_is_confirmed=booking.isConfirmed,
        booking_is_reimbursed=booking.paymentStatus == TransactionStatus.SENT,
        booking_is_duo=booking.quantity == DUO_QUANTITY,
        booking_is_educational=booking.educationalBookingId is not None,
        redactor_email=booking.redactorEmail,
        redactor_firstname=booking.redactorFirstname,
        redactor_lastname=booking.redactorLastname,
        venue_identifier=booking.venueId,
        date_used=_serialize_date_with_timezone(booking.dateUsed, booking),
        payment_date=_serialize_date_with_timezone(booking.paymentDate, booking),
        cancellation_date=_serialize_date_with_timezone(booking.cancellationDate, booking=booking),
        cancellation_limit_date=_serialize_date_with_timezone(booking.cancellationLimitDate, booking),
        venue_name=booking.venuePublicName if booking.venuePublicName else booking.venueName,
        venue_is_virtual=booking.venueIsVirtual,
        event_beginning_datetime=_apply_departement_timezone(
            booking.stockBeginningDatetime, booking.venueDepartmentCode
        )
        if booking.stockBeginningDatetime
        else None,
        offer_isbn=booking.offerExtraData["isbn"]
        if booking.offerExtraData and "isbn" in booking.offerExtraData
        else None,
    )


def _serialize_csv_report(query: Query) -> str:
    output = StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)
    writer.writerow(
        (
            "Lieu",
            "Nom de l’offre",
            "Date de l'évènement",
            "ISBN",
            "Nom et prénom du bénéficiaire",
            "Email du bénéficiaire",
            "Téléphone du bénéficiaire",
            "Date et heure de réservation",
            "Date et heure de validation",
            "Contremarque",
            "Prix de la réservation",
            "Statut de la contremarque",
            "Date et heure de remboursement",
        )
    )
    for batch in get_batches(query, Booking.id, 1000):
        rows = [
            (
                booking.venueName,
                booking.offerName,
                _serialize_date_with_timezone(booking.stockBeginningDatetime, booking),
                booking.isbn,
                f"{booking.beneficiaryLastName} {booking.beneficiaryFirstName}",
                booking.beneficiaryEmail,
                booking.beneficiaryPhoneNumber,
                _serialize_date_with_timezone(booking.bookedAt, booking),
                _serialize_date_with_timezone(booking.usedAt, booking),
                booking.token,
                booking.amount,
                BOOKING_STATUS_LABELS[booking.status],
                _serialize_date_with_timezone(booking.reimbursedAt, booking),
            )
            for booking in batch
        ]
        writer.writerows(rows)

    return output.getvalue()

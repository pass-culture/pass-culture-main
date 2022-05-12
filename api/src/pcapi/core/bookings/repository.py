import csv
from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta
from io import BytesIO
from io import StringIO
import math
import typing
from typing import Iterable
from typing import List
from typing import Optional
from typing import Union

from flask_sqlalchemy import BaseQuery
from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import case
from sqlalchemy import cast
from sqlalchemy import func
from sqlalchemy import or_
from sqlalchemy import text
from sqlalchemy.orm import contains_eager
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.sql.elements import not_
from sqlalchemy.sql.functions import coalesce
from sqlalchemy.util._collections import AbstractKeyedTuple
import xlsxwriter

from pcapi.core.bookings import constants
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingCancellationReasons
from pcapi.core.bookings.models import BookingExportType
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.bookings.models import BookingStatusFilter
from pcapi.core.bookings.models import IndividualBooking
from pcapi.core.bookings.utils import _apply_departement_timezone
from pcapi.core.bookings.utils import convert_booking_dates_utc_to_venue_timezone
from pcapi.core.categories import subcategories
from pcapi.core.educational.models import EducationalBooking
from pcapi.core.educational.models import EducationalInstitution
from pcapi.core.educational.models import EducationalRedactor
from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.models import UserOfferer
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.core.offers.serialize import serialize_offer_type_educational_or_individual
from pcapi.core.users.models import User
from pcapi.core.users.utils import sanitize_email
from pcapi.domain.booking_recap import utils as booking_recap_utils
from pcapi.domain.booking_recap.booking_recap import BookingRecap
from pcapi.domain.booking_recap.bookings_recap_paginated import BookingsRecapPaginated
from pcapi.models import db
from pcapi.models.api_errors import ResourceNotFoundError
from pcapi.models.feature import FeatureToggle
from pcapi.routes.serialization.bookings_recap_serialize import OfferType
from pcapi.utils.token import random_token


DUO_QUANTITY = 2


BOOKING_STATUS_LABELS = {
    BookingStatus.PENDING: "préréservé",
    BookingStatus.CONFIRMED: "réservé",
    BookingStatus.CANCELLED: "annulé",
    BookingStatus.USED: "validé",
    BookingStatus.REIMBURSED: "remboursé",
    "confirmed": "confirmé",
}

BOOKING_DATE_STATUS_MAPPING = {
    BookingStatusFilter.BOOKED: Booking.dateCreated,
    BookingStatusFilter.VALIDATED: Booking.dateUsed,
    BookingStatusFilter.REIMBURSED: Booking.reimbursementDate,
}

BOOKING_EXPORT_HEADER = [
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
    "Type d'offre",
]


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

    if offer_id is not None:
        query = query.join(Stock).join(Offer).filter(Offer.id == offer_id)

    booking = query.one_or_none()

    if booking is None:
        errors = ResourceNotFoundError()
        errors.add_error("global", "Cette contremarque n'a pas été trouvée")
        raise errors

    return booking


def find_by_pro_user(
    user: User,
    booking_period: Optional[tuple[date, date]] = None,
    status_filter: Optional[BookingStatusFilter] = None,
    event_date: Optional[datetime] = None,
    venue_id: Optional[int] = None,
    offer_type: Optional[OfferType] = None,
    page: int = 1,
    per_page_limit: int = 1000,
) -> BookingsRecapPaginated:
    total_bookings_recap = _get_filtered_bookings_count(
        user,
        booking_period,
        status_filter=status_filter,
        event_date=event_date,
        venue_id=venue_id,
        offer_type=offer_type,
    )

    bookings_query = _get_filtered_booking_pro(
        pro_user=user,
        period=booking_period,
        status_filter=status_filter,
        event_date=event_date,
        venue_id=venue_id,
        offer_type=offer_type,
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


def find_unique_eac_booking_if_any(stock_id: int) -> Optional[Booking]:
    return Booking.query.filter(
        Booking.stockId == stock_id, not_(Booking.status == BookingStatus.CANCELLED)
    ).one_or_none()


def find_ongoing_bookings_by_stock(stock_id: int) -> list[Booking]:
    return Booking.query.filter(
        Booking.stockId == stock_id,
        Booking.status.in_((BookingStatus.PENDING, BookingStatus.CONFIRMED)),
    ).all()


def find_not_cancelled_bookings_by_stock(stock: Stock) -> list[Booking]:
    return Booking.query.filter(Booking.stockId == stock.id, Booking.status != BookingStatus.CANCELLED).all()


def token_exists(token: str) -> bool:
    return db.session.query(Booking.query.filter_by(token=token.upper()).exists()).scalar()


def find_used_by_token(token: str) -> Booking:
    return Booking.query.filter(
        Booking.token == token.upper(),
        Booking.is_used_or_reimbursed.is_(True),  # type: ignore [attr-defined]
    ).one_or_none()


def find_expiring_individual_bookings_query() -> BaseQuery:
    today_at_midnight = datetime.combine(date.today(), time(0, 0))
    return (
        IndividualBooking.query.join(Booking)
        .join(Stock)
        .join(Offer)
        .filter(
            Booking.status.in_((BookingStatus.PENDING, BookingStatus.CONFIRMED)),
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


def find_expiring_educational_bookings_query() -> BaseQuery:
    today_at_midnight = datetime.combine(date.today(), time(0, 0))

    return EducationalBooking.query.join(Booking).filter(
        Booking.status == BookingStatus.PENDING,
        EducationalBooking.confirmationLimitDate <= today_at_midnight,
    )


def find_expiring_booking_ids_from_query(query: BaseQuery) -> BaseQuery:
    return query.order_by(Booking.id).with_entities(Booking.id)


def find_soon_to_be_expiring_individual_bookings_ordered_by_user(given_date: date = None) -> BaseQuery:
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
            Booking.status.in_((BookingStatus.PENDING, BookingStatus.CONFIRMED)),
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


def find_user_ids_with_expired_individual_bookings(expired_on: date = None) -> List[int]:
    expired_on = expired_on or date.today()
    return [
        user_id
        for user_id, in (
            db.session.query(User.id)
            .join(IndividualBooking)
            .join(Booking)
            .filter(
                Booking.status == BookingStatus.CANCELLED,
                Booking.cancellationDate >= expired_on,
                Booking.cancellationDate < (expired_on + timedelta(days=1)),
                Booking.cancellationReason == BookingCancellationReasons.EXPIRED,
            )
            .all()
        )
    ]


def get_expired_individual_bookings_for_user(user: User, expired_on: date = None) -> list[IndividualBooking]:
    expired_on = expired_on or date.today()
    return (
        IndividualBooking.query.join(Booking)
        .filter(
            IndividualBooking.user == user,
            Booking.status == BookingStatus.CANCELLED,
            Booking.cancellationDate >= expired_on,
            Booking.cancellationDate < (expired_on + timedelta(days=1)),
            Booking.cancellationReason == BookingCancellationReasons.EXPIRED,
        )
        .all()
    )


def find_expired_individual_bookings_ordered_by_offerer(expired_on: date = None) -> list[IndividualBooking]:
    expired_on = expired_on or date.today()
    return (
        IndividualBooking.query.join(Booking)
        .filter(Booking.status == BookingStatus.CANCELLED)
        .filter(cast(Booking.cancellationDate, Date) == expired_on)
        .filter(Booking.cancellationReason == BookingCancellationReasons.EXPIRED)
        .order_by(Booking.offererId)
        .all()
    )


def find_expired_educational_bookings() -> list[EducationalBooking]:
    expired_on = date.today()
    return (
        EducationalBooking.query.join(Booking)
        .filter(Booking.status == BookingStatus.CANCELLED)
        .filter(cast(Booking.cancellationDate, Date) == expired_on)
        .filter(Booking.cancellationReason == BookingCancellationReasons.EXPIRED)
        .options(
            contains_eager(EducationalBooking.booking)
            .load_only(Booking.stockId)
            .joinedload(Booking.stock, innerjoin=True)
            .load_only(Stock.beginningDatetime)
            .joinedload(Stock.offer, innerjoin=True)
            .load_only(Offer.name)
            .joinedload(Offer.venue, innerjoin=True)
            .load_only(Venue.name)
        )
        .options(
            joinedload(EducationalBooking.educationalRedactor, innerjoin=True).load_only(
                EducationalRedactor.email, EducationalRedactor.firstName, EducationalRedactor.lastName
            )
        )
        .options(joinedload(EducationalBooking.educationalInstitution, innerjoin=True))
        .all()
    )


def get_legacy_active_bookings_quantity_for_venue(venue_id: int) -> int:
    # Stock.dnBookedQuantity cannot be used here because we exclude used/confirmed bookings.
    return (
        Booking.query.filter(
            Booking.venueId == venue_id,
            Booking.status.in_((BookingStatus.PENDING, BookingStatus.CONFIRMED)),
            Booking.isConfirmed.is_(False),  # type: ignore [attr-defined]
        )
        .with_entities(coalesce(func.sum(Booking.quantity), 0))
        .one()[0]
    )


def get_legacy_validated_bookings_quantity_for_venue(venue_id: int) -> int:
    return (
        Booking.query.filter(
            Booking.venueId == venue_id,
            Booking.status != BookingStatus.CANCELLED,
            or_(Booking.is_used_or_reimbursed.is_(True), Booking.isConfirmed.is_(True)),  # type: ignore [attr-defined]
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
        .filter(Booking.status.in_((BookingStatus.PENDING, BookingStatus.CONFIRMED)))
        .all()
    )


def find_cancellable_bookings_by_offerer(offerer_id: int) -> list[Booking]:
    return Booking.query.filter(
        Booking.offererId == offerer_id,
        Booking.status.in_(
            (BookingStatus.PENDING, BookingStatus.CONFIRMED),
        ),
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


def get_export(
    user: User,
    booking_period: Optional[tuple[date, date]] = None,
    status_filter: Optional[BookingStatusFilter] = BookingStatusFilter.BOOKED,
    event_date: Optional[datetime] = None,
    venue_id: Optional[int] = None,
    offer_type: Optional[OfferType] = None,
    export_type: Optional[BookingExportType] = BookingExportType.CSV,
) -> Union[str, bytes]:
    bookings_query = _get_filtered_booking_report(
        pro_user=user,
        period=booking_period,  # type: ignore [arg-type]
        status_filter=status_filter,  # type: ignore [arg-type]
        event_date=event_date,
        venue_id=venue_id,
        offer_type=offer_type,
    )
    bookings_query = _duplicate_booking_when_quantity_is_two(bookings_query)
    if export_type == BookingExportType.EXCEL:
        return _serialize_excel_report(bookings_query)
    return _serialize_csv_report(bookings_query)


# FIXME (Gautier, 03-25-2022): also used in collective_booking. SHould we move it to core or some other place?
def field_to_venue_timezone(field: InstrumentedAttribute) -> cast:
    return cast(func.timezone(Venue.timezone, func.timezone("UTC", field)), Date)


def _get_filtered_bookings_query(
    pro_user: User,
    period: Optional[tuple[date, date]] = None,
    status_filter: Optional[BookingStatusFilter] = None,
    event_date: Optional[date] = None,
    venue_id: Optional[int] = None,
    offer_type: Optional[OfferType] = None,
    extra_joins: Optional[Iterable[Column]] = None,
) -> BaseQuery:
    remove_educational_bookings = FeatureToggle.ENABLE_INDIVIDUAL_AND_COLLECTIVE_OFFER_SEPARATION.is_active()
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

    bookings_query = bookings_query.filter(UserOfferer.validationToken.is_(None))

    if remove_educational_bookings:
        bookings_query = bookings_query.filter(Booking.educationalBookingId.is_(None))

    if period:
        period_attribut_filter = (
            BOOKING_DATE_STATUS_MAPPING[status_filter]
            if status_filter
            else BOOKING_DATE_STATUS_MAPPING[BookingStatusFilter.BOOKED]
        )

        bookings_query = bookings_query.filter(
            field_to_venue_timezone(period_attribut_filter).between(*period, symmetric=True)  # type: ignore [arg-type]
        )

    if venue_id is not None:
        bookings_query = bookings_query.filter(Booking.venueId == venue_id)

    if event_date:
        bookings_query = bookings_query.filter(field_to_venue_timezone(Stock.beginningDatetime) == event_date)  # type: ignore [arg-type]

    if offer_type is not None:
        if offer_type == OfferType.INDIVIDUAL_OR_DUO:
            bookings_query = bookings_query.filter(Booking.individualBookingId != None)
        else:
            bookings_query = bookings_query.filter(Booking.educationalBookingId != None)

    return bookings_query


def _get_filtered_bookings_count(
    pro_user: User,
    period: Optional[tuple[date, date]] = None,
    status_filter: Optional[BookingStatusFilter] = None,
    event_date: Optional[date] = None,
    venue_id: Optional[int] = None,
    offer_type: Optional[OfferType] = None,
) -> int:
    bookings = (
        _get_filtered_bookings_query(pro_user, period, status_filter, event_date, venue_id, offer_type)
        .with_entities(Booking.id, Booking.quantity)
        .distinct(Booking.id)
    ).cte()
    # We really want total quantities here (and not the number of bookings),
    # since we'll build two rows for each "duo" bookings later.
    bookings_count = db.session.query(func.coalesce(func.sum(bookings.c.quantity), 0))
    return bookings_count.scalar()


def _get_filtered_booking_report(
    pro_user: User,
    period: tuple[date, date],
    status_filter: BookingStatusFilter,
    event_date: Optional[datetime] = None,
    venue_id: Optional[int] = None,
    offer_type: Optional[OfferType] = None,
) -> str:
    bookings_query = (
        _get_filtered_bookings_query(
            pro_user,
            period,
            status_filter,
            event_date,
            venue_id,
            offer_type,
            extra_joins=(Stock.offer, Booking.user),  # type: ignore [arg-type]
        )
        .with_entities(
            func.coalesce(Venue.publicName, Venue.name).label("venueName"),
            Venue.departementCode.label("venueDepartmentCode"),
            Offerer.postalCode.label("offererPostalCode"),
            Offer.name.label("offerName"),
            Offer.isEducational.label("offerIsEducational"),
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
            Booking.isExternal,
            Booking.isConfirmed,
            # `get_batch` function needs a field called exactly `id` to work,
            # the label prevents SA from using a bad (prefixed) label for this field
            Booking.id.label("id"),
            Booking.userId,
        )
        .distinct(Booking.id)
    )

    return bookings_query


def _get_filtered_booking_pro(
    pro_user: User,
    period: Optional[tuple[date, date]] = None,
    status_filter: Optional[BookingStatusFilter] = None,
    event_date: Optional[datetime] = None,
    venue_id: Optional[int] = None,
    offer_type: Optional[OfferType] = None,
) -> BaseQuery:
    bookings_query = (
        _get_filtered_bookings_query(
            pro_user,
            period,
            status_filter,
            event_date,
            venue_id,
            offer_type,
            extra_joins=(  # type: ignore [arg-type]
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
            Booking.cancellationLimitDate,
            Booking.status,
            Booking.reimbursementDate.label("reimbursedAt"),
            Booking.educationalBookingId,
            Booking.isExternal,
            Booking.isConfirmed,
            EducationalBooking.confirmationDate,
            EducationalRedactor.firstName.label("redactorFirstname"),  # type: ignore [attr-defined]
            EducationalRedactor.lastName.label("redactorLastname"),  # type: ignore [attr-defined]
            EducationalRedactor.email.label("redactorEmail"),  # type: ignore [attr-defined]
            Offer.name.label("offerName"),
            Offer.id.label("offerId"),
            Offer.extraData["isbn"].label("offerIsbn"),
            User.firstName.label("beneficiaryFirstname"),
            User.lastName.label("beneficiaryLastname"),
            User.email.label("beneficiaryEmail"),
            User.phoneNumber.label("beneficiaryPhoneNumber"),
            Stock.beginningDatetime.label("stockBeginningDatetime"),
            Booking.stockId,
            Venue.departementCode.label("venueDepartmentCode"),
            Offerer.postalCode.label("offererPostalCode"),
        )
        .distinct(Booking.id)
    )

    return bookings_query


def _duplicate_booking_when_quantity_is_two(bookings_recap_query: BaseQuery) -> BaseQuery:
    return bookings_recap_query.union_all(bookings_recap_query.filter(Booking.quantity == 2))


def _serialize_booking_recap(booking: AbstractKeyedTuple) -> BookingRecap:
    return BookingRecap(
        offer_identifier=booking.offerId,  # type: ignore [attr-defined]
        offer_name=booking.offerName,  # type: ignore [attr-defined]
        beneficiary_email=booking.beneficiaryEmail,  # type: ignore [attr-defined]
        beneficiary_phonenumber=booking.beneficiaryPhoneNumber,  # type: ignore [attr-defined]
        beneficiary_firstname=booking.beneficiaryFirstname,  # type: ignore [attr-defined]
        beneficiary_lastname=booking.beneficiaryLastname,  # type: ignore [attr-defined]
        booking_amount=booking.bookingAmount,  # type: ignore [attr-defined]
        booking_token=booking.bookingToken,  # type: ignore [attr-defined]
        booking_date=convert_booking_dates_utc_to_venue_timezone(booking.bookedAt, booking),  # type: ignore [attr-defined]
        booking_is_used=booking.status in (BookingStatus.USED, BookingStatus.REIMBURSED),  # type: ignore [attr-defined]
        booking_is_cancelled=booking.status == BookingStatus.CANCELLED,  # type: ignore [attr-defined]
        booking_is_reimbursed=booking.status == BookingStatus.REIMBURSED,  # type: ignore [attr-defined]
        booking_is_confirmed=booking.isConfirmed,  # type: ignore [attr-defined]
        booking_is_duo=booking.quantity == DUO_QUANTITY,  # type: ignore [attr-defined]
        booking_is_educational=booking.educationalBookingId is not None,  # type: ignore [attr-defined]
        booking_is_external=booking.isExternal,  # type: ignore [attr-defined]
        booking_raw_status=booking.status,  # type: ignore [attr-defined]
        booking_confirmation_date=booking.confirmationDate,  # type: ignore [attr-defined]
        redactor_email=booking.redactorEmail,  # type: ignore [attr-defined]
        redactor_firstname=booking.redactorFirstname,  # type: ignore [attr-defined]
        redactor_lastname=booking.redactorLastname,  # type: ignore [attr-defined]
        date_used=convert_booking_dates_utc_to_venue_timezone(booking.usedAt, booking),  # type: ignore [attr-defined]
        payment_date=convert_booking_dates_utc_to_venue_timezone(booking.reimbursedAt, booking),  # type: ignore [attr-defined]
        cancellation_date=convert_booking_dates_utc_to_venue_timezone(booking.cancelledAt, booking=booking),  # type: ignore [attr-defined]
        cancellation_limit_date=convert_booking_dates_utc_to_venue_timezone(booking.cancellationLimitDate, booking),  # type: ignore [attr-defined]
        event_beginning_datetime=(
            _apply_departement_timezone(booking.stockBeginningDatetime, booking.venueDepartmentCode)  # type: ignore [attr-defined]
            if booking.stockBeginningDatetime  # type: ignore [attr-defined]
            else None
        ),
        offer_isbn=booking.offerIsbn,  # type: ignore [attr-defined]
        stock_identifier=booking.stockId,  # type: ignore [attr-defined]
    )


def _paginated_bookings_sql_entities_to_bookings_recap(
    paginated_bookings: list[object],
    page: int,
    per_page_limit: int,
    total_bookings_recap: int,
) -> BookingsRecapPaginated:
    return BookingsRecapPaginated(
        bookings_recap=[_serialize_booking_recap(booking) for booking in paginated_bookings],  # type: ignore [arg-type]
        page=page,
        pages=int(math.ceil(total_bookings_recap / per_page_limit)),
        total=total_bookings_recap,
    )


def _get_booking_status(status: BookingStatus, is_confirmed: bool) -> str:
    cancellation_limit_date_exists_and_past = is_confirmed
    if cancellation_limit_date_exists_and_past and status == BookingStatus.CONFIRMED:
        return BOOKING_STATUS_LABELS["confirmed"]
    return BOOKING_STATUS_LABELS[status]


def _serialize_csv_report(query: BaseQuery) -> str:
    output = StringIO()
    writer = csv.writer(output, dialect=csv.excel, delimiter=";", quoting=csv.QUOTE_NONNUMERIC)
    writer.writerow(BOOKING_EXPORT_HEADER)
    for booking in query.yield_per(1000):
        writer.writerow(
            (
                booking.venueName,
                booking.offerName,
                convert_booking_dates_utc_to_venue_timezone(booking.stockBeginningDatetime, booking),
                booking.isbn,
                f"{booking.beneficiaryLastName} {booking.beneficiaryFirstName}",
                booking.beneficiaryEmail,
                booking.beneficiaryPhoneNumber,
                convert_booking_dates_utc_to_venue_timezone(booking.bookedAt, booking),
                convert_booking_dates_utc_to_venue_timezone(booking.usedAt, booking),
                booking_recap_utils.get_booking_token(
                    booking.token,
                    booking.status,
                    booking.offerIsEducational,
                    booking.isExternal,
                    booking.stockBeginningDatetime,
                ),
                booking.amount,
                _get_booking_status(booking.status, booking.isConfirmed),
                convert_booking_dates_utc_to_venue_timezone(booking.reimbursedAt, booking),
                serialize_offer_type_educational_or_individual(booking.offerIsEducational),
            )
        )

    return output.getvalue()


def _serialize_excel_report(query: BaseQuery) -> bytes:
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)

    bold = workbook.add_format({"bold": 1})
    currency_format = workbook.add_format({"num_format": "###0.00[$€-fr-FR]"})
    col_width = 18

    worksheet = workbook.add_worksheet()
    row = 0

    for col_num, title in enumerate(BOOKING_EXPORT_HEADER):
        worksheet.write(row, col_num, title, bold)
        worksheet.set_column(col_num, col_num, col_width)
    row = 1
    for booking in query.yield_per(1000):
        worksheet.write(row, 0, booking.venueName)
        worksheet.write(row, 1, booking.offerName)
        worksheet.write(
            row, 2, str(convert_booking_dates_utc_to_venue_timezone(booking.stockBeginningDatetime, booking))
        )
        worksheet.write(row, 3, booking.isbn)
        worksheet.write(row, 4, f"{booking.beneficiaryLastName} {booking.beneficiaryFirstName}")
        worksheet.write(row, 5, booking.beneficiaryEmail)
        worksheet.write(row, 6, booking.beneficiaryPhoneNumber)
        worksheet.write(row, 7, str(convert_booking_dates_utc_to_venue_timezone(booking.bookedAt, booking)))
        worksheet.write(row, 8, str(convert_booking_dates_utc_to_venue_timezone(booking.usedAt, booking)))
        worksheet.write(
            row,
            9,
            booking_recap_utils.get_booking_token(
                booking.token,
                booking.status,
                booking.offerIsEducational,
                booking.isExternal,
                booking.stockBeginningDatetime,
            ),
        )
        worksheet.write(row, 10, booking.amount, currency_format)
        worksheet.write(row, 11, _get_booking_status(booking.status, booking.isConfirmed))
        worksheet.write(row, 12, str(convert_booking_dates_utc_to_venue_timezone(booking.reimbursedAt, booking)))
        worksheet.write(row, 13, serialize_offer_type_educational_or_individual(booking.offerIsEducational))
        row += 1

    workbook.close()
    return output.getvalue()


def get_soon_expiring_bookings(expiration_days_delta: int) -> typing.Generator[Booking, None, None]:
    """
    Find soon expiring bookings that will expire in exactly
    `expiration_days_delta` days.
    """
    query = (
        Booking.query.options(
            contains_eager(Booking.stock).load_only(Stock.id).contains_eager(Stock.offer).load_only(Offer.subcategoryId)
        )
        .join(Stock, Offer)
        .filter_by(canExpire=True)
        .filter(Booking.individualBookingId != None)  # noqa
        .filter(Booking.status == BookingStatus.CONFIRMED)
        .yield_per(1_000)
    )

    delta = timedelta(days=expiration_days_delta)
    for booking in query:
        expiration_date = booking.expirationDate
        if expiration_date and expiration_date.date() == date.today() + delta:
            yield booking


def venues_have_bookings(*venues: Venue) -> bool:
    """At least one venue which has email as bookingEmail has at least one non-canceled booking"""
    return db.session.query(
        Booking.query.filter(
            Booking.venueId.in_([venue.id for venue in venues]), Booking.status != BookingStatus.CANCELLED
        ).exists()
    ).scalar()


def user_has_bookings(user: User) -> bool:
    bookings_query = Booking.query.join(Booking.offerer).join(Offerer.UserOfferers)
    return db.session.query(bookings_query.filter(UserOfferer.userId == user.id).exists()).scalar()


def offerer_has_ongoing_bookings(offerer_id: int) -> bool:
    return db.session.query(
        Booking.query.filter(
            Booking.offererId == offerer_id,
            Booking.status.in_((BookingStatus.PENDING, BookingStatus.CONFIRMED)),
        ).exists()
    ).scalar()


def find_educational_bookings_done_yesterday() -> list[EducationalBooking]:
    yesterday = datetime.utcnow() - timedelta(days=1)
    yesterday_min = datetime.combine(yesterday, time.min)
    yesterday_max = datetime.combine(yesterday, time.max)

    return (
        EducationalBooking.query.join(EducationalBooking.booking)
        .join(Booking.stock)
        .filter(
            Stock.beginningDatetime >= yesterday_min,
            Stock.beginningDatetime <= yesterday_max,
        )
        .options(
            contains_eager(EducationalBooking.booking)
            .load_only(Booking.stockId)
            .joinedload(Booking.stock, innerjoin=True)
            .load_only(Stock.beginningDatetime)
            .joinedload(Stock.offer, innerjoin=True)
            .load_only(Offer.name)
            .joinedload(Offer.venue, innerjoin=True)
            .load_only(Venue.name, Venue.publicName)
        )
        .options(
            joinedload(EducationalBooking.educationalRedactor, innerjoin=True).load_only(
                EducationalRedactor.firstName,
                EducationalRedactor.lastName,
                EducationalRedactor.email,
            )
        )
        .options(
            joinedload(EducationalBooking.educationalInstitution, innerjoin=True).load_only(
                EducationalInstitution.name,
                EducationalInstitution.city,
                EducationalInstitution.postalCode,
            )
        )
        .all()
    )


def find_individual_bookings_event_happening_tomorrow_query() -> list[IndividualBooking]:
    tomorrow = datetime.utcnow() + timedelta(days=1)
    tomorrow_min = datetime.combine(tomorrow, time.min)
    tomorrow_max = datetime.combine(tomorrow, time.max)
    return (
        IndividualBooking.query.join(Booking)
        .filter(Stock.beginningDatetime >= tomorrow_min, Stock.beginningDatetime <= tomorrow_max)
        .filter(Offer.isEvent)
        .filter(not_(Offer.isDigital))
        # .options(contains_eager(IndividualBooking.user).load_only(User.firstName, User.departementCode))
        .options(
            contains_eager(IndividualBooking.booking)
            .load_only(Booking.id, Booking.stockId, Booking.quantity, Booking.token)
            .joinedload(Booking.stock, innerjoin=True)
            .load_only(Stock.beginningDatetime)
            .joinedload(Stock.offer, innerjoin=True)
            .load_only(
                Offer.name,
                Offer.subcategoryId,
                Offer.withdrawalDelay,
                Offer.withdrawalType,
                Offer.withdrawalDetails,
            )
            .joinedload(Offer.venue, innerjoin=True)
            .load_only(Venue.name, Venue.publicName, Venue.address, Venue.city, Venue.postalCode)
        )
        .all()
    )

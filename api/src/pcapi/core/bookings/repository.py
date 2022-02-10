import csv
from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta
from io import StringIO
import math
import typing
from typing import Iterable
from typing import List
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
from sqlalchemy.sql.elements import not_
from sqlalchemy.sql.functions import coalesce
from sqlalchemy.util._collections import AbstractKeyedTuple

from pcapi.core.bookings import constants
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingCancellationReasons
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.bookings.models import IndividualBooking
from pcapi.core.categories import subcategories
from pcapi.core.educational.models import EducationalBooking
from pcapi.core.educational.models import EducationalRedactor
from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.core.offers.serialize import serialize_offer_type_educational_or_individual
from pcapi.core.users.models import User
from pcapi.core.users.utils import sanitize_email
from pcapi.domain.booking_recap import utils as booking_recap_utils
from pcapi.domain.booking_recap.booking_recap import BookingRecap
from pcapi.domain.booking_recap.bookings_recap_paginated import BookingsRecapPaginated
from pcapi.domain.postal_code.postal_code import PostalCode
from pcapi.models import db
from pcapi.models.api_errors import ResourceNotFoundError
from pcapi.models.payment import Payment
from pcapi.models.user_offerer import UserOfferer
from pcapi.routes.serialization.bookings_recap_serialize import OfferType
from pcapi.utils.date import get_department_timezone
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
    booking_period: tuple[date, date],
    event_date: Optional[datetime] = None,
    venue_id: Optional[int] = None,
    offer_type: Optional[OfferType] = None,
    page: int = 1,
    per_page_limit: int = 1000,
) -> BookingsRecapPaginated:
    total_bookings_recap = _get_filtered_bookings_count(user, booking_period, event_date, venue_id, offer_type)

    bookings_query = _get_filtered_booking_pro(
        pro_user=user, period=booking_period, event_date=event_date, venue_id=venue_id, offer_type=offer_type
    )
    bookings_page = (
        bookings_query.order_by(text('"bookedAt" DESC')).offset((page - 1) * per_page_limit).limit(per_page_limit).all()
    )

    return _paginated_bookings_sql_entities_to_bookings_recap(
        paginated_bookings=bookings_page,
        page=page,
        per_page_limit=per_page_limit,
        total_bookings_recap=total_bookings_recap,
    )


def find_unique_eac_booking_if_any(stock_id: int) -> list[Booking]:
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


def find_bookings_eligible_for_payment_for_venue(venue_id: int, cutoff_date: datetime) -> list[Booking]:
    bookings = Booking.query
    bookings = bookings.filter(Booking.status == BookingStatus.USED)
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
    return Booking.query.filter(Booking.status.in_((BookingStatus.PENDING, BookingStatus.CONFIRMED))).all()


def find_used_by_token(token: str) -> Booking:
    return Booking.query.filter(
        Booking.token == token.upper(),
        Booking.is_used_or_reimbursed.is_(True),
    ).one_or_none()


def find_expiring_individual_bookings_query() -> Query:
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
        )
        .options(
            joinedload(EducationalBooking.educationalRedactor, innerjoin=True).load_only(EducationalRedactor.email)
        )
        .all()
    )


def get_active_bookings_quantity_for_offerer(offerer_id: int) -> dict:
    return dict(
        Booking.query.filter(
            offerer_id == Booking.offererId,
            Booking.status.in_((BookingStatus.PENDING, BookingStatus.CONFIRMED)),
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
            Booking.status.in_((BookingStatus.PENDING, BookingStatus.CONFIRMED)),
            Booking.isConfirmed.is_(False),
        )
        .with_entities(coalesce(func.sum(Booking.quantity), 0))
        .one()[0]
    )


def get_validated_bookings_quantity_for_offerer(offerer_id: int) -> dict:
    return dict(
        Booking.query.filter(Booking.status != BookingStatus.CANCELLED, offerer_id == Booking.offererId)
        .filter(or_(Booking.is_used_or_reimbursed.is_(True), Booking.isConfirmed.is_(True)))
        .with_entities(Booking.venueId, coalesce(func.sum(Booking.quantity), 0))
        .group_by(Booking.venueId)
        .all()
    )


def get_legacy_validated_bookings_quantity_for_venue(venue_id: int) -> int:
    return (
        Booking.query.filter(
            Booking.venueId == venue_id,
            Booking.status != BookingStatus.CANCELLED,
            or_(Booking.is_used_or_reimbursed.is_(True), Booking.isConfirmed.is_(True)),
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


def get_csv_report(
    user: User,
    booking_period: tuple[date, date],
    event_date: Optional[datetime] = None,
    venue_id: Optional[int] = None,
    offer_type: Optional[OfferType] = None,
) -> str:
    bookings_query = _get_filtered_booking_report(
        pro_user=user, period=booking_period, event_date=event_date, venue_id=venue_id, offer_type=offer_type
    )
    return _serialize_csv_report(bookings_query)


def _field_to_venue_timezone(field: InstrumentedAttribute) -> cast:
    return cast(func.timezone(Venue.timezone, func.timezone("UTC", field)), Date)


def _get_filtered_bookings_query(
    pro_user: User,
    period: tuple[date, date],
    event_date: Optional[date] = None,
    venue_id: Optional[int] = None,
    offer_type: Optional[OfferType] = None,
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

    if offer_type is not None:
        if offer_type == OfferType.INDIVIDUAL_OR_DUO:
            bookings_query = bookings_query.filter(Booking.individualBookingId != None)
        else:
            bookings_query = bookings_query.filter(Booking.educationalBookingId != None)

    return bookings_query


def _get_filtered_bookings_count(
    pro_user: User,
    period: tuple[date, date],
    event_date: Optional[date] = None,
    venue_id: Optional[int] = None,
    offer_type: Optional[OfferType] = None,
) -> int:
    bookings = (
        _get_filtered_bookings_query(pro_user, period, event_date, venue_id, offer_type)
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
    event_date: Optional[datetime] = None,
    venue_id: Optional[int] = None,
    offer_type: Optional[OfferType] = None,
) -> str:
    bookings_query = (
        _get_filtered_bookings_query(
            pro_user,
            period,
            event_date,
            venue_id,
            offer_type,
            extra_joins=(Stock.offer, Booking.user),
        )
        .with_entities(
            func.coalesce(Venue.publicName, Venue.name).label("venueName"),
            Venue.departementCode.label("venueDepartmentCode"),
            Offerer.postalCode.label("offererPostalCode"),
            Offer.name.label("offerName"),
            Offer.isEducational.label("offerIsEducational"),
            Stock.beginningDatetime.label("stockBeginningDatetime"),
            Stock.offerId,
            # TODO (ASK, JSONB): remove pylint disable when JSONB  migration is done
            Offer.extraData["isbn"].label("isbn"),  # pylint: disable=unsubscriptable-object
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
    period: tuple[date, date],
    event_date: Optional[datetime] = None,
    venue_id: Optional[int] = None,
    offer_type: Optional[OfferType] = None,
) -> Query:
    bookings_query = (
        _get_filtered_bookings_query(
            pro_user,
            period,
            event_date,
            venue_id,
            offer_type,
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
            Booking.cancellationLimitDate,
            Booking.status,
            Booking.reimbursementDate.label("reimbursedAt"),
            Booking.educationalBookingId,
            Booking.isConfirmed,
            EducationalBooking.confirmationDate,
            EducationalRedactor.firstName.label("redactorFirstname"),
            EducationalRedactor.lastName.label("redactorLastname"),
            EducationalRedactor.email.label("redactorEmail"),
            Offer.name.label("offerName"),
            Offer.id.label("offerId"),
            # TODO (ASK, JSONB): remove pylint disable when JSONB  migration is done
            Offer.extraData["isbn"].label("offerIsbn"),  # pylint: disable=unsubscriptable-object
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
        booking_is_confirmed=booking.isConfirmed,
        booking_is_duo=booking.quantity == DUO_QUANTITY,
        booking_is_educational=booking.educationalBookingId is not None,
        booking_raw_status=booking.status,
        booking_confirmation_date=booking.confirmationDate,
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


def _paginated_bookings_sql_entities_to_bookings_recap(
    paginated_bookings: list[object],
    page: int,
    per_page_limit: int,
    total_bookings_recap: int,
) -> BookingsRecapPaginated:
    return BookingsRecapPaginated(
        bookings_recap=[_serialize_booking_recap(booking) for booking in paginated_bookings],
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


def _get_booking_status(status: BookingStatus, is_confirmed: bool) -> str:
    cancellation_limit_date_exists_and_past = is_confirmed
    if cancellation_limit_date_exists_and_past and status == BookingStatus.CONFIRMED:
        return BOOKING_STATUS_LABELS["confirmed"]
    return BOOKING_STATUS_LABELS[status]


def _serialize_csv_report(query: Query) -> str:
    output = StringIO()
    writer = csv.writer(output, dialect=csv.excel, delimiter=";", quoting=csv.QUOTE_NONNUMERIC)
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
            "Type d'offre",
        )
    )
    for booking in query.yield_per(1000):
        print(booking)
        writer.writerow(
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
                booking_recap_utils.get_booking_token(
                    booking.token, booking.status, booking.offerIsEducational, booking.stockBeginningDatetime
                ),
                booking.amount,
                _get_booking_status(booking.status, booking.isConfirmed),
                _serialize_date_with_timezone(booking.reimbursedAt, booking),
                serialize_offer_type_educational_or_individual(booking.offerIsEducational),
            )
        )

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

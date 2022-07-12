from collections import namedtuple
from datetime import date
from datetime import datetime
from datetime import time
from decimal import Decimal
from typing import Iterable
from typing import Tuple

from flask_sqlalchemy import BaseQuery
from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import cast
from sqlalchemy import func
from sqlalchemy.orm import Query
from sqlalchemy.orm import contains_eager
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import load_only
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import extract

from pcapi.core.bookings.models import BookingStatus
from pcapi.core.bookings.models import BookingStatusFilter
from pcapi.core.bookings.repository import field_to_venue_timezone
from pcapi.core.bookings.utils import convert_booking_dates_utc_to_venue_timezone
from pcapi.core.educational import models as educational_models
from pcapi.core.educational.exceptions import CollectiveOfferNotFound
from pcapi.core.educational.exceptions import CollectiveOfferTemplateNotFound
from pcapi.core.educational.exceptions import EducationalDepositNotFound
from pcapi.core.educational.exceptions import EducationalInstitutionNotFound
from pcapi.core.educational.exceptions import EducationalYearNotFound
from pcapi.core.educational.exceptions import StockDoesNotExist
from pcapi.core.educational.models import CollectiveBooking
from pcapi.core.educational.models import CollectiveBookingCancellationReasons
from pcapi.core.educational.models import CollectiveBookingStatus
from pcapi.core.educational.models import CollectiveBookingStatusFilter
from pcapi.core.educational.models import CollectiveOffer
from pcapi.core.educational.models import CollectiveStock
from pcapi.core.educational.models import EducationalDomain
from pcapi.core.educational.models import EducationalRedactor
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.models import UserOfferer
from pcapi.core.offerers.models import Venue
from pcapi.core.offers import repository as offers_repository
from pcapi.core.users.models import User
from pcapi.models import db


COLLECTIVE_BOOKING_STATUS_LABELS = {
    CollectiveBookingStatus.PENDING: "préréservé",
    CollectiveBookingStatus.CONFIRMED: "réservé",
    CollectiveBookingStatus.CANCELLED: "annulé",
    CollectiveBookingStatus.USED: "validé",
    CollectiveBookingStatus.REIMBURSED: "remboursé",
    "confirmed": "confirmé",
}


BOOKING_DATE_STATUS_MAPPING = {
    CollectiveBookingStatusFilter.BOOKED: CollectiveBooking.dateCreated,
    CollectiveBookingStatusFilter.VALIDATED: CollectiveBooking.dateUsed,
    CollectiveBookingStatusFilter.REIMBURSED: CollectiveBooking.reimbursementDate,
}

CollectiveBookingNamedTuple = namedtuple(
    "CollectiveBookingNamedTuple",
    [
        "collectiveBookingId",
        "bookedAt",
        "bookingAmount",
        "usedAt",
        "cancelledAt",
        "cancellationLimitDate",
        "status",
        "reimbursedAt",
        "isConfirmed",
        "confirmationDate",
        "redactorFirstname",
        "redactorLastname",
        "redactorEmail",
        "offerName",
        "offerId",
        "stockBeginningDatetime",
        "venueDepartmentCode",
        "offererPostalCode",
    ],
)


def get_and_lock_educational_deposit(
    educational_institution_id: int, educational_year_id: str
) -> educational_models.EducationalDeposit:
    """Returns educational_deposit with a FOR UPDATE lock
    Raises EducationalDepositNotFound if no stock is found.
    WARNING: MAKE SURE YOU FREE THE LOCK (with COMMIT or ROLLBACK) and don't hold it longer than
    strictly necessary.
    """
    educational_deposit = (
        educational_models.EducationalDeposit.query.filter_by(
            educationalInstitutionId=educational_institution_id,
            educationalYearId=educational_year_id,
        )
        .populate_existing()
        .with_for_update()
        .one_or_none()
    )
    if not educational_deposit:
        raise EducationalDepositNotFound()
    return educational_deposit


def get_confirmed_collective_bookings_amount(
    educational_institution_id: int,
    educational_year_id: str,
) -> Decimal:
    query = db.session.query(func.sum(educational_models.CollectiveStock.price).label("amount"))
    query = query.join(educational_models.CollectiveBooking, educational_models.CollectiveStock.collectiveBookings)
    query = query.filter(
        educational_models.CollectiveBooking.educationalInstitutionId == educational_institution_id,
        educational_models.CollectiveBooking.educationalYearId == educational_year_id,
        ~educational_models.CollectiveBooking.status.in_(
            [CollectiveBookingStatus.CANCELLED, CollectiveBookingStatus.PENDING]
        ),
    )
    return query.first().amount or Decimal(0)


def find_collective_booking_by_id(booking_id: int) -> educational_models.CollectiveBooking | None:
    return (
        CollectiveBooking.query.filter(educational_models.CollectiveBooking.id == booking_id)
        .options(
            joinedload(educational_models.CollectiveBooking.collectiveStock, innerjoin=True)
            .joinedload(educational_models.CollectiveStock.collectiveOffer, innerjoin=True)
            .load_only(educational_models.CollectiveOffer.name)
            .joinedload(educational_models.CollectiveOffer.venue, innerjoin=True)
            .load_only(Venue.name)
        )
        .options(joinedload(educational_models.CollectiveBooking.educationalInstitution, innerjoin=True))
        .options(
            joinedload(educational_models.CollectiveBooking.educationalRedactor, innerjoin=True).load_only(
                educational_models.EducationalRedactor.email,
                educational_models.EducationalRedactor.firstName,
                educational_models.EducationalRedactor.lastName,
            )
        )
        .one_or_none()
    )


def find_educational_year_by_date(date_searched: datetime) -> educational_models.EducationalYear | None:
    return educational_models.EducationalYear.query.filter(
        date_searched >= educational_models.EducationalYear.beginningDate,
        date_searched <= educational_models.EducationalYear.expirationDate,
    ).one_or_none()


def find_educational_institution_by_uai_code(uai_code: str) -> educational_models.EducationalInstitution | None:
    return educational_models.EducationalInstitution.query.filter_by(institutionId=uai_code).one_or_none()


def find_all_educational_institution() -> list[educational_models.EducationalInstitution]:
    return educational_models.EducationalInstitution.query.all()


def find_educational_deposit_by_institution_id_and_year(
    educational_institution_id: int,
    educational_year_id: str,
) -> educational_models.EducationalDeposit | None:
    return educational_models.EducationalDeposit.query.filter(
        educational_models.EducationalDeposit.educationalInstitutionId == educational_institution_id,
        educational_models.EducationalDeposit.educationalYearId == educational_year_id,
    ).one_or_none()


def get_educational_year_beginning_at_given_year(year: int) -> educational_models.EducationalYear:
    educational_year = educational_models.EducationalYear.query.filter(
        extract("year", educational_models.EducationalYear.beginningDate) == year  # type: ignore [arg-type]
    ).one_or_none()
    if educational_year is None:
        raise EducationalYearNotFound()
    return educational_year


def find_collective_bookings_for_adage(
    uai_code: str,
    year_id: str,
    redactor_email: str | None = None,
    status: educational_models.CollectiveBookingStatus
    | educational_models.EducationalBookingStatus
    | BookingStatus
    | None = None,
) -> list[educational_models.CollectiveBooking]:

    query = educational_models.CollectiveBooking.query
    query = query.options(
        joinedload(educational_models.CollectiveBooking.collectiveStock, innerjoin=True)
        .joinedload(educational_models.CollectiveStock.collectiveOffer, innerjoin=True)
        .options(
            joinedload(educational_models.CollectiveOffer.venue, innerjoin=True),
            joinedload(educational_models.CollectiveOffer.domains),
        )
    )
    query = query.join(educational_models.EducationalInstitution)
    query = query.join(educational_models.EducationalRedactor)
    query = query.join(educational_models.EducationalYear)
    query = query.options(contains_eager(educational_models.CollectiveBooking.educationalInstitution))
    query = query.options(contains_eager(educational_models.CollectiveBooking.educationalRedactor))
    query = query.filter(educational_models.EducationalInstitution.institutionId == uai_code)
    query = query.filter(educational_models.EducationalYear.adageId == year_id)

    if redactor_email is not None:
        query = query.filter(educational_models.EducationalRedactor.email == redactor_email)

    if status is not None:
        query = query.filter(educational_models.CollectiveBooking.status == status)
    return query.all()


def find_redactor_by_email(redactor_email: str) -> educational_models.EducationalRedactor | None:
    return educational_models.EducationalRedactor.query.filter(
        educational_models.EducationalRedactor.email == redactor_email
    ).one_or_none()


def find_active_collective_booking_by_offer_id(
    collective_offer_id: int,
) -> educational_models.CollectiveBooking | None:
    return (
        educational_models.CollectiveBooking.query.filter(
            educational_models.CollectiveBooking.status.in_(
                [
                    educational_models.CollectiveBookingStatus.CONFIRMED,
                    educational_models.CollectiveBookingStatus.PENDING,
                ]
            )
        )
        .join(educational_models.CollectiveStock)
        .filter(
            educational_models.CollectiveStock.collectiveOfferId == collective_offer_id,
        )
        .options(
            contains_eager(educational_models.CollectiveBooking.collectiveStock)
            .joinedload(educational_models.CollectiveStock.collectiveOffer, innerjoin=True)
            .joinedload(educational_models.CollectiveOffer.venue, innerjoin=True)
        )
        .options(joinedload(educational_models.CollectiveBooking.educationalInstitution, innerjoin=True))
        .options(joinedload(educational_models.CollectiveBooking.educationalRedactor, innerjoin=True))
        .one_or_none()
    )


def get_paginated_collective_bookings_for_educational_year(
    educational_year_id: str,
    page: int | None,
    per_page: int | None,
) -> list[educational_models.CollectiveBooking]:
    page = 1 if page is None else page
    per_page = 1000 if per_page is None else per_page

    query = educational_models.CollectiveBooking.query
    query = query.filter(educational_models.CollectiveBooking.educationalYearId == educational_year_id)
    query = query.options(
        joinedload(educational_models.CollectiveBooking.educationalRedactor, innerjoin=True).load_only(
            educational_models.EducationalRedactor.email
        )
    )
    query = query.options(
        load_only(
            educational_models.CollectiveBooking.collectiveStockId,
            educational_models.CollectiveBooking.status,
            educational_models.CollectiveBooking.confirmationLimitDate,
        )
        .joinedload(educational_models.CollectiveBooking.collectiveStock, innerjoin=True)
        .load_only(
            educational_models.CollectiveStock.beginningDatetime,
            educational_models.CollectiveStock.collectiveOfferId,
            educational_models.CollectiveStock.price,
        )
        .joinedload(educational_models.CollectiveStock.collectiveOffer, innerjoin=True)
        .load_only(educational_models.CollectiveOffer.name)
        .joinedload(educational_models.CollectiveOffer.venue, innerjoin=True)
        .load_only(offerers_models.Venue.managingOffererId, offerers_models.Venue.departementCode)
        .joinedload(offerers_models.Venue.managingOfferer, innerjoin=True)
        .load_only(offerers_models.Offerer.postalCode)
    )
    query = query.options(
        joinedload(educational_models.CollectiveBooking.collectiveStock, innerjoin=True)
        .joinedload(educational_models.CollectiveStock.collectiveOffer, innerjoin=True)
        .joinedload(educational_models.CollectiveOffer.domains)
    )
    query = query.options(joinedload(educational_models.CollectiveBooking.educationalInstitution, innerjoin=True))
    query = query.order_by(educational_models.CollectiveBooking.id)
    query = query.offset((page - 1) * per_page)
    query = query.limit(per_page)
    return query.all()


def get_expired_collective_offers(interval: list[datetime]) -> BaseQuery:
    """Return a query of collective offers whose latest booking limit occurs within
    the given interval.

    Inactive or deleted offers are ignored.
    """

    # FIXME (cgaunet, 2022-03-08): This query could be optimized by returning offers
    # that do not have bookings because booking a collective offer will unindex it.
    return (
        educational_models.CollectiveOffer.query.join(educational_models.CollectiveStock)
        .filter(
            educational_models.CollectiveOffer.isActive.is_(True),
        )
        .having(func.max(educational_models.CollectiveStock.bookingLimitDatetime).between(*interval))
        .group_by(educational_models.CollectiveOffer.id)
        .order_by(educational_models.CollectiveOffer.id)
    )


def find_expiring_collective_bookings_query() -> BaseQuery:
    today_at_midnight = datetime.combine(date.today(), time(0, 0))

    return CollectiveBooking.query.filter(
        CollectiveBooking.status == CollectiveBookingStatus.PENDING,
        CollectiveBooking.confirmationLimitDate <= today_at_midnight,
    )


def find_expiring_collective_booking_ids_from_query(query: BaseQuery) -> BaseQuery:
    return query.order_by(CollectiveBooking.id).with_entities(CollectiveBooking.id)


def find_expired_collective_bookings() -> list[educational_models.CollectiveBooking]:
    expired_on = date.today()
    return (
        educational_models.CollectiveBooking.query.filter(
            CollectiveBooking.status == educational_models.CollectiveBookingStatus.CANCELLED
        )
        .filter(cast(educational_models.CollectiveBooking.cancellationDate, Date) == expired_on)
        .filter(
            educational_models.CollectiveBooking.cancellationReason == CollectiveBookingCancellationReasons.EXPIRED,
        )
        .options(
            joinedload(educational_models.CollectiveBooking.collectiveStock, innerjoin=True)
            .load_only(
                educational_models.CollectiveStock.beginningDatetime,
                educational_models.CollectiveStock.collectiveOfferId,
            )
            .joinedload(educational_models.CollectiveStock.collectiveOffer, innerjoin=True)
            .load_only(educational_models.CollectiveOffer.name, educational_models.CollectiveOffer.venueId)
            .joinedload(educational_models.CollectiveOffer.venue, innerjoin=True)
            .load_only(Venue.name)
        )
        .options(
            joinedload(educational_models.CollectiveBooking.educationalRedactor, innerjoin=True).load_only(
                educational_models.EducationalRedactor.email,
                educational_models.EducationalRedactor.firstName,
                educational_models.EducationalRedactor.lastName,
            )
        )
        .options(joinedload(educational_models.CollectiveBooking.educationalInstitution, innerjoin=True))
        .all()
    )


def get_and_lock_collective_stock(stock_id: int) -> educational_models.CollectiveStock:
    """Returns `stock_id` stock with a FOR UPDATE lock
    Raises StockDoesNotExist if no stock is found.
    WARNING: MAKE SURE YOU FREE THE LOCK (with COMMIT or ROLLBACK) and don't hold it longer than
    strictly necessary.
    """
    # Use `with_for_update()` to make sure we lock the stock while perfoming
    # the booking checks and update the `dnBookedQuantity`
    # This is required to prevent bugs due to concurent acces
    # Also call `populate_existing()` to make sure we don't use something
    # older from the SQLAlchemy's session.
    stock = (
        educational_models.CollectiveStock.query.filter_by(id=stock_id)
        .populate_existing()
        .with_for_update()
        .one_or_none()
    )
    if not stock:
        raise StockDoesNotExist()
    return stock


def get_collective_stock_from_stock_id(stock_id: int | str) -> educational_models.CollectiveStock:
    return educational_models.CollectiveStock.query.filter(
        educational_models.CollectiveStock.stockId == stock_id
    ).one_or_none()


def get_collective_stock(collective_stock_id: int) -> educational_models.CollectiveStock | None:
    query = educational_models.CollectiveStock.query.filter(
        educational_models.CollectiveStock.id == collective_stock_id
    )
    query = query.options(joinedload(educational_models.CollectiveStock.collectiveOffer))
    return query.one_or_none()


def get_collective_offers_for_filters(
    user_id: int,
    user_is_admin: bool,
    offers_limit: int,
    offerer_id: int | None = None,
    status: str | None = None,
    venue_id: int | None = None,
    category_id: str | None = None,
    name_keywords: str | None = None,
    period_beginning_date: str | None = None,
    period_ending_date: str | None = None,
) -> list[educational_models.CollectiveOffer]:
    query = offers_repository.get_collective_offers_by_filters(
        user_id=user_id,
        user_is_admin=user_is_admin,
        offerer_id=offerer_id,
        status=status,
        venue_id=venue_id,
        category_id=category_id,
        name_keywords=name_keywords,
        period_beginning_date=period_beginning_date,  # type: ignore [arg-type]
        period_ending_date=period_ending_date,  # type: ignore [arg-type]
    )

    query = query.order_by(educational_models.CollectiveOffer.id.desc())
    offers = (
        query.options(
            joinedload(educational_models.CollectiveOffer.venue).joinedload(offerers_models.Venue.managingOfferer)
        )
        .options(
            joinedload(educational_models.CollectiveOffer.collectiveStock).joinedload(
                educational_models.CollectiveStock.collectiveBookings
            )
        )
        .options(joinedload(educational_models.CollectiveOffer.institution))
        .limit(offers_limit)
        .all()
    )
    return offers


def get_collective_offers_template_for_filters(
    user_id: int,
    user_is_admin: bool,
    offers_limit: int,
    offerer_id: int | None = None,
    status: str | None = None,
    venue_id: int | None = None,
    category_id: str | None = None,
    name_keywords: str | None = None,
    period_beginning_date: str | None = None,
    period_ending_date: str | None = None,
) -> list[educational_models.CollectiveOfferTemplate]:
    query = offers_repository.get_collective_offers_template_by_filters(
        user_id=user_id,
        user_is_admin=user_is_admin,
        offerer_id=offerer_id,
        status=status,
        venue_id=venue_id,
        category_id=category_id,
        name_keywords=name_keywords,
        period_beginning_date=period_beginning_date,  # type: ignore [arg-type]
        period_ending_date=period_ending_date,  # type: ignore [arg-type]
    )

    if query is None:
        return []

    query = query.order_by(educational_models.CollectiveOfferTemplate.id.desc())

    offers = (
        query.options(
            joinedload(educational_models.CollectiveOfferTemplate.venue).joinedload(
                offerers_models.Venue.managingOfferer
            )
        )
        .limit(offers_limit)
        .all()
    )
    return offers


def _get_filtered_collective_bookings_query(
    pro_user: User,
    period: tuple[date, date] | None = None,
    status_filter: CollectiveBookingStatusFilter | None = None,
    event_date: date | None = None,
    venue_id: int | None = None,
    extra_joins: Iterable[Column] | None = None,
) -> Query:
    extra_joins = extra_joins or tuple()

    collective_bookings_query = (
        CollectiveBooking.query.join(CollectiveBooking.offerer)
        .join(Offerer.UserOfferers)
        .join(CollectiveBooking.collectiveStock)
        .join(CollectiveBooking.venue, isouter=True)
    )
    for join_key in extra_joins:
        collective_bookings_query = collective_bookings_query.join(join_key, isouter=True)

    if not pro_user.has_admin_role:
        collective_bookings_query = collective_bookings_query.filter(UserOfferer.user == pro_user)

    collective_bookings_query = collective_bookings_query.filter(UserOfferer.isValidated)

    if period:
        period_attribute_filter = (
            BOOKING_DATE_STATUS_MAPPING[status_filter]
            if status_filter
            else BOOKING_DATE_STATUS_MAPPING[CollectiveBookingStatusFilter.BOOKED]
        )

        collective_bookings_query = collective_bookings_query.filter(
            field_to_venue_timezone(period_attribute_filter).between(*period, symmetric=True)  # type: ignore [arg-type]
        )

    if venue_id is not None:
        collective_bookings_query = collective_bookings_query.filter(CollectiveBooking.venueId == venue_id)

    if event_date:
        collective_bookings_query = collective_bookings_query.filter(
            field_to_venue_timezone(CollectiveStock.beginningDatetime) == event_date  # type: ignore [arg-type]
        )

    return collective_bookings_query


def _get_filtered_collective_bookings_pro(
    pro_user: User,
    period: tuple[date, date] | None = None,
    status_filter: BookingStatusFilter | None = None,
    event_date: datetime | None = None,
    venue_id: int | None = None,
) -> Query:
    bookings_query = (
        _get_filtered_collective_bookings_query(
            pro_user,
            period,
            status_filter,  # type: ignore [arg-type]
            event_date,
            venue_id,
            extra_joins=(  # type: ignore [arg-type]
                CollectiveStock.collectiveOffer,
                CollectiveBooking.educationalRedactor,
            ),
        )
        .with_entities(
            CollectiveBooking.id.label("collectiveBookingId"),
            CollectiveBooking.dateCreated.label("bookedAt"),
            CollectiveStock.price.label("bookingAmount"),
            CollectiveBooking.dateUsed.label("usedAt"),
            CollectiveBooking.cancellationDate.label("cancelledAt"),
            CollectiveBooking.cancellationLimitDate,
            CollectiveBooking.status,
            CollectiveBooking.reimbursementDate.label("reimbursedAt"),
            CollectiveBooking.isConfirmed,
            CollectiveBooking.confirmationDate,
            EducationalRedactor.firstName.label("redactorFirstname"),
            EducationalRedactor.lastName.label("redactorLastname"),
            EducationalRedactor.email.label("redactorEmail"),  # type: ignore [attr-defined]
            CollectiveOffer.name.label("offerName"),
            CollectiveOffer.id.label("offerId"),
            CollectiveStock.beginningDatetime.label("stockBeginningDatetime"),
            Venue.departementCode.label("venueDepartmentCode"),
            Offerer.postalCode.label("offererPostalCode"),
        )
        .distinct(CollectiveBooking.id)
    )

    return bookings_query


def find_collective_bookings_by_pro_user(
    user: User,
    booking_period: tuple[date, date] | None = None,
    status_filter: CollectiveBookingStatusFilter | None = None,
    event_date: datetime | None = None,
    venue_id: int | None = None,
    page: int = 1,
    per_page_limit: int = 1000,
) -> Tuple[int | None, list[CollectiveBookingNamedTuple]]:
    # FIXME (gvanneste, 2022-04-01): Ne calculer le total que la première fois. À faire quand on branchera le front
    total_collective_bookings = (
        _get_filtered_collective_bookings_query(
            pro_user=user,
            period=booking_period,
            status_filter=status_filter,
            event_date=event_date,
            venue_id=venue_id,
        )
        .with_entities(CollectiveBooking.id)
        .count()
    )

    collective_bookings_query = _get_filtered_collective_bookings_pro(
        pro_user=user, period=booking_period, status_filter=status_filter, event_date=event_date, venue_id=venue_id  # type: ignore [arg-type]
    )

    collective_bookings_page = (
        collective_bookings_query.order_by(CollectiveBooking.id.desc(), CollectiveBooking.dateCreated.desc())
        .offset((page - 1) * per_page_limit)
        .limit(per_page_limit)
        .all()
    )

    collective_bookings_page_with_converted_dates = []
    for booking in collective_bookings_page:
        booking_with_converted_dates = CollectiveBookingNamedTuple(
            collectiveBookingId=booking.collectiveBookingId,
            bookedAt=convert_booking_dates_utc_to_venue_timezone(booking.bookedAt, booking),
            bookingAmount=booking.bookingAmount,
            usedAt=convert_booking_dates_utc_to_venue_timezone(booking.usedAt, booking),
            cancelledAt=convert_booking_dates_utc_to_venue_timezone(booking.cancelledAt, booking),
            cancellationLimitDate=convert_booking_dates_utc_to_venue_timezone(booking.cancellationLimitDate, booking),
            status=booking.status,
            reimbursedAt=convert_booking_dates_utc_to_venue_timezone(booking.reimbursedAt, booking),
            isConfirmed=booking.isConfirmed,
            confirmationDate=convert_booking_dates_utc_to_venue_timezone(booking.confirmationDate, booking),
            redactorFirstname=booking.redactorFirstname,
            redactorLastname=booking.redactorLastname,
            redactorEmail=booking.redactorEmail,
            offerName=booking.offerName,
            offerId=booking.offerId,
            stockBeginningDatetime=convert_booking_dates_utc_to_venue_timezone(booking.stockBeginningDatetime, booking),
            venueDepartmentCode=booking.venueDepartmentCode,
            offererPostalCode=booking.offererPostalCode,
        )
        collective_bookings_page_with_converted_dates.append(booking_with_converted_dates)

    return total_collective_bookings, collective_bookings_page_with_converted_dates


def get_filtered_collective_booking_report(
    pro_user: User,
    period: tuple[date, date],
    status_filter: CollectiveBookingStatusFilter,
    event_date: datetime | None = None,
    venue_id: int | None = None,
) -> str:
    bookings_query = (
        _get_filtered_collective_bookings_query(
            pro_user,
            period,
            status_filter,
            event_date,
            venue_id,
            extra_joins=(  # type: ignore [arg-type]
                CollectiveStock.collectiveOffer,
                CollectiveBooking.educationalRedactor,
            ),
        )
        .with_entities(
            func.coalesce(Venue.publicName, Venue.name).label("venueName"),
            Venue.departementCode.label("venueDepartmentCode"),
            offerers_models.Offerer.postalCode.label("offererPostalCode"),
            CollectiveOffer.name.label("offerName"),
            CollectiveStock.price,
            CollectiveStock.beginningDatetime.label("stockBeginningDatetime"),
            EducationalRedactor.firstName,
            EducationalRedactor.lastName,
            EducationalRedactor.email,
            CollectiveBooking.id,
            CollectiveBooking.dateCreated.label("bookedAt"),
            CollectiveBooking.dateUsed.label("usedAt"),
            CollectiveBooking.reimbursementDate.label("reimbursedAt"),
            CollectiveBooking.status,
            CollectiveBooking.isConfirmed,
            # `get_batch` function needs a field called exactly `id` to work,
            # the label prevents SA from using a bad (prefixed) label for this field
            CollectiveBooking.id.label("id"),
            CollectiveBooking.educationalRedactorId,
        )
        .distinct(CollectiveBooking.id)
    )

    return bookings_query


def get_collective_offer_by_id(offer_id: int) -> educational_models.CollectiveOffer:
    try:
        return (
            educational_models.CollectiveOffer.query.filter(educational_models.CollectiveOffer.id == offer_id)
            .outerjoin(
                educational_models.CollectiveStock, educational_models.CollectiveStock.collectiveOfferId == offer_id
            )
            .options(
                joinedload(educational_models.CollectiveOffer.venue, innerjoin=True,).joinedload(
                    Venue.managingOfferer,
                    innerjoin=True,
                )
            )
            .options(joinedload(educational_models.CollectiveOffer.domains))
            .one()
        )
    except NoResultFound:
        raise CollectiveOfferNotFound()


def get_collective_offer_template_by_id(offer_id: int) -> educational_models.CollectiveOfferTemplate:
    try:
        query = educational_models.CollectiveOfferTemplate.query
        query = query.filter(educational_models.CollectiveOfferTemplate.id == offer_id)
        query = query.options(
            joinedload(educational_models.CollectiveOfferTemplate.venue, innerjoin=True,).joinedload(
                Venue.managingOfferer,
                innerjoin=True,
            )
        )
        query = query.options(joinedload(educational_models.CollectiveOfferTemplate.domains))
        return query.one()
    except NoResultFound:
        raise CollectiveOfferTemplateNotFound()


def user_has_bookings(user: User) -> bool:
    bookings_query = CollectiveBooking.query.join(CollectiveBooking.offerer).join(Offerer.UserOfferers)
    return db.session.query(bookings_query.filter(UserOfferer.userId == user.id).exists()).scalar()


def get_collective_stock_for_offer(offer_id: int) -> CollectiveStock | None:
    return (
        CollectiveStock.query.options(
            joinedload(CollectiveStock.collectiveBookings).load_only(CollectiveBooking.status)
        )
        .filter(CollectiveStock.collectiveOfferId == offer_id)
        .one_or_none()
    )


def get_collective_offer_by_offer_id(offer_id: int) -> CollectiveOffer:
    return CollectiveOffer.query.filter(CollectiveOffer.offerId == offer_id).one()


def get_collective_offer_by_id_for_adage(offer_id: int) -> CollectiveOffer:
    return (
        educational_models.CollectiveOffer.query.filter(educational_models.CollectiveOffer.id == offer_id)
        .options(
            joinedload(educational_models.CollectiveOffer.collectiveStock).joinedload(
                educational_models.CollectiveStock.collectiveBookings
            )
        )
        .options(joinedload(educational_models.CollectiveOffer.institution))
        .options(
            joinedload(educational_models.CollectiveOffer.venue)
            .joinedload(offerers_models.Venue.managingOfferer)
            .load_only(
                offerers_models.Offerer.name,
                offerers_models.Offerer.validationToken,
                offerers_models.Offerer.isActive,
            )
        )
        .options(joinedload(educational_models.CollectiveOffer.domains))
        .one()
    )


def get_collective_offer_template_by_id_for_adage(offer_id: int) -> CollectiveOffer:
    return (
        educational_models.CollectiveOfferTemplate.query.filter(
            educational_models.CollectiveOfferTemplate.id == offer_id
        )
        .options(
            joinedload(educational_models.CollectiveOfferTemplate.venue)
            .joinedload(offerers_models.Venue.managingOfferer)
            .load_only(
                offerers_models.Offerer.name,
                offerers_models.Offerer.validationToken,
                offerers_models.Offerer.isActive,
            )
        )
        .options(joinedload(educational_models.CollectiveOfferTemplate.domains))
        .one()
    )


def get_query_for_collective_offers_by_ids_for_user(user: User, ids: Iterable[int]) -> BaseQuery:
    query = educational_models.CollectiveOffer.query
    if not user.has_admin_role:
        query = query.join(Venue, educational_models.CollectiveOffer.venue)
        query = query.join(Offerer, Venue.managingOfferer)
        query = query.join(UserOfferer, Offerer.UserOfferers)
        query = query.filter(UserOfferer.userId == user.id, UserOfferer.isValidated)
    query = query.filter(educational_models.CollectiveOffer.id.in_(ids))
    return query


def get_query_for_collective_offers_template_by_ids_for_user(user: User, ids: Iterable[int]) -> BaseQuery:
    query = educational_models.CollectiveOfferTemplate.query
    if not user.has_admin_role:
        query = query.join(Venue, educational_models.CollectiveOfferTemplate.venue)
        query = query.join(Offerer, Venue.managingOfferer)
        query = query.join(UserOfferer, Offerer.UserOfferers)
        query = query.filter(UserOfferer.userId == user.id, UserOfferer.isValidated)
    query = query.filter(educational_models.CollectiveOfferTemplate.id.in_(ids))
    return query


def get_educational_domains_from_ids(ids: Iterable[int]) -> list[educational_models.EducationalDomain]:
    return educational_models.EducationalDomain.query.filter(educational_models.EducationalDomain.id.in_(ids)).all()


def get_all_educational_domains_ordered_by_name() -> list[EducationalDomain]:
    return EducationalDomain.query.order_by(EducationalDomain.name).all()


def get_all_educational_institutions(offset: int = 0, limit: int = 0) -> tuple[tuple, int]:
    total = db.session.query(func.count(educational_models.EducationalInstitution.id)).one()[0]

    query = educational_models.EducationalInstitution.query
    query = query.order_by(educational_models.EducationalInstitution.name)
    query = query.with_entities(
        educational_models.EducationalInstitution.name,
        educational_models.EducationalInstitution.id,
        educational_models.EducationalInstitution.postalCode,
        educational_models.EducationalInstitution.city,
    )

    if offset != 0:
        query = query.offset(offset)
    if limit != 0:
        query = query.limit(limit)

    return query.all(), total


def get_educational_institution_by_id(institution_id: int) -> educational_models.EducationalInstitution:
    try:
        return educational_models.EducationalInstitution.query.filter_by(id=institution_id).one()
    except NoResultFound:
        raise EducationalInstitutionNotFound()

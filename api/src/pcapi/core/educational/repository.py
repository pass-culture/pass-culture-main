from collections import namedtuple
from datetime import date
from datetime import datetime
from datetime import time
from decimal import Decimal
from typing import Iterable
from typing import Tuple

from flask_sqlalchemy import BaseQuery
import sqlalchemy as sa
from sqlalchemy.sql.expression import extract

from pcapi.core.bookings import models as bookings_models
from pcapi.core.bookings.repository import field_to_venue_timezone
from pcapi.core.bookings.utils import convert_booking_dates_utc_to_venue_timezone
from pcapi.core.educational import exceptions as educational_exceptions
from pcapi.core.educational import models as educational_models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import repository as offers_repository
from pcapi.core.users.models import User
from pcapi.models import db
from pcapi.models import offer_mixin
from pcapi.utils.clean_accents import clean_accents


COLLECTIVE_BOOKING_STATUS_LABELS = {
    educational_models.CollectiveBookingStatus.PENDING: "préréservé",
    educational_models.CollectiveBookingStatus.CONFIRMED: "réservé",
    educational_models.CollectiveBookingStatus.CANCELLED: "annulé",
    educational_models.CollectiveBookingStatus.USED: "validé",
    educational_models.CollectiveBookingStatus.REIMBURSED: "remboursé",
    "confirmed": "confirmé",
}


BOOKING_DATE_STATUS_MAPPING = {
    educational_models.CollectiveBookingStatusFilter.BOOKED: educational_models.CollectiveBooking.dateCreated,
    educational_models.CollectiveBookingStatusFilter.VALIDATED: educational_models.CollectiveBooking.dateUsed,
    educational_models.CollectiveBookingStatusFilter.REIMBURSED: educational_models.CollectiveBooking.reimbursementDate,
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
        "institutionId",
        "institutionType",
        "institutionName",
        "institutionPostalCode",
        "institutionCity",
        "institutionPhoneNumber",
        "offerName",
        "offerId",
        "stockBeginningDatetime",
        "venueDepartmentCode",
        "offererPostalCode",
        "numberOfTickets",
    ],
)


def get_and_lock_educational_deposit(
    educational_institution_id: int, educational_year_id: str
) -> educational_models.EducationalDeposit:
    """Returns educational_deposit with a FOR UPDATE lock
    Raises educational_exceptions.EducationalDepositNotFound if no stock is found.
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
        raise educational_exceptions.EducationalDepositNotFound()
    return educational_deposit


def get_ministry_budget_for_year(ministry: str | None, educational_year_id: str) -> Decimal:
    query = db.session.query(sa.func.sum(educational_models.EducationalDeposit.amount).label("amount"))
    query = query.filter(
        educational_models.EducationalDeposit.educationalYearId == educational_year_id,
        educational_models.EducationalDeposit.ministry == ministry,
    )
    return query.first().amount or Decimal(0)


def get_confirmed_collective_bookings_amount_for_ministry(
    ministry: str | None,
    educational_year_id: str,
) -> Decimal:
    query = db.session.query(sa.func.sum(educational_models.CollectiveStock.price).label("amount"))
    query = query.join(educational_models.CollectiveBooking, educational_models.CollectiveStock.collectiveBookings)
    query = query.join(
        educational_models.EducationalInstitution, educational_models.CollectiveBooking.educationalInstitution
    )
    query = query.join(educational_models.EducationalDeposit, educational_models.EducationalInstitution.deposits)
    query = query.filter(
        educational_models.CollectiveBooking.educationalYearId == educational_year_id,
        ~educational_models.CollectiveBooking.status.in_(
            [educational_models.CollectiveBookingStatus.CANCELLED, educational_models.CollectiveBookingStatus.PENDING]
        ),
        educational_models.EducationalDeposit.ministry == ministry,
    )
    return query.first().amount or Decimal(0)


def get_confirmed_collective_bookings_amount(
    educational_institution_id: int,
    educational_year_id: str,
) -> Decimal:
    query = db.session.query(sa.func.sum(educational_models.CollectiveStock.price).label("amount"))
    query = query.join(educational_models.CollectiveBooking, educational_models.CollectiveStock.collectiveBookings)
    query = query.filter(
        educational_models.CollectiveBooking.educationalInstitutionId == educational_institution_id,
        educational_models.CollectiveBooking.educationalYearId == educational_year_id,
        ~educational_models.CollectiveBooking.status.in_(
            [educational_models.CollectiveBookingStatus.CANCELLED, educational_models.CollectiveBookingStatus.PENDING]
        ),
    )
    return query.first().amount or Decimal(0)


def find_collective_booking_by_id(booking_id: int) -> educational_models.CollectiveBooking | None:
    return (
        educational_models.CollectiveBooking.query.filter(educational_models.CollectiveBooking.id == booking_id)
        .options(
            sa.orm.joinedload(educational_models.CollectiveBooking.collectiveStock, innerjoin=True)
            .joinedload(educational_models.CollectiveStock.collectiveOffer, innerjoin=True)
            .load_only(educational_models.CollectiveOffer.name)
            .joinedload(educational_models.CollectiveOffer.venue, innerjoin=True)
            .load_only(offerers_models.Venue.name)
        )
        .options(sa.orm.joinedload(educational_models.CollectiveBooking.educationalInstitution, innerjoin=True))
        .options(
            sa.orm.joinedload(educational_models.CollectiveBooking.educationalRedactor, innerjoin=True).load_only(
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
        extract("year", educational_models.EducationalYear.beginningDate) == year
    ).one_or_none()
    if educational_year is None:
        raise educational_exceptions.EducationalYearNotFound()
    return educational_year


def find_collective_bookings_for_adage(
    uai_code: str,
    year_id: str,
    redactor_email: str | None = None,
) -> list[educational_models.CollectiveBooking]:

    query = educational_models.CollectiveBooking.query
    query = query.options(
        sa.orm.joinedload(educational_models.CollectiveBooking.collectiveStock, innerjoin=True)
        .joinedload(educational_models.CollectiveStock.collectiveOffer, innerjoin=True)
        .options(
            sa.orm.joinedload(educational_models.CollectiveOffer.venue, innerjoin=True),
            sa.orm.joinedload(educational_models.CollectiveOffer.domains),
        )
    )
    query = query.join(educational_models.EducationalInstitution)
    query = query.join(educational_models.EducationalRedactor)
    query = query.join(educational_models.EducationalYear)
    query = query.options(sa.orm.contains_eager(educational_models.CollectiveBooking.educationalInstitution))
    query = query.options(sa.orm.contains_eager(educational_models.CollectiveBooking.educationalRedactor))
    query = query.filter(educational_models.EducationalInstitution.institutionId == uai_code)
    query = query.filter(educational_models.EducationalYear.adageId == year_id)

    if redactor_email is not None:
        query = query.filter(educational_models.EducationalRedactor.email == redactor_email)

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
            sa.orm.contains_eager(educational_models.CollectiveBooking.collectiveStock)
            .joinedload(educational_models.CollectiveStock.collectiveOffer, innerjoin=True)
            .joinedload(educational_models.CollectiveOffer.venue, innerjoin=True)
        )
        .options(sa.orm.joinedload(educational_models.CollectiveBooking.educationalInstitution, innerjoin=True))
        .options(sa.orm.joinedload(educational_models.CollectiveBooking.educationalRedactor, innerjoin=True))
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
        sa.orm.joinedload(educational_models.CollectiveBooking.educationalRedactor, innerjoin=True).load_only(
            educational_models.EducationalRedactor.email
        )
    )
    query = query.options(
        sa.orm.load_only(
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
        sa.orm.joinedload(educational_models.CollectiveBooking.collectiveStock, innerjoin=True)
        .joinedload(educational_models.CollectiveStock.collectiveOffer, innerjoin=True)
        .joinedload(educational_models.CollectiveOffer.domains)
    )
    query = query.options(
        sa.orm.joinedload(educational_models.CollectiveBooking.educationalInstitution, innerjoin=True)
    )
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
        .having(sa.func.max(educational_models.CollectiveStock.bookingLimitDatetime).between(*interval))  # type: ignore [arg-type]
        .group_by(educational_models.CollectiveOffer.id)
        .order_by(educational_models.CollectiveOffer.id)
    )


def find_expiring_collective_bookings_query() -> BaseQuery:
    today_at_midnight = datetime.combine(date.today(), time(0, 0))

    return educational_models.CollectiveBooking.query.filter(
        educational_models.CollectiveBooking.status == educational_models.CollectiveBookingStatus.PENDING,
        educational_models.CollectiveBooking.confirmationLimitDate <= today_at_midnight,
    )


def find_expiring_collective_booking_ids_from_query(query: BaseQuery) -> BaseQuery:
    return query.order_by(educational_models.CollectiveBooking.id).with_entities(
        educational_models.CollectiveBooking.id
    )


def find_expired_collective_bookings() -> list[educational_models.CollectiveBooking]:
    expired_on = date.today()
    return (
        educational_models.CollectiveBooking.query.filter(
            educational_models.CollectiveBooking.status == educational_models.CollectiveBookingStatus.CANCELLED
        )
        .filter(sa.cast(educational_models.CollectiveBooking.cancellationDate, sa.Date) == expired_on)
        .filter(
            educational_models.CollectiveBooking.cancellationReason
            == educational_models.CollectiveBookingCancellationReasons.EXPIRED,
        )
        .options(
            sa.orm.joinedload(educational_models.CollectiveBooking.collectiveStock, innerjoin=True)
            .load_only(
                educational_models.CollectiveStock.beginningDatetime,
                educational_models.CollectiveStock.collectiveOfferId,
            )
            .joinedload(educational_models.CollectiveStock.collectiveOffer, innerjoin=True)
            .load_only(educational_models.CollectiveOffer.name, educational_models.CollectiveOffer.venueId)
            .joinedload(educational_models.CollectiveOffer.venue, innerjoin=True)
            .load_only(offerers_models.Venue.name)
        )
        .options(
            sa.orm.joinedload(educational_models.CollectiveBooking.educationalRedactor, innerjoin=True).load_only(
                educational_models.EducationalRedactor.email,
                educational_models.EducationalRedactor.firstName,
                educational_models.EducationalRedactor.lastName,
            )
        )
        .options(sa.orm.joinedload(educational_models.CollectiveBooking.educationalInstitution, innerjoin=True))
        .all()
    )


def get_and_lock_collective_stock(stock_id: int) -> educational_models.CollectiveStock:
    """Returns `stock_id` stock with a FOR UPDATE lock
    Raises educational_exceptions.StockDoesNotExist if no stock is found.
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
        raise educational_exceptions.StockDoesNotExist()
    return stock


def get_collective_stock_from_stock_id(stock_id: int | str) -> educational_models.CollectiveStock:
    return educational_models.CollectiveStock.query.filter(
        educational_models.CollectiveStock.stockId == stock_id
    ).one_or_none()


def get_collective_stock(collective_stock_id: int) -> educational_models.CollectiveStock | None:
    query = educational_models.CollectiveStock.query.filter(
        educational_models.CollectiveStock.id == collective_stock_id
    )
    query = query.options(sa.orm.joinedload(educational_models.CollectiveStock.collectiveOffer))
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
            sa.orm.joinedload(educational_models.CollectiveOffer.venue).joinedload(
                offerers_models.Venue.managingOfferer
            )
        )
        .options(
            sa.orm.joinedload(educational_models.CollectiveOffer.collectiveStock).joinedload(
                educational_models.CollectiveStock.collectiveBookings
            )
        )
        .options(sa.orm.joinedload(educational_models.CollectiveOffer.institution))
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
            sa.orm.joinedload(educational_models.CollectiveOfferTemplate.venue).joinedload(
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
    status_filter: educational_models.CollectiveBookingStatusFilter | None = None,
    event_date: date | None = None,
    venue_id: int | None = None,
    extra_joins: Iterable[sa.Column] | None = None,
) -> sa.orm.Query:
    extra_joins = extra_joins or tuple()

    collective_bookings_query = (
        educational_models.CollectiveBooking.query.join(educational_models.CollectiveBooking.offerer)
        .join(offerers_models.Offerer.UserOfferers)
        .join(educational_models.CollectiveBooking.collectiveStock)
        .join(educational_models.CollectiveBooking.venue, isouter=True)
    )
    for join_key in extra_joins:
        collective_bookings_query = collective_bookings_query.join(join_key, isouter=True)

    if not pro_user.has_admin_role:
        collective_bookings_query = collective_bookings_query.filter(offerers_models.UserOfferer.user == pro_user)

    collective_bookings_query = collective_bookings_query.filter(offerers_models.UserOfferer.isValidated)

    if period:
        period_attribute_filter = (
            BOOKING_DATE_STATUS_MAPPING[status_filter]
            if status_filter
            else BOOKING_DATE_STATUS_MAPPING[educational_models.CollectiveBookingStatusFilter.BOOKED]
        )

        collective_bookings_query = collective_bookings_query.filter(
            field_to_venue_timezone(period_attribute_filter).between(*period, symmetric=True)  # type: ignore [arg-type]
        )

    if venue_id is not None:
        collective_bookings_query = collective_bookings_query.filter(
            educational_models.CollectiveBooking.venueId == venue_id
        )

    if event_date:
        collective_bookings_query = collective_bookings_query.filter(
            field_to_venue_timezone(educational_models.CollectiveStock.beginningDatetime) == event_date
        )

    return collective_bookings_query


def list_public_collective_offers(
    offerer_id: int,
    status: offer_mixin.OfferStatus | None = None,
    venue_id: int | None = None,
    period_beginning_date: str | None = None,
    period_ending_date: str | None = None,
    limit: int = 500,
) -> list[educational_models.CollectiveOffer]:
    query = educational_models.CollectiveOffer.query
    query = query.join(offerers_models.Venue, educational_models.CollectiveOffer.venue)
    query = query.join(educational_models.CollectiveStock, educational_models.CollectiveOffer.collectiveStock)
    filters = [
        offerers_models.Venue.managingOffererId == offerer_id,
        educational_models.CollectiveOffer.validation != offer_mixin.OfferValidationStatus.DRAFT,
    ]
    if status:
        filters.append(educational_models.CollectiveOffer.status == status)  # type: ignore [arg-type]
    if venue_id:
        filters.append(educational_models.CollectiveOffer.venueId == venue_id)
    if period_beginning_date:
        filters.append(educational_models.CollectiveStock.beginningDatetime >= period_beginning_date)
    if period_ending_date:
        filters.append(educational_models.CollectiveStock.beginningDatetime <= period_ending_date)
    query = query.filter(*filters)

    query = query.options(
        sa.orm.joinedload(educational_models.CollectiveOffer.collectiveStock),
        sa.orm.joinedload(educational_models.CollectiveOffer.collectiveStock).joinedload(
            # used to compute CollectiveOffer.status
            educational_models.CollectiveStock.collectiveBookings
        ),
    )

    query = query.order_by(educational_models.CollectiveOffer.id)
    query = query.limit(limit)
    return query.all()


def _get_filtered_collective_bookings_pro(
    pro_user: User,
    period: tuple[date, date] | None = None,
    status_filter: bookings_models.BookingStatusFilter | None = None,
    event_date: datetime | None = None,
    venue_id: int | None = None,
) -> sa.orm.Query:
    bookings_query = (
        _get_filtered_collective_bookings_query(
            pro_user,
            period,
            status_filter,  # type: ignore [arg-type]
            event_date,
            venue_id,
            extra_joins=(
                educational_models.CollectiveStock.collectiveOffer,
                educational_models.CollectiveBooking.educationalInstitution,
            ),
        )
        .with_entities(
            educational_models.CollectiveBooking.id.label("collectiveBookingId"),
            educational_models.CollectiveBooking.dateCreated.label("bookedAt"),
            educational_models.CollectiveStock.price.label("bookingAmount"),
            educational_models.CollectiveBooking.dateUsed.label("usedAt"),
            educational_models.CollectiveBooking.cancellationDate.label("cancelledAt"),
            educational_models.CollectiveBooking.cancellationLimitDate,
            educational_models.CollectiveBooking.status,
            educational_models.CollectiveBooking.reimbursementDate.label("reimbursedAt"),
            educational_models.CollectiveBooking.isConfirmed,
            educational_models.CollectiveBooking.confirmationDate,
            educational_models.EducationalInstitution.id.label("institutionId"),
            educational_models.EducationalInstitution.institutionType.label("institutionType"),
            educational_models.EducationalInstitution.name.label("institutionName"),
            educational_models.EducationalInstitution.city.label("institutionCity"),
            educational_models.EducationalInstitution.postalCode.label("institutionPostalCode"),
            educational_models.EducationalInstitution.phoneNumber.label("institutionPhoneNumber"),
            educational_models.CollectiveOffer.name.label("offerName"),
            educational_models.CollectiveOffer.id.label("offerId"),
            educational_models.CollectiveStock.beginningDatetime.label("stockBeginningDatetime"),
            offerers_models.Venue.departementCode.label("venueDepartmentCode"),
            offerers_models.Offerer.postalCode.label("offererPostalCode"),
            educational_models.CollectiveStock.numberOfTickets.label("stockNumberOfTickets"),
        )
        .distinct(educational_models.CollectiveBooking.id)
    )

    return bookings_query


def find_collective_bookings_by_pro_user(
    user: User,
    booking_period: tuple[date, date] | None = None,
    status_filter: educational_models.CollectiveBookingStatusFilter | None = None,
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
        .with_entities(educational_models.CollectiveBooking.id)
        .count()
    )

    collective_bookings_query = _get_filtered_collective_bookings_pro(
        pro_user=user, period=booking_period, status_filter=status_filter, event_date=event_date, venue_id=venue_id  # type: ignore [arg-type]
    )

    collective_bookings_page = (
        collective_bookings_query.order_by(
            educational_models.CollectiveBooking.id.desc(), educational_models.CollectiveBooking.dateCreated.desc()
        )
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
            institutionId=booking.institutionId,
            institutionType=booking.institutionType,
            institutionName=booking.institutionName,
            institutionPostalCode=booking.institutionPostalCode,
            institutionCity=booking.institutionCity,
            institutionPhoneNumber=booking.institutionPhoneNumber,
            offerName=booking.offerName,
            offerId=booking.offerId,
            stockBeginningDatetime=convert_booking_dates_utc_to_venue_timezone(booking.stockBeginningDatetime, booking),
            venueDepartmentCode=booking.venueDepartmentCode,
            offererPostalCode=booking.offererPostalCode,
            numberOfTickets=booking.stockNumberOfTickets,
        )
        collective_bookings_page_with_converted_dates.append(booking_with_converted_dates)

    return total_collective_bookings, collective_bookings_page_with_converted_dates


def get_filtered_collective_booking_report(
    pro_user: User,
    period: tuple[date, date],
    status_filter: educational_models.CollectiveBookingStatusFilter,
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
            extra_joins=(
                educational_models.CollectiveStock.collectiveOffer,
                educational_models.CollectiveBooking.educationalRedactor,
            ),
        )
        .with_entities(
            sa.func.coalesce(offerers_models.Venue.publicName, offerers_models.Venue.name).label("venueName"),
            offerers_models.Venue.departementCode.label("venueDepartmentCode"),
            offerers_models.Offerer.postalCode.label("offererPostalCode"),
            educational_models.CollectiveOffer.name.label("offerName"),
            educational_models.CollectiveStock.price,
            educational_models.CollectiveStock.beginningDatetime.label("stockBeginningDatetime"),
            educational_models.EducationalRedactor.firstName,
            educational_models.EducationalRedactor.lastName,
            educational_models.EducationalRedactor.email,
            educational_models.CollectiveBooking.id,
            educational_models.CollectiveBooking.dateCreated.label("bookedAt"),
            educational_models.CollectiveBooking.dateUsed.label("usedAt"),
            educational_models.CollectiveBooking.reimbursementDate.label("reimbursedAt"),
            educational_models.CollectiveBooking.status,
            educational_models.CollectiveBooking.isConfirmed,
            # `get_batch` function needs a field called exactly `id` to work,
            # the label prevents SA from using a bad (prefixed) label for this field
            educational_models.CollectiveBooking.id.label("id"),
            educational_models.CollectiveBooking.educationalRedactorId,
        )
        .distinct(educational_models.CollectiveBooking.id)
    )

    return bookings_query  # type: ignore [return-value]


def get_collective_offer_by_id(offer_id: int) -> educational_models.CollectiveOffer:
    try:
        return (
            educational_models.CollectiveOffer.query.filter(educational_models.CollectiveOffer.id == offer_id)
            .outerjoin(
                educational_models.CollectiveStock, educational_models.CollectiveStock.collectiveOfferId == offer_id
            )
            .options(
                sa.orm.joinedload(educational_models.CollectiveOffer.venue, innerjoin=True,).joinedload(
                    offerers_models.Venue.managingOfferer,
                    innerjoin=True,
                )
            )
            .options(sa.orm.joinedload(educational_models.CollectiveOffer.domains))
            .options(
                sa.orm.contains_eager(educational_models.CollectiveOffer.collectiveStock).joinedload(
                    educational_models.CollectiveStock.collectiveBookings
                )
            )
            .one()
        )
    except sa.orm.exc.NoResultFound:
        raise educational_exceptions.CollectiveOfferNotFound()


def get_collective_offer_template_by_id(offer_id: int) -> educational_models.CollectiveOfferTemplate:
    try:
        query = educational_models.CollectiveOfferTemplate.query
        query = query.filter(educational_models.CollectiveOfferTemplate.id == offer_id)
        query = query.options(
            sa.orm.joinedload(educational_models.CollectiveOfferTemplate.venue, innerjoin=True,).joinedload(
                offerers_models.Venue.managingOfferer,
                innerjoin=True,
            )
        )
        query = query.options(sa.orm.joinedload(educational_models.CollectiveOfferTemplate.domains))
        return query.one()
    except sa.orm.exc.NoResultFound:
        raise educational_exceptions.CollectiveOfferTemplateNotFound()


def user_has_bookings(user: User) -> bool:
    bookings_query = educational_models.CollectiveBooking.query.join(educational_models.CollectiveBooking.offerer).join(
        offerers_models.Offerer.UserOfferers
    )
    return db.session.query(bookings_query.filter(offerers_models.UserOfferer.userId == user.id).exists()).scalar()


def get_collective_stock_for_offer(offer_id: int) -> educational_models.CollectiveStock | None:
    return (
        educational_models.CollectiveStock.query.options(
            sa.orm.joinedload(educational_models.CollectiveStock.collectiveBookings).load_only(
                educational_models.CollectiveBooking.status
            )
        )
        .filter(educational_models.CollectiveStock.collectiveOfferId == offer_id)
        .one_or_none()
    )


def get_collective_offer_by_offer_id(offer_id: int) -> educational_models.CollectiveOffer:
    return educational_models.CollectiveOffer.query.filter(educational_models.CollectiveOffer.offerId == offer_id).one()


def get_collective_offer_by_id_for_adage(offer_id: int) -> educational_models.CollectiveOffer:
    return (
        educational_models.CollectiveOffer.query.filter(educational_models.CollectiveOffer.id == offer_id)
        .options(
            sa.orm.joinedload(educational_models.CollectiveOffer.collectiveStock).joinedload(
                educational_models.CollectiveStock.collectiveBookings
            )
        )
        .options(sa.orm.joinedload(educational_models.CollectiveOffer.institution))
        .options(
            sa.orm.joinedload(educational_models.CollectiveOffer.venue)
            .joinedload(offerers_models.Venue.managingOfferer)
            .load_only(
                offerers_models.Offerer.name,
                offerers_models.Offerer.validationToken,
                offerers_models.Offerer.isActive,
            )
        )
        .options(sa.orm.joinedload(educational_models.CollectiveOffer.domains))
        .one()
    )


def get_collective_offer_template_by_id_for_adage(offer_id: int) -> educational_models.CollectiveOffer:
    return (
        educational_models.CollectiveOfferTemplate.query.filter(
            educational_models.CollectiveOfferTemplate.id == offer_id
        )
        .options(
            sa.orm.joinedload(educational_models.CollectiveOfferTemplate.venue)
            .joinedload(offerers_models.Venue.managingOfferer)
            .load_only(
                offerers_models.Offerer.name,
                offerers_models.Offerer.validationToken,
                offerers_models.Offerer.isActive,
            )
        )
        .options(sa.orm.joinedload(educational_models.CollectiveOfferTemplate.domains))
        .one()
    )


def get_query_for_collective_offers_by_ids_for_user(user: User, ids: Iterable[int]) -> BaseQuery:
    query = educational_models.CollectiveOffer.query
    if not user.has_admin_role:
        query = query.join(offerers_models.Venue, educational_models.CollectiveOffer.venue)
        query = query.join(offerers_models.Offerer, offerers_models.Venue.managingOfferer)
        query = query.join(offerers_models.UserOfferer, offerers_models.Offerer.UserOfferers)
        query = query.filter(offerers_models.UserOfferer.userId == user.id, offerers_models.UserOfferer.isValidated)
    query = query.filter(educational_models.CollectiveOffer.id.in_(ids))
    return query


def get_query_for_collective_offers_template_by_ids_for_user(user: User, ids: Iterable[int]) -> BaseQuery:
    query = educational_models.CollectiveOfferTemplate.query
    if not user.has_admin_role:
        query = query.join(offerers_models.Venue, educational_models.CollectiveOfferTemplate.venue)
        query = query.join(offerers_models.Offerer, offerers_models.Venue.managingOfferer)
        query = query.join(offerers_models.UserOfferer, offerers_models.Offerer.UserOfferers)
        query = query.filter(offerers_models.UserOfferer.userId == user.id, offerers_models.UserOfferer.isValidated)
    query = query.filter(educational_models.CollectiveOfferTemplate.id.in_(ids))
    return query


def get_educational_domains_from_ids(ids: Iterable[int]) -> list[educational_models.EducationalDomain]:
    return educational_models.EducationalDomain.query.filter(educational_models.EducationalDomain.id.in_(ids)).all()


def get_educational_domains_from_names(names: Iterable[str]) -> list[educational_models.EducationalDomain]:
    return educational_models.EducationalDomain.query.filter(educational_models.EducationalDomain.name.in_(names)).all()


def get_all_educational_domains_ordered_by_name() -> list[educational_models.EducationalDomain]:
    return educational_models.EducationalDomain.query.order_by(educational_models.EducationalDomain.name).all()


def get_all_educational_institutions(offset: int = 0, limit: int = 0) -> tuple[tuple, int]:
    total = db.session.query(sa.func.count(educational_models.EducationalInstitution.id)).one()[0]

    query = educational_models.EducationalInstitution.query
    query = query.order_by(educational_models.EducationalInstitution.name)
    query = query.with_entities(
        educational_models.EducationalInstitution.name,
        educational_models.EducationalInstitution.id,
        educational_models.EducationalInstitution.postalCode,
        educational_models.EducationalInstitution.city,
        educational_models.EducationalInstitution.institutionType,
        educational_models.EducationalInstitution.phoneNumber,
    )

    if offset != 0:
        query = query.offset(offset)
    if limit != 0:
        query = query.limit(limit)

    return query.all(), total


def get_educational_institution_by_id(institution_id: int) -> educational_models.EducationalInstitution:
    try:
        return educational_models.EducationalInstitution.query.filter_by(id=institution_id).one()
    except sa.orm.exc.NoResultFound:
        raise educational_exceptions.EducationalInstitutionNotFound()


def search_educational_institution(
    educational_institution_id: int | None,
    name: str | None,
    institution_type: str | None,
    city: str | None,
    postal_code: str | None,
    limit: int,
) -> educational_models.EducationalInstitution:
    filters = []
    if educational_institution_id is not None:
        filters.append(
            sa.func.unaccent(educational_models.EducationalInstitution.id).ilike(f"%{id}%"),
        )

    if name is not None:
        name = name.replace(" ", "%")
        name = name.replace("-", "%")
        filters.append(
            sa.func.unaccent(educational_models.EducationalInstitution.name).ilike(f"%{clean_accents(name)}%"),
        )

    if institution_type is not None:
        institution_type = institution_type.replace(" ", "%")
        institution_type = institution_type.replace("-", "%")
        filters.append(
            sa.func.unaccent(educational_models.EducationalInstitution.institutionType).ilike(
                f"%{clean_accents(institution_type)}%"
            ),
        )

    if city is not None:
        city = city.replace(" ", "%")
        city = city.replace("-", "%")
        filters.append(
            sa.func.unaccent(educational_models.EducationalInstitution.city).ilike(f"%{clean_accents(city)}%"),
        )

    if postal_code is not None:
        postal_code = postal_code.replace(" ", "%")
        postal_code = postal_code.replace("-", "%")
        filters.append(
            sa.func.unaccent(educational_models.EducationalInstitution.postalCode).ilike(f"%{postal_code}%"),
        )
    return (
        educational_models.EducationalInstitution.query.filter(*filters)
        .order_by(educational_models.EducationalInstitution.id)
        .limit(limit)
        .all()
    )

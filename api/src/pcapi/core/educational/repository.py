from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta
from decimal import Decimal
import typing

from flask_sqlalchemy import BaseQuery
import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from sqlalchemy.sql.expression import extract

from pcapi.core.bookings.repository import field_to_venue_timezone
import pcapi.core.categories.subcategories_v2 as subcategories
from pcapi.core.educational import exceptions as educational_exceptions
from pcapi.core.educational import models as educational_models
from pcapi.core.finance import models as finance_models
from pcapi.core.offerers import exceptions as offerers_exceptions
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import repository as offers_repository
from pcapi.core.providers import models as providers_models
from pcapi.core.users.models import User
from pcapi.models import db
from pcapi.models import offer_mixin
from pcapi.repository import repository
from pcapi.routes.adage_iframe.serialization.adage_authentication import RedactorInformation
from pcapi.utils.clean_accents import clean_accents


COLLECTIVE_BOOKING_STATUS_LABELS = {
    educational_models.CollectiveBookingStatus.PENDING: "préréservé",
    educational_models.CollectiveBookingStatus.CONFIRMED: "réservé",
    educational_models.CollectiveBookingStatus.CANCELLED: "annulé",
    educational_models.CollectiveBookingStatus.USED: "validé",
    educational_models.CollectiveBookingStatus.REIMBURSED: "remboursé",
    "confirmed": "confirmé",
}


BOOKING_DATE_STATUS_MAPPING: dict[educational_models.CollectiveBookingStatusFilter, sa_orm.InstrumentedAttribute] = {
    educational_models.CollectiveBookingStatusFilter.BOOKED: educational_models.CollectiveBooking.dateCreated,
    educational_models.CollectiveBookingStatusFilter.VALIDATED: educational_models.CollectiveBooking.dateUsed,
    educational_models.CollectiveBookingStatusFilter.REIMBURSED: educational_models.CollectiveBooking.reimbursementDate,
}


def find_bookings_happening_in_x_days(number_of_days: int) -> list[educational_models.CollectiveBooking]:
    target_day = datetime.utcnow() + timedelta(days=number_of_days)
    start = datetime.combine(target_day, time.min)
    end = datetime.combine(target_day, time.max)
    return find_bookings_starting_in_interval(start, end)


def find_bookings_starting_in_interval(start: datetime, end: datetime) -> list[educational_models.CollectiveBooking]:
    query = educational_models.CollectiveBooking.query.join(
        educational_models.CollectiveStock, educational_models.CollectiveBooking.collectiveStock
    )
    query = query.filter(
        educational_models.CollectiveStock.beginningDatetime.between(start, end),
        educational_models.CollectiveBooking.status != educational_models.CollectiveBookingStatus.CANCELLED,
    )
    query = query.options(sa.orm.joinedload(educational_models.CollectiveBooking.collectiveStock, innerjoin=True))
    query = query.options(
        sa.orm.joinedload(educational_models.CollectiveBooking.collectiveStock, innerjoin=True).joinedload(
            educational_models.CollectiveStock.collectiveOffer, innerjoin=True
        )
    )
    query = query.options(
        sa.orm.joinedload(educational_models.CollectiveBooking.collectiveStock, innerjoin=True)
        .joinedload(educational_models.CollectiveStock.collectiveOffer, innerjoin=True)
        .joinedload(educational_models.CollectiveOffer.venue, innerjoin=True)
    )
    query = query.options(sa.orm.joinedload(educational_models.CollectiveBooking.educationalRedactor, innerjoin=True))
    query = query.options(
        sa.orm.joinedload(educational_models.CollectiveBooking.educationalInstitution, innerjoin=True)
    )
    return query.distinct().all()


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


def get_ministry_budget_for_year(
    ministry: educational_models.Ministry | None,
    educational_year_id: str,
) -> Decimal:
    query = db.session.query(sa.func.sum(educational_models.EducationalDeposit.amount).label("amount"))
    query = query.filter(
        educational_models.EducationalDeposit.educationalYearId == educational_year_id,
        educational_models.EducationalDeposit.ministry == ministry,
    )
    return query.first().amount or Decimal(0)


def get_confirmed_collective_bookings_amount_for_ministry(
    ministry: educational_models.Ministry | None,
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
        educational_models.CollectiveBooking.status.not_in(
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
        educational_models.CollectiveBooking.status.not_in(
            [educational_models.CollectiveBookingStatus.CANCELLED, educational_models.CollectiveBookingStatus.PENDING]
        ),
    )
    return query.first().amount or Decimal(0)


def find_collective_booking_by_id(booking_id: int) -> educational_models.CollectiveBooking | None:
    query = _get_bookings_for_adage_base_query()
    query = query.filter(educational_models.CollectiveBooking.id == booking_id)
    return query.one_or_none()


def find_educational_year_by_date(date_searched: datetime) -> educational_models.EducationalYear | None:
    return educational_models.EducationalYear.query.filter(
        date_searched >= educational_models.EducationalYear.beginningDate,
        date_searched <= educational_models.EducationalYear.expirationDate,
    ).one_or_none()


def find_educational_institution_by_uai_code(uai_code: str | None) -> educational_models.EducationalInstitution | None:
    return (
        educational_models.EducationalInstitution.query.filter_by(institutionId=uai_code)
        .options(sa.orm.joinedload(educational_models.EducationalInstitution.programs))
        .one_or_none()
    )


def find_educational_deposit_by_institution_id_and_year(
    educational_institution_id: int,
    educational_year_id: str,
) -> educational_models.EducationalDeposit | None:
    return educational_models.EducationalDeposit.query.filter(
        educational_models.EducationalDeposit.educationalInstitutionId == educational_institution_id,
        educational_models.EducationalDeposit.educationalYearId == educational_year_id,
    ).one_or_none()


def get_educational_deposits_by_year(year_id: str) -> list[educational_models.EducationalDeposit]:
    return (
        educational_models.EducationalDeposit.query.join(educational_models.EducationalDeposit.educationalInstitution)
        .filter(educational_models.EducationalDeposit.educationalYearId == year_id)
        .options(sa.orm.joinedload(educational_models.EducationalDeposit.educationalInstitution))
        .all()
    )


def get_educational_year_beginning_at_given_year(year: int) -> educational_models.EducationalYear:
    educational_year = educational_models.EducationalYear.query.filter(
        extract("year", educational_models.EducationalYear.beginningDate) == year
    ).one_or_none()
    if educational_year is None:
        raise educational_exceptions.EducationalYearNotFound()
    return educational_year


def _get_bookings_for_adage_base_query() -> BaseQuery:
    query = educational_models.CollectiveBooking.query
    query = query.options(
        sa.orm.joinedload(educational_models.CollectiveBooking.collectiveStock, innerjoin=True)
        .load_only(
            educational_models.CollectiveStock.beginningDatetime,
            educational_models.CollectiveStock.startDatetime,
            educational_models.CollectiveStock.endDatetime,
            educational_models.CollectiveStock.numberOfTickets,
            educational_models.CollectiveStock.priceDetail,
            educational_models.CollectiveStock.price,
            educational_models.CollectiveStock.collectiveOfferId,
        )
        .joinedload(educational_models.CollectiveStock.collectiveOffer, innerjoin=True)
        .load_only(
            educational_models.CollectiveOffer.audioDisabilityCompliant,
            educational_models.CollectiveOffer.mentalDisabilityCompliant,
            educational_models.CollectiveOffer.motorDisabilityCompliant,
            educational_models.CollectiveOffer.visualDisabilityCompliant,
            educational_models.CollectiveOffer.offerVenue,
            educational_models.CollectiveOffer.contactEmail,
            educational_models.CollectiveOffer.contactPhone,
            educational_models.CollectiveOffer.description,
            educational_models.CollectiveOffer.durationMinutes,
            educational_models.CollectiveOffer.name,
            educational_models.CollectiveOffer.students,
            educational_models.CollectiveOffer.subcategoryId,
            educational_models.CollectiveOffer.id,
            educational_models.CollectiveOffer.interventionArea,
            educational_models.CollectiveOffer.imageCredit,
            educational_models.CollectiveOffer.imageId,
            educational_models.CollectiveOffer.bookingEmails,
            educational_models.CollectiveOffer.formats,
        )
        .options(
            sa.orm.joinedload(educational_models.CollectiveOffer.domains).load_only(
                educational_models.EducationalDomain.id
            ),
            sa.orm.joinedload(educational_models.CollectiveOffer.venue, innerjoin=True)
            .load_only(
                offerers_models.Venue.city,
                offerers_models.Venue.postalCode,
                offerers_models.Venue.latitude,
                offerers_models.Venue.longitude,
                offerers_models.Venue.timezone,
                offerers_models.Venue.publicName,
                offerers_models.Venue.name,
                offerers_models.Venue.street,
            )
            .joinedload(offerers_models.Venue.managingOfferer)
            .load_only(offerers_models.Offerer.name),
        )
    )

    query = query.options(sa.orm.joinedload(educational_models.CollectiveBooking.educationalInstitution))
    query = query.options(sa.orm.joinedload(educational_models.CollectiveBooking.educationalRedactor))

    return query


def find_collective_bookings_for_adage(
    uai_code: str,
    year_id: str,
    redactor_email: str | None = None,
) -> list[educational_models.CollectiveBooking]:
    query = _get_bookings_for_adage_base_query()

    query = query.join(educational_models.EducationalInstitution)
    query = query.join(educational_models.EducationalRedactor)
    query = query.join(educational_models.EducationalYear)

    query = query.filter(educational_models.EducationalInstitution.institutionId == uai_code)
    query = query.filter(educational_models.EducationalYear.adageId == year_id)

    if redactor_email is not None:
        query = query.filter(educational_models.EducationalRedactor.email == redactor_email)

    return query.all()


def find_redactor_by_email(redactor_email: str) -> educational_models.EducationalRedactor | None:
    return educational_models.EducationalRedactor.query.filter(
        educational_models.EducationalRedactor.email == redactor_email
    ).one_or_none()


def find_or_create_redactor(information: RedactorInformation) -> educational_models.EducationalRedactor:
    redactor = find_redactor_by_email(information.email)
    if redactor:
        return redactor

    redactor = educational_models.EducationalRedactor(
        email=information.email,
        firstName=information.firstname,
        lastName=information.lastname,
        civility=information.civility,
    )

    repository.save(redactor)
    return redactor


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

    query = educational_models.CollectiveBooking.query.filter(
        educational_models.CollectiveBooking.educationalYearId == educational_year_id
    )
    query = query.options(
        sa.orm.load_only(
            educational_models.CollectiveBooking.id,
            educational_models.CollectiveBooking.collectiveStockId,
            educational_models.CollectiveBooking.status,
            educational_models.CollectiveBooking.confirmationLimitDate,
            educational_models.CollectiveBooking.cancellationReason,
            educational_models.CollectiveBooking.dateCreated,
            educational_models.CollectiveBooking.dateUsed,
            educational_models.CollectiveBooking.offererId,
            educational_models.CollectiveBooking.cancellationDate,
            educational_models.CollectiveBooking.cancellationLimitDate,
        )
    )
    query = query.options(
        # fetch a collective booking's stock...
        sa.orm.joinedload(educational_models.CollectiveBooking.collectiveStock, innerjoin=True)
        .load_only(
            educational_models.CollectiveStock.beginningDatetime,
            educational_models.CollectiveStock.startDatetime,
            educational_models.CollectiveStock.endDatetime,
            educational_models.CollectiveStock.collectiveOfferId,
            educational_models.CollectiveStock.price,
        )
        # ...to fetch its offer...
        .joinedload(educational_models.CollectiveStock.collectiveOffer, innerjoin=True)
        .load_only(
            educational_models.CollectiveOffer.name,
            educational_models.CollectiveOffer.venueId,
            educational_models.CollectiveOffer.formats,
        )
        .options(
            # ... to fetch its venue...
            sa.orm.joinedload(educational_models.CollectiveOffer.venue, innerjoin=True).load_only(
                offerers_models.Venue.id,
                offerers_models.Venue.name,
                offerers_models.Venue.timezone,
            )
            # ... to fetch its offerer.
            .joinedload(offerers_models.Venue.managingOfferer).load_only(offerers_models.Offerer.name),
            # and the offer's domains
            sa.orm.joinedload(educational_models.CollectiveOffer.domains).load_only(
                educational_models.EducationalDomain.id
            ),
        )
    )
    query = query.options(
        sa.orm.joinedload(educational_models.CollectiveBooking.educationalInstitution, innerjoin=True).load_only(
            educational_models.EducationalInstitution.institutionId
        )
    )
    query = query.options(
        sa.orm.joinedload(educational_models.CollectiveBooking.educationalRedactor, innerjoin=True).load_only(
            educational_models.EducationalRedactor.email
        )
    )
    query = query.order_by(educational_models.CollectiveBooking.id)
    query = query.offset((page - 1) * per_page)
    query = query.limit(per_page)
    return query.all()


def get_expired_collective_offers_template() -> BaseQuery:
    """Return a query of collective offers template whose latest booking limit occurs within
    the given interval.
    """
    return (
        educational_models.CollectiveOfferTemplate.query.group_by(educational_models.CollectiveOfferTemplate.id)
        .order_by(educational_models.CollectiveOfferTemplate.id)
        .filter_by(hasEndDatePassed=True)
    )


def find_expiring_collective_bookings_query() -> BaseQuery:
    today_at_midnight = datetime.combine(date.today(), time(0, 0))

    return educational_models.CollectiveBooking.query.filter(
        educational_models.CollectiveBooking.status == educational_models.CollectiveBookingStatus.PENDING,
        educational_models.CollectiveBooking.confirmationLimitDate <= today_at_midnight,
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
                educational_models.CollectiveStock.startDatetime,
                educational_models.CollectiveStock.endDatetime,
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
    # Use `with_for_update()` to make sure we lock the stock while performing
    # the booking checks and update the `dnBookedQuantity`
    # This is required to prevent bugs due to concurrent access
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
    period_beginning_date: date | None = None,
    period_ending_date: date | None = None,
    formats: list[subcategories.EacFormat] | None = None,
) -> list[educational_models.CollectiveOffer]:
    query = offers_repository.get_collective_offers_by_filters(
        user_id=user_id,
        user_is_admin=user_is_admin,
        offerer_id=offerer_id,
        status=status,
        venue_id=venue_id,
        category_id=category_id,
        name_keywords=name_keywords,
        period_beginning_date=period_beginning_date,
        period_ending_date=period_ending_date,
        formats=formats,
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
    period_beginning_date: date | None = None,
    period_ending_date: date | None = None,
    formats: list[subcategories.EacFormat] | None = None,
) -> list[educational_models.CollectiveOfferTemplate]:
    query = offers_repository.get_collective_offers_template_by_filters(
        user_id=user_id,
        user_is_admin=user_is_admin,
        offerer_id=offerer_id,
        status=status,
        venue_id=venue_id,
        category_id=category_id,
        name_keywords=name_keywords,
        period_beginning_date=period_beginning_date,
        period_ending_date=period_ending_date,
        formats=formats,
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
    extra_joins: typing.Iterable[sa.Column] | None = None,
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

        if all(period):
            collective_bookings_query = collective_bookings_query.filter(
                field_to_venue_timezone(period_attribute_filter).between(*period, symmetric=True)
            )
        elif period[0]:
            collective_bookings_query = collective_bookings_query.filter(
                field_to_venue_timezone(period_attribute_filter) >= period[0]
            )
        elif period[1]:
            collective_bookings_query = collective_bookings_query.filter(
                field_to_venue_timezone(period_attribute_filter) <= period[1]
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
    required_id: int,
    status: offer_mixin.OfferStatus | None = None,
    venue_id: int | None = None,
    period_beginning_date: str | None = None,
    period_ending_date: str | None = None,
    limit: int = 500,
) -> list[educational_models.CollectiveOffer]:
    query = educational_models.CollectiveOffer.query

    query = query.join(providers_models.Provider, educational_models.CollectiveOffer.provider)
    query = query.join(educational_models.CollectiveStock, educational_models.CollectiveOffer.collectiveStock)
    filters = [
        educational_models.CollectiveOffer.providerId == required_id,
        educational_models.CollectiveOffer.validation != offer_mixin.OfferValidationStatus.DRAFT,
    ]

    if status:
        filters.append(educational_models.CollectiveOffer.status == status)
    if venue_id:
        filters.append(educational_models.CollectiveOffer.venueId == venue_id)
    if period_beginning_date:
        filters.append(educational_models.CollectiveStock.beginningDatetime >= period_beginning_date)
    if period_ending_date:
        filters.append(educational_models.CollectiveStock.beginningDatetime <= period_ending_date)
    query = query.filter(*filters)
    query = query.options(
        sa.orm.joinedload(educational_models.CollectiveOffer.collectiveStock)
        .load_only(
            educational_models.CollectiveStock.bookingLimitDatetime,
            educational_models.CollectiveStock.beginningDatetime,
            educational_models.CollectiveStock.startDatetime,
            educational_models.CollectiveStock.endDatetime,
        )
        .joinedload(educational_models.CollectiveStock.collectiveBookings)
        .load_only(
            educational_models.CollectiveBooking.id,
            educational_models.CollectiveBooking.status,
            educational_models.CollectiveBooking.confirmationDate,
            educational_models.CollectiveBooking.cancellationLimitDate,
            educational_models.CollectiveBooking.reimbursementDate,
            educational_models.CollectiveBooking.dateUsed,
            educational_models.CollectiveBooking.dateCreated,
        )
    )

    query = query.order_by(educational_models.CollectiveOffer.id)
    query = query.limit(limit)
    return query.all()


def _get_filtered_collective_bookings_pro(
    pro_user: User,
    period: tuple[date, date] | None = None,
    status_filter: educational_models.CollectiveBookingStatusFilter | None = None,
    event_date: datetime | None = None,
    venue_id: int | None = None,
) -> sa.orm.Query:
    bookings_query = (
        _get_filtered_collective_bookings_query(
            pro_user,
            period,
            status_filter,
            event_date,
            venue_id,
            extra_joins=(
                educational_models.CollectiveStock.collectiveOffer,
                educational_models.CollectiveBooking.educationalInstitution,
            ),
        )
        .options(sa.orm.joinedload(educational_models.CollectiveBooking.collectiveStock))
        .options(
            sa.orm.joinedload(educational_models.CollectiveBooking.collectiveStock).joinedload(
                educational_models.CollectiveStock.collectiveOffer
            )
        )
        .options(sa.orm.joinedload(educational_models.CollectiveBooking.educationalInstitution))
        .options(sa.orm.joinedload(educational_models.CollectiveBooking.venue))
        .options(sa.orm.joinedload(educational_models.CollectiveBooking.offerer))
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
) -> tuple[int, list[educational_models.CollectiveBooking]]:
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
        pro_user=user,
        period=booking_period,
        status_filter=status_filter,
        event_date=event_date,
        venue_id=venue_id,
    )
    collective_bookings_page = (
        collective_bookings_query.order_by(
            educational_models.CollectiveBooking.id.desc(), educational_models.CollectiveBooking.dateCreated.desc()
        )
        .offset((page - 1) * per_page_limit)
        .limit(per_page_limit)
        .all()
    )
    return total_collective_bookings, collective_bookings_page


def get_filtered_collective_booking_report(
    pro_user: User,
    period: tuple[date, date] | None,
    status_filter: educational_models.CollectiveBookingStatusFilter | None,
    event_date: datetime | None = None,
    venue_id: int | None = None,
) -> BaseQuery:
    bookings_query = _get_filtered_collective_bookings_query(
        pro_user,
        period,
        status_filter,
        event_date,
        venue_id,
        extra_joins=(
            educational_models.CollectiveStock.collectiveOffer,
            educational_models.CollectiveBooking.educationalRedactor,
            educational_models.CollectiveBooking.educationalInstitution,
        ),
    )
    bookings_query = bookings_query.with_entities(
        offerers_models.Venue.common_name.label("venueName"),  # type: ignore[attr-defined]
        offerers_models.Venue.departementCode.label("venueDepartmentCode"),
        offerers_models.Offerer.postalCode.label("offererPostalCode"),
        educational_models.CollectiveOffer.name.label("offerName"),
        educational_models.CollectiveStock.price,
        educational_models.CollectiveStock.beginningDatetime.label("stockBeginningDatetime"),
        educational_models.CollectiveStock.beginningDatetime.label("stockBookingLimitDatetime"),
        educational_models.EducationalRedactor.firstName,
        educational_models.EducationalRedactor.lastName,
        educational_models.EducationalRedactor.email,
        educational_models.CollectiveBooking.id,
        educational_models.CollectiveBooking.dateCreated.label("bookedAt"),
        educational_models.CollectiveBooking.dateUsed.label("usedAt"),
        educational_models.CollectiveBooking.reimbursementDate.label("reimbursedAt"),
        educational_models.CollectiveBooking.status,
        educational_models.CollectiveBooking.isConfirmed,
        educational_models.EducationalInstitution.institutionId,
        educational_models.EducationalInstitution.name.label("institutionName"),
        educational_models.EducationalInstitution.institutionType,
        # `get_batch` function needs a field called exactly `id` to work,
        # the label prevents SA from using a bad (prefixed) label for this field
        educational_models.CollectiveBooking.id.label("id"),
        educational_models.CollectiveBooking.educationalRedactorId,
    )
    bookings_query = bookings_query.distinct(educational_models.CollectiveBooking.id)

    return bookings_query


def get_collective_offer_by_id(offer_id: int) -> educational_models.CollectiveOffer:
    try:
        return (
            educational_models.CollectiveOffer.query.filter(educational_models.CollectiveOffer.id == offer_id)
            .outerjoin(
                educational_models.CollectiveStock, educational_models.CollectiveStock.collectiveOfferId == offer_id
            )
            .options(
                sa.orm.joinedload(
                    educational_models.CollectiveOffer.venue,
                    innerjoin=True,
                ).joinedload(
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


def get_collective_offer_and_extra_data(offer_id: int) -> educational_models.CollectiveOffer | None:
    is_non_free_offer_subquery = (
        sa.select(1)
        .select_from(educational_models.CollectiveStock)
        .where(
            educational_models.CollectiveStock.collectiveOfferId == educational_models.CollectiveOffer.id,
            educational_models.CollectiveStock.price > 0,
        )
        .correlate(educational_models.CollectiveOffer)
        .exists()
    )

    collective_offer = (
        db.session.query(educational_models.CollectiveOffer)
        .filter(educational_models.CollectiveOffer.id == offer_id)
        .outerjoin(educational_models.CollectiveStock, educational_models.CollectiveStock.collectiveOfferId == offer_id)
        .options(
            sa.orm.joinedload(
                educational_models.CollectiveOffer.venue,
                innerjoin=True,
            )
            .load_only(offerers_models.Venue.id)
            .joinedload(
                offerers_models.Venue.managingOfferer,
                innerjoin=True,
            )
            .load_only(offerers_models.Offerer.id)
            .joinedload(offerers_models.Offerer.confidenceRule)
            .load_only(offerers_models.OffererConfidenceRule.confidenceLevel),
            sa.orm.joinedload(
                educational_models.CollectiveOffer.venue,
                innerjoin=True,
            )
            .load_only(offerers_models.Venue.id)
            .joinedload(offerers_models.Venue.confidenceRule)
            .load_only(offerers_models.OffererConfidenceRule.confidenceLevel),
        )
        .options(sa.orm.joinedload(educational_models.CollectiveOffer.domains))
        .options(
            sa.orm.joinedload(educational_models.CollectiveOffer.collectiveStock)
            .joinedload(educational_models.CollectiveStock.collectiveBookings)
            .load_only(educational_models.CollectiveBooking.id)
        )
        .options(sa.orm.with_expression(educational_models.CollectiveOffer.isNonFreeOffer, is_non_free_offer_subquery))
        .one_or_none()
    )

    return collective_offer


def get_collective_offer_request_by_id(request_id: int) -> educational_models.CollectiveOfferRequest:
    try:
        query = educational_models.CollectiveOfferRequest.query.filter(
            educational_models.CollectiveOfferRequest.id == request_id
        ).options(
            sa.orm.joinedload(educational_models.CollectiveOfferRequest.collectiveOfferTemplate)
            .load_only(educational_models.CollectiveOfferTemplate.id)
            .joinedload(educational_models.CollectiveOfferTemplate.venue)
            .load_only(offerers_models.Venue.managingOffererId),
            sa.orm.joinedload(educational_models.CollectiveOfferRequest.educationalRedactor).load_only(
                educational_models.EducationalRedactor.firstName,
                educational_models.EducationalRedactor.lastName,
                educational_models.EducationalRedactor.email,
            ),
            sa.orm.joinedload(educational_models.CollectiveOfferRequest.educationalInstitution),
        )

        return query.one()
    except sa.orm.exc.NoResultFound:
        raise educational_exceptions.CollectiveOfferRequestNotFound()


def get_offerer_ids_from_collective_offers_ids(offers_ids: list[int]) -> set[int]:
    query = db.session.query(offerers_models.Offerer.id)
    query = query.join(offerers_models.Offerer, offerers_models.Venue.managingOfferer)
    query = query.join(educational_models.CollectiveOffer, offerers_models.Venue.collectiveOffers)
    query = query.filter(educational_models.CollectiveOffer.id.in_(offers_ids))
    return {result[0] for result in query.all()}


def get_offerer_ids_from_collective_offers_template_ids(offers_ids: list[int]) -> set[int]:
    query = db.session.query(offerers_models.Offerer.id)
    query = query.join(offerers_models.Offerer, offerers_models.Venue.managingOfferer)
    query = query.join(educational_models.CollectiveOfferTemplate, offerers_models.Venue.collectiveOfferTemplates)
    query = query.filter(educational_models.CollectiveOfferTemplate.id.in_(offers_ids))
    return {result[0] for result in query.all()}


def get_collective_offer_template_by_id(offer_id: int) -> educational_models.CollectiveOfferTemplate:
    try:
        query = educational_models.CollectiveOfferTemplate.query
        query = query.filter(educational_models.CollectiveOfferTemplate.id == offer_id)
        query = query.options(
            sa.orm.joinedload(
                educational_models.CollectiveOfferTemplate.venue,
                innerjoin=True,
            ).joinedload(
                offerers_models.Venue.managingOfferer,
                innerjoin=True,
            )
        )
        query = query.options(sa.orm.joinedload(educational_models.CollectiveOfferTemplate.domains))
        return query.one()
    except sa.orm.exc.NoResultFound:
        raise educational_exceptions.CollectiveOfferTemplateNotFound()


def get_collective_offer_template_by_ids(offer_ids: list[int]) -> list[educational_models.CollectiveOfferTemplate]:
    query = educational_models.CollectiveOfferTemplate.query
    query = query.filter(educational_models.CollectiveOfferTemplate.id.in_(offer_ids))
    query = query.options(
        sa.orm.joinedload(
            educational_models.CollectiveOfferTemplate.venue,
            innerjoin=True,
        ).joinedload(
            offerers_models.Venue.managingOfferer,
            innerjoin=True,
        )
    )
    query = query.options(sa.orm.joinedload(educational_models.CollectiveOfferTemplate.domains))
    return query


def get_collective_offer_templates_for_playlist_query(
    institution_id: int,
    playlist_type: educational_models.PlaylistType,
    max_distance: int | None = None,
    min_distance: int | None = None,
) -> BaseQuery:
    query = educational_models.CollectivePlaylist.query.filter(
        educational_models.CollectivePlaylist.type == playlist_type,
        educational_models.CollectivePlaylist.institutionId == institution_id,
    )

    if max_distance:
        query = query.filter(educational_models.CollectivePlaylist.distanceInKm <= max_distance)

    if min_distance:
        query = query.filter(educational_models.CollectivePlaylist.distanceInKm > min_distance)

    query = query.options(
        sa.orm.joinedload(educational_models.CollectivePlaylist.collective_offer_template)
        .joinedload(
            educational_models.CollectiveOfferTemplate.venue,
            innerjoin=True,
        )
        .joinedload(
            offerers_models.Venue.managingOfferer,
            innerjoin=True,
        ),
        sa.orm.joinedload(educational_models.CollectivePlaylist.collective_offer_template).joinedload(
            educational_models.CollectiveOfferTemplate.domains
        ),
        sa.orm.joinedload(educational_models.CollectivePlaylist.collective_offer_template)
        .joinedload(
            educational_models.CollectiveOfferTemplate.venue,
            innerjoin=True,
        )
        .joinedload(offerers_models.Venue.googlePlacesInfo),
        sa.orm.joinedload(educational_models.CollectivePlaylist.venue).joinedload(
            offerers_models.Venue.googlePlacesInfo
        ),
    )
    return query


def user_has_bookings(user: User) -> bool:
    bookings_query = educational_models.CollectiveBooking.query.join(educational_models.CollectiveBooking.offerer).join(
        offerers_models.Offerer.UserOfferers
    )
    return db.session.query(bookings_query.filter(offerers_models.UserOfferer.userId == user.id).exists()).scalar()


def get_collective_offer_by_id_for_adage(offer_id: int) -> educational_models.CollectiveOffer:
    query = educational_models.CollectiveOffer.query.filter(
        educational_models.CollectiveOffer.validation == offer_mixin.OfferValidationStatus.APPROVED,
    ).options(
        sa.orm.joinedload(educational_models.CollectiveOffer.nationalProgram),
        sa.orm.joinedload(educational_models.CollectiveOffer.teacher).load_only(
            educational_models.EducationalRedactor.email,
            educational_models.EducationalRedactor.firstName,
            educational_models.EducationalRedactor.lastName,
            educational_models.EducationalRedactor.civility,
        ),
        sa.orm.joinedload(educational_models.CollectiveOffer.collectiveStock).joinedload(
            educational_models.CollectiveStock.collectiveBookings
        ),
        sa.orm.joinedload(educational_models.CollectiveOffer.institution),
        sa.orm.joinedload(educational_models.CollectiveOffer.venue)
        .joinedload(offerers_models.Venue.managingOfferer)
        .load_only(
            offerers_models.Offerer.name,
            offerers_models.Offerer.validationStatus,
            offerers_models.Offerer.isActive,
        ),
        sa.orm.joinedload(educational_models.CollectiveOffer.domains),
    )
    return query.filter(educational_models.CollectiveOffer.id == offer_id).one()


def _get_collective_offer_template_by_id_for_adage_base_query() -> BaseQuery:
    return educational_models.CollectiveOfferTemplate.query.filter(
        educational_models.CollectiveOfferTemplate.validation == offer_mixin.OfferValidationStatus.APPROVED,
    ).options(
        sa.orm.joinedload(educational_models.CollectiveOfferTemplate.nationalProgram),
        sa.orm.joinedload(educational_models.CollectiveOfferTemplate.venue)
        .joinedload(offerers_models.Venue.managingOfferer)
        .load_only(
            offerers_models.Offerer.name,
            offerers_models.Offerer.validationStatus,
            offerers_models.Offerer.isActive,
        ),
        sa.orm.joinedload(educational_models.CollectiveOfferTemplate.venue).joinedload(
            offerers_models.Venue.googlePlacesInfo
        ),
        sa.orm.joinedload(educational_models.CollectiveOfferTemplate.domains),
    )


def get_collective_offer_template_by_id_for_adage(offer_id: int) -> educational_models.CollectiveOffer:
    query = _get_collective_offer_template_by_id_for_adage_base_query()
    return query.filter(educational_models.CollectiveOfferTemplate.id == offer_id).one()


def get_collective_offer_templates_by_ids_for_adage(offer_ids: typing.Collection[int]) -> BaseQuery:
    query = _get_collective_offer_template_by_id_for_adage_base_query()
    return query.filter(educational_models.CollectiveOfferTemplate.id.in_(offer_ids))


def get_query_for_collective_offers_by_ids_for_user(user: User, ids: typing.Iterable[int]) -> BaseQuery:
    query = educational_models.CollectiveOffer.query
    if not user.has_admin_role:
        query = query.join(offerers_models.Venue, educational_models.CollectiveOffer.venue)
        query = query.join(offerers_models.Offerer, offerers_models.Venue.managingOfferer)
        query = query.join(offerers_models.UserOfferer, offerers_models.Offerer.UserOfferers)
        query = query.filter(offerers_models.UserOfferer.userId == user.id, offerers_models.UserOfferer.isValidated)
    query = query.filter(educational_models.CollectiveOffer.id.in_(ids))
    return query


def get_query_for_collective_offers_template_by_ids_for_user(user: User, ids: typing.Iterable[int]) -> BaseQuery:
    query = educational_models.CollectiveOfferTemplate.query
    if not user.has_admin_role:
        query = query.join(offerers_models.Venue, educational_models.CollectiveOfferTemplate.venue)
        query = query.join(offerers_models.Offerer, offerers_models.Venue.managingOfferer)
        query = query.join(offerers_models.UserOfferer, offerers_models.Offerer.UserOfferers)
        query = query.filter(offerers_models.UserOfferer.userId == user.id, offerers_models.UserOfferer.isValidated)
    query = query.filter(educational_models.CollectiveOfferTemplate.id.in_(ids))
    return query


def get_educational_domains_from_ids(ids: typing.Iterable[int]) -> list[educational_models.EducationalDomain]:
    return (
        educational_models.EducationalDomain.query.filter(educational_models.EducationalDomain.id.in_(ids))
        .options(sa.orm.joinedload(educational_models.EducationalDomain.nationalPrograms))
        .all()
    )


def get_all_educational_domains_ordered_by_name() -> list[educational_models.EducationalDomain]:
    return educational_models.EducationalDomain.query.order_by(educational_models.EducationalDomain.name).all()


def get_all_educational_institutions(offset: int = 0, limit: int = 0) -> tuple[tuple, int]:
    query = db.session.query(sa.func.count(educational_models.EducationalInstitution.id))
    query = query.filter(educational_models.EducationalInstitution.isActive)
    total = query.one()[0]

    query = educational_models.EducationalInstitution.query
    query = query.filter(educational_models.EducationalInstitution.isActive)
    query = query.order_by(
        educational_models.EducationalInstitution.name,
        educational_models.EducationalInstitution.id,
    )
    query = query.with_entities(
        educational_models.EducationalInstitution.name,
        educational_models.EducationalInstitution.id,
        educational_models.EducationalInstitution.postalCode,
        educational_models.EducationalInstitution.city,
        educational_models.EducationalInstitution.institutionType,
        educational_models.EducationalInstitution.phoneNumber,
        educational_models.EducationalInstitution.institutionId,
    )

    if offset != 0:
        query = query.offset(offset)
    if limit != 0:
        query = query.limit(limit)

    return query.all(), total


def search_educational_institution(
    educational_institution_id: int | None,
    name: str | None,
    institution_type: str | None,
    city: str | None,
    postal_code: str | None,
    uai: str | None,
    limit: int,
) -> educational_models.EducationalInstitution:
    filters = []
    if educational_institution_id is not None:
        filters.append(educational_models.EducationalInstitution.id == educational_institution_id)

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

    if uai is not None:
        filters.append(educational_models.EducationalInstitution.institutionId == uai)

    return (
        educational_models.EducationalInstitution.query.filter(
            *filters,
            educational_models.EducationalInstitution.isActive,
        )
        .order_by(educational_models.EducationalInstitution.id)
        .limit(limit)
        .all()
    )


def find_pending_booking_confirmation_limit_date_in_3_days() -> list[educational_models.CollectiveBooking]:
    target_day = datetime.utcnow() + timedelta(days=3)
    start = datetime.combine(target_day, time.min)
    end = datetime.combine(target_day, time.max)
    query = (
        educational_models.CollectiveBooking.query.filter(
            educational_models.CollectiveBooking.confirmationLimitDate.between(start, end)
        )
        .filter(educational_models.CollectiveBooking.status == educational_models.CollectiveBookingStatus.PENDING)
        .distinct()
    )
    query = query.options(sa.orm.joinedload(educational_models.CollectiveBooking.collectiveStock, innerjoin=True))
    query = query.options(
        sa.orm.joinedload(educational_models.CollectiveBooking.collectiveStock, innerjoin=True).joinedload(
            educational_models.CollectiveStock.collectiveOffer, innerjoin=True
        )
    )
    query = query.options(
        sa.orm.joinedload(educational_models.CollectiveBooking.collectiveStock, innerjoin=True)
        .joinedload(educational_models.CollectiveStock.collectiveOffer, innerjoin=True)
        .joinedload(educational_models.CollectiveOffer.venue, innerjoin=True)
    )
    query = query.options(sa.orm.joinedload(educational_models.CollectiveBooking.educationalRedactor, innerjoin=True))
    return query.all()


def get_paginated_active_collective_offer_template_ids(batch_size: int, page: int = 1) -> list[int]:
    query = (
        educational_models.CollectiveOfferTemplate.query.with_entities(educational_models.CollectiveOfferTemplate.id)
        .filter(
            educational_models.CollectiveOfferTemplate.isActive.is_(True),
        )
        .order_by(educational_models.CollectiveOfferTemplate.id)
        .offset((page - 1) * batch_size)  # first page is 1, not 0
        .limit(batch_size)
    )
    return [offer_id for offer_id, in query]


def get_booking_related_bank_account(booking_id: int) -> offerers_models.VenueBankAccountLink | None:
    return (
        finance_models.BankAccount.query.join(
            offerers_models.VenueBankAccountLink,
            sa.and_(
                offerers_models.VenueBankAccountLink.bankAccountId == finance_models.BankAccount.id,
                offerers_models.VenueBankAccountLink.timespan.contains(datetime.utcnow()),
            ),
        )
        .join(offerers_models.Venue, offerers_models.VenueBankAccountLink.venueId == offerers_models.Venue.id)
        .join(
            educational_models.CollectiveBooking,
            educational_models.CollectiveBooking.venueId == offerers_models.Venue.id,
        )
        .filter(educational_models.CollectiveBooking.id == booking_id)
        .options(sa.orm.load_only(finance_models.BankAccount.status, finance_models.BankAccount.dsApplicationId))
        .one_or_none()
    )


def get_educational_institution_public(
    institution_id: int | None, uai: str | None
) -> educational_models.EducationalInstitution | None:
    return educational_models.EducationalInstitution.query.filter(
        sa.or_(
            educational_models.EducationalInstitution.institutionId == uai,
            educational_models.EducationalInstitution.id == institution_id,
        ),
    ).one_or_none()


def get_all_offer_by_redactor_id(redactor_id: int) -> list[educational_models.CollectiveOffer]:
    return (
        educational_models.CollectiveOffer.query.join(
            educational_models.EducationalRedactor, educational_models.CollectiveOffer.educationalRedactorsFavorite
        )
        .options(
            sa_orm.joinedload(educational_models.CollectiveOffer.collectiveStock).joinedload(
                educational_models.CollectiveStock.collectiveBookings
            ),
            sa_orm.joinedload(educational_models.CollectiveOffer.nationalProgram),
            sa_orm.joinedload(educational_models.CollectiveOffer.domains),
            sa_orm.joinedload(educational_models.CollectiveOffer.teacher),
            sa_orm.joinedload(educational_models.CollectiveOffer.venue).joinedload(
                offerers_models.Venue.managingOfferer
            ),
            sa_orm.joinedload(educational_models.CollectiveOffer.venue).selectinload(
                offerers_models.Venue.googlePlacesInfo
            ),
        )
        .filter(educational_models.EducationalRedactor.id == redactor_id)
        .all()
    )


def get_all_offer_template_by_redactor_id(redactor_id: int) -> list[educational_models.CollectiveOfferTemplate]:
    return (
        educational_models.CollectiveOfferTemplate.query.join(
            educational_models.EducationalRedactor,
            educational_models.CollectiveOfferTemplate.educationalRedactorsFavorite,
        )
        .options(
            sa_orm.joinedload(educational_models.CollectiveOfferTemplate.venue).joinedload(
                offerers_models.Venue.managingOfferer
            ),
            sa_orm.joinedload(educational_models.CollectiveOfferTemplate.domains),
            sa_orm.joinedload(educational_models.CollectiveOfferTemplate.venue).selectinload(
                offerers_models.Venue.googlePlacesInfo
            ),
        )
        .filter(educational_models.EducationalRedactor.id == redactor_id)
        .all()
    )


def get_user_favorite_offers_from_uai(redactor_id: int | None, uai: str) -> set[int]:
    if not redactor_id:
        return set()
    query = (
        educational_models.CollectiveOffer.query.join(
            educational_models.EducationalInstitution, educational_models.CollectiveOffer.institution
        )
        .filter(educational_models.EducationalInstitution.institutionId == uai)
        .join(educational_models.EducationalRedactor, educational_models.CollectiveOffer.educationalRedactorsFavorite)
        .filter(educational_models.EducationalRedactor.id == redactor_id)
    )
    return {offer.id for offer in query}


def get_venue_base_query() -> BaseQuery:
    return offerers_models.Venue.query.filter(
        offerers_models.Venue.adageId.is_not(None),
    ).options(sa.orm.joinedload(offerers_models.Venue.adage_addresses))


def fetch_venue_for_new_offer(venue_id: int, requested_provider_id: int) -> offerers_models.Venue:
    query = (
        offerers_models.Venue.query.filter(offerers_models.Venue.id == venue_id)
        .join(providers_models.VenueProvider, offerers_models.Venue.venueProviders)
        .filter(providers_models.VenueProvider.providerId == requested_provider_id)
        .options(
            sa_orm.joinedload(offerers_models.Venue.managingOfferer)
            .joinedload(offerers_models.Offerer.confidenceRule)
            .load_only(offerers_models.OffererConfidenceRule.confidenceLevel),
            sa.orm.joinedload(offerers_models.Venue.confidenceRule).load_only(
                offerers_models.OffererConfidenceRule.confidenceLevel
            ),
        )
    )

    venue = query.one_or_none()
    if not venue:
        raise offerers_exceptions.VenueNotFoundException()
    return typing.cast(offerers_models.Venue, venue)

import typing
from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta
from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy import orm as sa_orm
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql.expression import extract

from pcapi.core.educational import exceptions
from pcapi.core.educational import models
from pcapi.core.educational import schemas
from pcapi.core.finance import models as finance_models
from pcapi.core.geography import models as geography_models
from pcapi.core.offerers import exceptions as offerers_exceptions
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers.models import Venue
from pcapi.core.providers import models as providers_models
from pcapi.core.users.models import User
from pcapi.models import db
from pcapi.models import offer_mixin
from pcapi.utils import repository
from pcapi.utils.clean_accents import clean_accents


COLLECTIVE_BOOKING_STATUS_LABELS = {
    models.CollectiveBookingStatus.PENDING: "préréservé",
    models.CollectiveBookingStatus.CONFIRMED: "réservé",
    models.CollectiveBookingStatus.CANCELLED: "annulé",
    models.CollectiveBookingStatus.USED: "validé",
    models.CollectiveBookingStatus.REIMBURSED: "remboursé",
    "confirmed": "confirmé",
}


BOOKING_DATE_STATUS_MAPPING: dict[models.CollectiveBookingStatusFilter, sa_orm.InstrumentedAttribute] = {
    models.CollectiveBookingStatusFilter.BOOKED: models.CollectiveBooking.dateCreated,
    models.CollectiveBookingStatusFilter.VALIDATED: models.CollectiveBooking.dateUsed,
    models.CollectiveBookingStatusFilter.REIMBURSED: models.CollectiveBooking.reimbursementDate,
}


def find_bookings_starting_in_x_days(number_of_days: int) -> list[models.CollectiveBooking]:
    target_day = datetime.utcnow() + timedelta(days=number_of_days)
    start = datetime.combine(target_day, time.min)
    end = datetime.combine(target_day, time.max)
    return find_bookings_in_interval(start, end, models.CollectiveStock.startDatetime)


def find_bookings_ending_in_x_days(number_of_days: int) -> list[models.CollectiveBooking]:
    target_day = datetime.utcnow() + timedelta(days=number_of_days)
    start = datetime.combine(target_day, time.min)
    end = datetime.combine(target_day, time.max)
    return find_bookings_in_interval(start, end, models.CollectiveStock.endDatetime)


def find_bookings_in_interval(start: datetime, end: datetime, dateColumn: sa.Column) -> list[models.CollectiveBooking]:
    query = db.session.query(models.CollectiveBooking).join(
        models.CollectiveStock, models.CollectiveBooking.collectiveStock
    )
    query = query.filter(
        dateColumn.between(start, end),
        models.CollectiveBooking.status != models.CollectiveBookingStatus.CANCELLED,
    )
    query = query.options(sa_orm.joinedload(models.CollectiveBooking.collectiveStock, innerjoin=True))
    query = query.options(
        sa_orm.joinedload(models.CollectiveBooking.collectiveStock, innerjoin=True).joinedload(
            models.CollectiveStock.collectiveOffer, innerjoin=True
        )
    )
    query = query.options(
        sa_orm.joinedload(models.CollectiveBooking.collectiveStock, innerjoin=True)
        .joinedload(models.CollectiveStock.collectiveOffer, innerjoin=True)
        .joinedload(models.CollectiveOffer.venue, innerjoin=True)
        .joinedload(offerers_models.Venue.managingOfferer, innerjoin=True)
        .load_only(offerers_models.Offerer.siren, offerers_models.Offerer.postalCode)
    )
    query = query.options(sa_orm.joinedload(models.CollectiveBooking.educationalRedactor, innerjoin=True))
    query = query.options(sa_orm.joinedload(models.CollectiveBooking.educationalInstitution, innerjoin=True))
    return query.distinct().all()


def get_and_lock_educational_deposit(
    educational_institution_id: int, educational_year_id: str
) -> models.EducationalDeposit:
    """Returns educational_deposit with a FOR UPDATE lock
    Raises exceptions.EducationalDepositNotFound if no stock is found.
    WARNING: MAKE SURE YOU FREE THE LOCK (with COMMIT or ROLLBACK) and don't hold it longer than
    strictly necessary.
    """
    educational_deposit = (
        db.session.query(models.EducationalDeposit)
        .filter_by(
            educationalInstitutionId=educational_institution_id,
            educationalYearId=educational_year_id,
        )
        .populate_existing()
        .with_for_update()
        .one_or_none()
    )
    if not educational_deposit:
        raise exceptions.EducationalDepositNotFound()
    return educational_deposit


def get_ministry_budget_for_year(
    ministry: models.Ministry | None,
    educational_year_id: str,
) -> Decimal:
    query = db.session.query(sa.func.sum(models.EducationalDeposit.amount).label("amount"))
    query = query.filter(
        models.EducationalDeposit.educationalYearId == educational_year_id,
        models.EducationalDeposit.ministry == ministry,
    )
    return query.first().amount or Decimal(0)


def get_confirmed_collective_bookings_amount_for_ministry(
    ministry: models.Ministry | None,
    educational_year_id: str,
) -> Decimal:
    query = db.session.query(sa.func.sum(models.CollectiveStock.price).label("amount"))
    query = query.join(models.CollectiveBooking, models.CollectiveStock.collectiveBookings)
    query = query.join(models.EducationalInstitution, models.CollectiveBooking.educationalInstitution)
    query = query.join(models.EducationalDeposit, models.EducationalInstitution.deposits)
    query = query.filter(
        models.CollectiveBooking.educationalYearId == educational_year_id,
        models.CollectiveBooking.status.not_in(
            [models.CollectiveBookingStatus.CANCELLED, models.CollectiveBookingStatus.PENDING]
        ),
        models.EducationalDeposit.ministry == ministry,
    )
    return query.first().amount or Decimal(0)


def get_confirmed_collective_bookings_amount(
    educational_institution_id: int,
    educational_year_id: str,
    min_end_month: int | None = None,
    max_end_month: int | None = None,
) -> Decimal:
    query = db.session.query(sa.func.sum(models.CollectiveStock.price).label("amount"))
    query = query.join(models.CollectiveBooking, models.CollectiveStock.collectiveBookings)
    query = query.filter(
        models.CollectiveBooking.educationalInstitutionId == educational_institution_id,
        models.CollectiveBooking.educationalYearId == educational_year_id,
        models.CollectiveBooking.status.not_in(
            [models.CollectiveBookingStatus.CANCELLED, models.CollectiveBookingStatus.PENDING]
        ),
    )

    if min_end_month is not None:
        query = query.filter(min_end_month <= sa.extract("month", models.CollectiveStock.endDatetime))

    if max_end_month is not None:
        query = query.filter(sa.extract("month", models.CollectiveStock.endDatetime) <= max_end_month)

    return query.first().amount or Decimal(0)


def find_collective_booking_by_id(booking_id: int) -> models.CollectiveBooking | None:
    query = _get_bookings_for_adage_base_query()
    query = query.filter(models.CollectiveBooking.id == booking_id)
    return query.one_or_none()


def find_educational_year_by_date(date_searched: datetime) -> models.EducationalYear | None:
    return (
        db.session.query(models.EducationalYear)
        .filter(
            date_searched >= models.EducationalYear.beginningDate,
            date_searched <= models.EducationalYear.expirationDate,
        )
        .one_or_none()
    )


def find_educational_institution_by_uai_code(uai_code: str | None) -> models.EducationalInstitution | None:
    return db.session.query(models.EducationalInstitution).filter_by(institutionId=uai_code).one_or_none()


def find_educational_deposit_by_institution_id_and_year(
    educational_institution_id: int,
    educational_year_id: str,
) -> models.EducationalDeposit | None:
    return (
        db.session.query(models.EducationalDeposit)
        .filter(
            models.EducationalDeposit.educationalInstitutionId == educational_institution_id,
            models.EducationalDeposit.educationalYearId == educational_year_id,
        )
        .one_or_none()
    )


def get_educational_deposits_by_year(year_id: str) -> list[models.EducationalDeposit]:
    return (
        db.session.query(models.EducationalDeposit)
        .join(models.EducationalDeposit.educationalInstitution)
        .filter(models.EducationalDeposit.educationalYearId == year_id)
        .options(sa_orm.joinedload(models.EducationalDeposit.educationalInstitution))
        .all()
    )


def get_educational_year_beginning_at_given_year(year: int) -> models.EducationalYear:
    educational_year = (
        db.session.query(models.EducationalYear)
        .filter(extract("year", models.EducationalYear.beginningDate) == year)
        .one_or_none()
    )
    if educational_year is None:
        raise exceptions.EducationalYearNotFound()
    return educational_year


def _get_bookings_for_adage_base_query() -> "sa_orm.Query[models.CollectiveBooking]":
    query = db.session.query(models.CollectiveBooking)
    query = query.options(
        sa_orm.joinedload(models.CollectiveBooking.collectiveStock, innerjoin=True)
        .load_only(
            models.CollectiveStock.startDatetime,
            models.CollectiveStock.endDatetime,
            models.CollectiveStock.numberOfTickets,
            models.CollectiveStock.priceDetail,
            models.CollectiveStock.price,
            models.CollectiveStock.collectiveOfferId,
        )
        .joinedload(models.CollectiveStock.collectiveOffer, innerjoin=True)
        .load_only(
            models.CollectiveOffer.audioDisabilityCompliant,
            models.CollectiveOffer.mentalDisabilityCompliant,
            models.CollectiveOffer.motorDisabilityCompliant,
            models.CollectiveOffer.visualDisabilityCompliant,
            models.CollectiveOffer.offerVenue,
            models.CollectiveOffer.contactEmail,
            models.CollectiveOffer.contactPhone,
            models.CollectiveOffer.description,
            models.CollectiveOffer.durationMinutes,
            models.CollectiveOffer.name,
            models.CollectiveOffer.students,
            models.CollectiveOffer.id,
            models.CollectiveOffer.interventionArea,
            models.CollectiveOffer.imageCredit,
            models.CollectiveOffer.imageId,
            models.CollectiveOffer.bookingEmails,
            models.CollectiveOffer.formats,
            models.CollectiveOffer.locationType,
            models.CollectiveOffer.locationComment,
            models.CollectiveOffer.offererAddressId,
        )
        .options(
            sa_orm.joinedload(models.CollectiveOffer.domains).load_only(models.EducationalDomain.id),
            sa_orm.joinedload(models.CollectiveOffer.offererAddress).joinedload(offerers_models.OffererAddress.address),
            sa_orm.joinedload(models.CollectiveOffer.venue, innerjoin=True).options(
                sa_orm.load_only(
                    # TODO(OA) - remove the address fields when the virtual venues are migrated
                    offerers_models.Venue.city,
                    offerers_models.Venue.postalCode,
                    offerers_models.Venue.latitude,
                    offerers_models.Venue.longitude,
                    offerers_models.Venue.timezone,
                    offerers_models.Venue.departementCode,
                    offerers_models.Venue.publicName,
                    offerers_models.Venue.name,
                    offerers_models.Venue.street,
                    offerers_models.Venue.offererAddressId,
                ),
                sa_orm.joinedload(offerers_models.Venue.managingOfferer, innerjoin=True).load_only(
                    offerers_models.Offerer.name, offerers_models.Offerer.siren, offerers_models.Offerer.postalCode
                ),
                sa_orm.joinedload(offerers_models.Venue.offererAddress)
                .joinedload(offerers_models.OffererAddress.address)
                .load_only(geography_models.Address.timezone),
            ),
        )
    )

    query = query.options(sa_orm.joinedload(models.CollectiveBooking.educationalInstitution))
    query = query.options(sa_orm.joinedload(models.CollectiveBooking.educationalRedactor))

    return query


def find_collective_bookings_for_adage(
    uai_code: str,
    year_id: str,
    redactor_email: str | None = None,
) -> list[models.CollectiveBooking]:
    query = _get_bookings_for_adage_base_query()

    query = query.join(models.EducationalInstitution)
    query = query.join(models.EducationalRedactor)
    query = query.join(models.EducationalYear)

    query = query.filter(models.EducationalInstitution.institutionId == uai_code)
    query = query.filter(models.EducationalYear.adageId == year_id)

    if redactor_email is not None:
        query = query.filter(models.EducationalRedactor.email == redactor_email)

    return query.all()


def find_redactor_by_email(redactor_email: str) -> models.EducationalRedactor | None:
    return (
        db.session.query(models.EducationalRedactor)
        .filter(models.EducationalRedactor.email == redactor_email)
        .one_or_none()
    )


def find_or_create_redactor(information: schemas.RedactorInformation) -> models.EducationalRedactor:
    redactor = find_redactor_by_email(information.email)
    if redactor:
        return redactor

    redactor = models.EducationalRedactor(
        email=information.email,
        firstName=information.firstname,
        lastName=information.lastname,
        civility=information.civility,
    )

    repository.save(redactor)
    return redactor


def find_active_collective_booking_by_offer_id(
    collective_offer_id: int,
) -> models.CollectiveBooking | None:
    return (
        db.session.query(models.CollectiveBooking)
        .filter(
            models.CollectiveBooking.status.in_(
                [
                    models.CollectiveBookingStatus.CONFIRMED,
                    models.CollectiveBookingStatus.PENDING,
                ]
            )
        )
        .join(models.CollectiveStock)
        .filter(
            models.CollectiveStock.collectiveOfferId == collective_offer_id,
        )
        .options(
            sa_orm.contains_eager(models.CollectiveBooking.collectiveStock)
            .joinedload(models.CollectiveStock.collectiveOffer, innerjoin=True)
            .options(
                sa_orm.joinedload(models.CollectiveOffer.venue, innerjoin=True),
                sa_orm.joinedload(models.CollectiveOffer.offererAddress).joinedload(
                    offerers_models.OffererAddress.address
                ),
            )
        )
        .options(sa_orm.joinedload(models.CollectiveBooking.educationalInstitution, innerjoin=True))
        .options(sa_orm.joinedload(models.CollectiveBooking.educationalRedactor, innerjoin=True))
        .one_or_none()
    )


def get_paginated_collective_bookings_for_educational_year(
    educational_year_id: str,
    page: int | None,
    per_page: int | None,
) -> list[models.CollectiveBooking]:
    page = 1 if page is None else page
    per_page = 1000 if per_page is None else per_page

    query = db.session.query(models.CollectiveBooking).filter(
        models.CollectiveBooking.educationalYearId == educational_year_id
    )
    query = query.options(
        sa_orm.load_only(
            models.CollectiveBooking.id,
            models.CollectiveBooking.collectiveStockId,
            models.CollectiveBooking.status,
            models.CollectiveBooking.confirmationLimitDate,
            models.CollectiveBooking.cancellationReason,
            models.CollectiveBooking.dateCreated,
            models.CollectiveBooking.dateUsed,
            models.CollectiveBooking.offererId,
            models.CollectiveBooking.cancellationDate,
            models.CollectiveBooking.cancellationLimitDate,
        )
    )
    query = query.options(
        # fetch a collective booking's stock...
        sa_orm.joinedload(models.CollectiveBooking.collectiveStock, innerjoin=True)
        .load_only(
            models.CollectiveStock.startDatetime,
            models.CollectiveStock.endDatetime,
            models.CollectiveStock.collectiveOfferId,
            models.CollectiveStock.price,
        )
        # ...to fetch its offer...
        .joinedload(models.CollectiveStock.collectiveOffer, innerjoin=True)
        .load_only(
            models.CollectiveOffer.name,
            models.CollectiveOffer.venueId,
            models.CollectiveOffer.formats,
        )
        .options(
            # ... to fetch its venue...
            sa_orm.joinedload(models.CollectiveOffer.venue, innerjoin=True).options(
                sa_orm.load_only(
                    offerers_models.Venue.id,
                    offerers_models.Venue.name,
                    offerers_models.Venue.timezone,  # TODO(OA) - remove this when the virtual venues are migrated
                ),
                # ... to fetch its offerer...
                sa_orm.joinedload(offerers_models.Venue.managingOfferer).load_only(offerers_models.Offerer.name),
                # ... and its address
                sa_orm.joinedload(offerers_models.Venue.offererAddress)
                .joinedload(offerers_models.OffererAddress.address)
                .load_only(geography_models.Address.timezone),
            ),
            # and the offer's domains
            sa_orm.joinedload(models.CollectiveOffer.domains).load_only(models.EducationalDomain.id),
        )
    )
    query = query.options(
        sa_orm.joinedload(models.CollectiveBooking.educationalInstitution, innerjoin=True).load_only(
            models.EducationalInstitution.institutionId
        )
    )
    query = query.options(
        sa_orm.joinedload(models.CollectiveBooking.educationalRedactor, innerjoin=True).load_only(
            models.EducationalRedactor.email
        )
    )
    query = query.order_by(models.CollectiveBooking.id)
    query = query.offset((page - 1) * per_page)
    query = query.limit(per_page)
    return query.all()


def get_expired_or_archived_collective_offers_template() -> sa_orm.Query:
    """Return a query of collective offer templates that are either expired (end date has passed)
    or archived.
    """
    return (
        db.session.query(models.CollectiveOfferTemplate.id)
        .order_by(models.CollectiveOfferTemplate.id)
        .filter(
            sa.or_(
                models.CollectiveOfferTemplate.hasEndDatePassed.is_(True),  # type: ignore[attr-defined]
                models.CollectiveOfferTemplate.isArchived.is_(True),  # type: ignore[attr-defined]
            )
        )
    )


def find_expiring_collective_bookings_query() -> sa_orm.Query:
    today_at_midnight = datetime.combine(date.today(), time(0, 0))

    return db.session.query(models.CollectiveBooking).filter(
        models.CollectiveBooking.status == models.CollectiveBookingStatus.PENDING,
        models.CollectiveBooking.confirmationLimitDate <= today_at_midnight,
    )


def find_expired_collective_bookings() -> list[models.CollectiveBooking]:
    expired_on = date.today()
    return (
        db.session.query(models.CollectiveBooking)
        .filter(models.CollectiveBooking.status == models.CollectiveBookingStatus.CANCELLED)
        .filter(sa.cast(models.CollectiveBooking.cancellationDate, sa.Date) == expired_on)
        .filter(
            models.CollectiveBooking.cancellationReason == models.CollectiveBookingCancellationReasons.EXPIRED,
        )
        .options(
            sa_orm.joinedload(models.CollectiveBooking.collectiveStock, innerjoin=True)
            .load_only(
                models.CollectiveStock.startDatetime,
                models.CollectiveStock.endDatetime,
                models.CollectiveStock.collectiveOfferId,
            )
            .joinedload(models.CollectiveStock.collectiveOffer, innerjoin=True)
            .load_only(models.CollectiveOffer.name, models.CollectiveOffer.venueId)
            .joinedload(models.CollectiveOffer.venue, innerjoin=True)
            .load_only(offerers_models.Venue.name)
        )
        .options(
            sa_orm.joinedload(models.CollectiveBooking.educationalRedactor, innerjoin=True).load_only(
                models.EducationalRedactor.email,
                models.EducationalRedactor.firstName,
                models.EducationalRedactor.lastName,
            )
        )
        .options(sa_orm.joinedload(models.CollectiveBooking.educationalInstitution, innerjoin=True))
        .all()
    )


def get_and_lock_collective_stock(stock_id: int) -> models.CollectiveStock:
    """Returns `stock_id` stock with a FOR UPDATE lock
    Raises exceptions.StockDoesNotExist if no stock is found.
    WARNING: MAKE SURE YOU FREE THE LOCK (with COMMIT or ROLLBACK) and don't hold it longer than
    strictly necessary.
    """
    # Use `with_for_update()` to make sure we lock the stock while performing
    # the booking checks and update the `dnBookedQuantity`
    # This is required to prevent bugs due to concurrent access
    # Also call `populate_existing()` to make sure we don't use something
    # older from the SQLAlchemy's session.
    stock = (
        db.session.query(models.CollectiveStock)
        .filter_by(id=stock_id)
        .populate_existing()
        .with_for_update()
        .one_or_none()
    )
    if not stock:
        raise exceptions.CollectiveStockDoesNotExist()
    return stock


def get_collective_stock(collective_stock_id: int) -> models.CollectiveStock | None:
    return (
        db.session.query(models.CollectiveStock)
        .filter(models.CollectiveStock.id == collective_stock_id)
        .options(
            sa_orm.joinedload(models.CollectiveStock.collectiveOffer).options(
                # needed to avoid a query when we call stock.collectiveOffer.collectiveStock
                sa_orm.contains_eager(models.CollectiveOffer.collectiveStock),
                sa_orm.joinedload(models.CollectiveOffer.venue),
            ),
            sa_orm.joinedload(models.CollectiveStock.collectiveBookings),
        )
        .one_or_none()
    )


def get_collective_offers_by_filters(filters: schemas.CollectiveOffersFilter) -> "sa_orm.Query[models.CollectiveOffer]":
    query = db.session.query(models.CollectiveOffer).join(models.CollectiveOffer.venue)

    if not filters.user_is_admin:
        query = (
            query.join(offerers_models.Venue.managingOfferer)
            .join(offerers_models.Offerer.UserOfferers)
            .filter(
                offerers_models.UserOfferer.userId == filters.user_id,
                offerers_models.UserOfferer.isValidated,
            )
        )

    if filters.offerer_id is not None:
        query = query.filter(offerers_models.Venue.managingOffererId == filters.offerer_id)

    if filters.venue_id is not None:
        query = query.filter(models.CollectiveOffer.venueId == filters.venue_id)

    if filters.provider_id is not None:
        query = query.filter(models.CollectiveOffer.providerId == filters.provider_id)

    if filters.name_keywords is not None:
        search = filters.name_keywords
        if len(filters.name_keywords) > 3:
            search = "%{}%".format(filters.name_keywords)

        query = query.filter(models.CollectiveOffer.name.ilike(search))

    if filters.statuses:
        query = filter_collective_offers_by_statuses(query, filters.statuses)

    if filters.period_beginning_date is not None or filters.period_ending_date is not None:
        subquery = (
            db.session.query(models.CollectiveStock)
            .with_entities(models.CollectiveStock.collectiveOfferId)
            .distinct(models.CollectiveStock.collectiveOfferId)
            .join(models.CollectiveOffer)
            .join(offerers_models.Venue)
        )
        if filters.period_beginning_date is not None:
            subquery = subquery.filter(
                sa.func.timezone(
                    # TODO(OA) - use Venue.offererAddress.address.timezone when the virtual venues are migrated
                    offerers_models.Venue.timezone,
                    sa.func.timezone("UTC", models.CollectiveStock.startDatetime),
                )
                >= filters.period_beginning_date
            )
        if filters.period_ending_date is not None:
            subquery = subquery.filter(
                sa.func.timezone(
                    # TODO(OA) - use Venue.offererAddress.address.timezone when the virtual venues are migrated
                    offerers_models.Venue.timezone,
                    sa.func.timezone("UTC", models.CollectiveStock.startDatetime),
                )
                <= datetime.combine(filters.period_ending_date, time.max),
            )
        if filters.venue_id is not None:
            subquery = subquery.filter(models.CollectiveOffer.venueId == filters.venue_id)
        elif filters.offerer_id is not None:
            subquery = subquery.filter(offerers_models.Venue.managingOffererId == filters.offerer_id)
        elif not filters.user_is_admin:
            subquery = (
                subquery.join(offerers_models.Offerer)
                .join(offerers_models.UserOfferer)
                .filter(
                    offerers_models.UserOfferer.userId == filters.user_id,
                    offerers_models.UserOfferer.isValidated,
                )
            )
        q2 = subquery.subquery()
        query = query.join(q2, q2.c.collectiveOfferId == models.CollectiveOffer.id)

    if filters.formats:
        query = query.filter(
            models.CollectiveOffer.formats.overlap(postgresql.array((format.name for format in filters.formats)))
        )

    if filters.location_type is not None:
        query = query.filter(models.CollectiveOffer.locationType == filters.location_type)

    if filters.offerer_address_id is not None:
        query = query.filter(models.CollectiveOffer.offererAddressId == filters.offerer_address_id)

    return query


def get_collective_offers_template_by_filters(filters: schemas.CollectiveOffersFilter) -> sa_orm.Query:
    query = db.session.query(models.CollectiveOfferTemplate).join(models.CollectiveOfferTemplate.venue)

    if filters.period_beginning_date is not None or filters.period_ending_date is not None:
        query = query.filter(sa.false())

    if not filters.user_is_admin:
        query = (
            query.join(offerers_models.Venue.managingOfferer)
            .join(offerers_models.Offerer.UserOfferers)
            .filter(
                offerers_models.UserOfferer.userId == filters.user_id,
                offerers_models.UserOfferer.isValidated,
            )
        )

    if filters.offerer_id is not None:
        query = query.filter(offerers_models.Venue.managingOffererId == filters.offerer_id)

    if filters.venue_id is not None:
        query = query.filter(models.CollectiveOfferTemplate.venueId == filters.venue_id)

    if filters.name_keywords is not None:
        search = filters.name_keywords
        if len(filters.name_keywords) > 3:
            search = "%{}%".format(filters.name_keywords)

        query = query.filter(models.CollectiveOfferTemplate.name.ilike(search))

    if filters.statuses:
        template_statuses = set(filters.statuses) & set(models.COLLECTIVE_OFFER_TEMPLATE_STATUSES)
        status_values = [status.value for status in template_statuses]
        query = query.filter(models.CollectiveOfferTemplate.displayedStatus.in_(status_values))  # type: ignore[attr-defined]

    if filters.formats:
        query = query.filter(
            models.CollectiveOfferTemplate.formats.overlap(
                postgresql.array((format.name for format in filters.formats))
            )
        )

    if filters.location_type is not None:
        query = query.filter(models.CollectiveOfferTemplate.locationType == filters.location_type)

    if filters.offerer_address_id is not None:
        query = query.filter(models.CollectiveOfferTemplate.offererAddressId == filters.offerer_address_id)

    return query


def filter_collective_offers_by_statuses(
    query: sa_orm.Query, statuses: list[models.CollectiveOfferDisplayedStatus] | None
) -> sa_orm.Query:
    """
    Filter a SQLAlchemy query for CollectiveOffers based on a list of statuses.

    This function modifies the input query to filter CollectiveOffers based on their CollectiveOfferDisplayedStatus.

    Args:
      query (sa_orm.Query): The initial query to be filtered.
      statuses (list[CollectiveOfferDisplayedStatus]): A list of status strings to filter by.

    Returns:
      sa_orm.Query: The modified query with applied filters.
    """
    on_collective_offer_filters: list = []
    on_booking_status_filter: list = []

    if not statuses:
        # if statuses is empty we return all offers
        return query

    offer_id_with_booking_status_subquery, query_with_booking = add_last_booking_status_to_collective_offer_query(query)

    if models.CollectiveOfferDisplayedStatus.ARCHIVED in statuses:
        on_collective_offer_filters.append(models.CollectiveOffer.isArchived == True)

    if models.CollectiveOfferDisplayedStatus.DRAFT in statuses:
        on_collective_offer_filters.append(
            sa.and_(
                models.CollectiveOffer.validation == offer_mixin.OfferValidationStatus.DRAFT,
                models.CollectiveOffer.isArchived == False,
            )
        )

    if models.CollectiveOfferDisplayedStatus.UNDER_REVIEW in statuses:
        on_collective_offer_filters.append(
            sa.and_(
                models.CollectiveOffer.validation == offer_mixin.OfferValidationStatus.PENDING,
                models.CollectiveOffer.isArchived == False,
            )
        )

    if models.CollectiveOfferDisplayedStatus.REJECTED in statuses:
        on_collective_offer_filters.append(
            sa.and_(
                models.CollectiveOffer.validation == offer_mixin.OfferValidationStatus.REJECTED,
                models.CollectiveOffer.isArchived == False,
            )
        )

    if models.CollectiveOfferDisplayedStatus.HIDDEN in statuses:
        # if the statuses filter contains HIDDEN only, we need to return no collective_offer
        # otherwise we return offers depending on the other statuses in the filter
        on_collective_offer_filters.append(sa.false())

    if models.CollectiveOfferDisplayedStatus.PUBLISHED in statuses:
        on_booking_status_filter.append(
            sa.and_(
                models.CollectiveOffer.validation == offer_mixin.OfferValidationStatus.APPROVED,
                models.CollectiveOffer.isActive == True,
                offer_id_with_booking_status_subquery.c.status == None,
                models.CollectiveOffer.hasBookingLimitDatetimesPassed == False,
            )
        )

    if models.CollectiveOfferDisplayedStatus.PREBOOKED in statuses:
        on_booking_status_filter.append(
            sa.and_(
                models.CollectiveOffer.validation == offer_mixin.OfferValidationStatus.APPROVED,
                models.CollectiveOffer.isActive == True,
                offer_id_with_booking_status_subquery.c.status == models.CollectiveBookingStatus.PENDING,
                models.CollectiveOffer.hasBookingLimitDatetimesPassed == False,
            )
        )

    if models.CollectiveOfferDisplayedStatus.BOOKED in statuses:
        on_booking_status_filter.append(
            sa.and_(
                models.CollectiveOffer.validation == offer_mixin.OfferValidationStatus.APPROVED,
                models.CollectiveOffer.isActive == True,
                offer_id_with_booking_status_subquery.c.status == models.CollectiveBookingStatus.CONFIRMED,
                models.CollectiveOffer.hasEndDatetimePassed == False,
            )
        )

    if models.CollectiveOfferDisplayedStatus.ENDED in statuses:
        on_booking_status_filter.append(
            sa.and_(
                models.CollectiveOffer.validation == offer_mixin.OfferValidationStatus.APPROVED,
                models.CollectiveOffer.isActive == True,
                sa.or_(
                    offer_id_with_booking_status_subquery.c.status == models.CollectiveBookingStatus.USED,
                    offer_id_with_booking_status_subquery.c.status == models.CollectiveBookingStatus.CONFIRMED,
                ),
                models.CollectiveOffer.hasEndDatetimePassed == True,
            )
        )

    if models.CollectiveOfferDisplayedStatus.REIMBURSED in statuses:
        on_booking_status_filter.append(
            sa.and_(
                models.CollectiveOffer.validation == offer_mixin.OfferValidationStatus.APPROVED,
                models.CollectiveOffer.isActive == True,
                offer_id_with_booking_status_subquery.c.status == models.CollectiveBookingStatus.REIMBURSED,
            )
        )

    if models.CollectiveOfferDisplayedStatus.EXPIRED in statuses:
        # expired with a pending booking or no booking
        on_booking_status_filter.append(
            sa.and_(
                models.CollectiveOffer.validation == offer_mixin.OfferValidationStatus.APPROVED,
                models.CollectiveOffer.isActive == True,
                models.CollectiveOffer.hasBookingLimitDatetimesPassed == True,
                models.CollectiveOffer.hasStartDatetimePassed == False,
                sa.or_(
                    offer_id_with_booking_status_subquery.c.status == models.CollectiveBookingStatus.PENDING,
                    offer_id_with_booking_status_subquery.c.status == None,
                ),
            )
        )
        # expired with a booking cancelled with reason EXPIRED
        on_booking_status_filter.append(
            sa.and_(
                models.CollectiveOffer.validation == offer_mixin.OfferValidationStatus.APPROVED,
                models.CollectiveOffer.isActive == True,
                models.CollectiveOffer.hasBookingLimitDatetimesPassed == True,
                models.CollectiveOffer.hasStartDatetimePassed == False,
                offer_id_with_booking_status_subquery.c.status == models.CollectiveBookingStatus.CANCELLED,
                offer_id_with_booking_status_subquery.c.cancellationReason
                == models.CollectiveBookingCancellationReasons.EXPIRED,
            )
        )

    if models.CollectiveOfferDisplayedStatus.CANCELLED in statuses:
        # Cancelled due to expired booking
        on_booking_status_filter.append(
            sa.and_(
                models.CollectiveOffer.validation == offer_mixin.OfferValidationStatus.APPROVED,
                models.CollectiveOffer.isActive == True,
                offer_id_with_booking_status_subquery.c.status == models.CollectiveBookingStatus.CANCELLED,
                offer_id_with_booking_status_subquery.c.cancellationReason
                == models.CollectiveBookingCancellationReasons.EXPIRED,
                models.CollectiveOffer.hasStartDatetimePassed == True,
            )
        )

        # Cancelled by admin / CA or on ADAGE
        on_booking_status_filter.append(
            sa.and_(
                models.CollectiveOffer.validation == offer_mixin.OfferValidationStatus.APPROVED,
                models.CollectiveOffer.isActive == True,
                offer_id_with_booking_status_subquery.c.status == models.CollectiveBookingStatus.CANCELLED,
                offer_id_with_booking_status_subquery.c.cancellationReason
                != models.CollectiveBookingCancellationReasons.EXPIRED,
            ),
        )

        # Cancelled due to no booking when the event has started
        on_booking_status_filter.append(
            sa.and_(
                models.CollectiveOffer.validation == offer_mixin.OfferValidationStatus.APPROVED,
                models.CollectiveOffer.isActive == True,
                offer_id_with_booking_status_subquery.c.status == None,
                models.CollectiveOffer.hasStartDatetimePassed == True,
            ),
        )

    # Add filters on `CollectiveBooking.Status`
    if on_booking_status_filter:
        substmt = query_with_booking.filter(sa.or_(*on_booking_status_filter)).subquery()
        on_collective_offer_filters.append(models.CollectiveOffer.id.in_(sa.select(substmt.c.id)))

    # Add filters on `CollectiveOffer`
    if on_collective_offer_filters:
        query = query.filter(sa.or_(*on_collective_offer_filters))

    return query


def add_last_booking_status_to_collective_offer_query(query: sa_orm.Query) -> typing.Tuple[typing.Any, sa_orm.Query]:
    last_booking_query = (
        db.session.query(models.CollectiveBooking)
        .with_entities(
            models.CollectiveBooking.collectiveStockId,
            sa.func.max(models.CollectiveBooking.dateCreated).label("maxdate"),
        )
        .group_by(models.CollectiveBooking.collectiveStockId)
        .subquery()
    )

    collective_stock_with_last_booking_status_query = (
        db.session.query(models.CollectiveStock)
        .with_entities(
            models.CollectiveStock.collectiveOfferId,
            models.CollectiveStock.bookingLimitDatetime,
            models.CollectiveBooking.status,
            models.CollectiveBooking.cancellationReason,
        )
        .outerjoin(
            models.CollectiveBooking,
            models.CollectiveStock.collectiveBookings,
        )
        .join(
            last_booking_query,
            sa.and_(
                models.CollectiveBooking.collectiveStockId == last_booking_query.c.collectiveStockId,
                models.CollectiveBooking.dateCreated == last_booking_query.c.maxdate,
            ),
        )
    )

    subquery = collective_stock_with_last_booking_status_query.subquery()

    query_with_booking = query.outerjoin(
        subquery,
        subquery.c.collectiveOfferId == models.CollectiveOffer.id,
    )

    return subquery, query_with_booking


def get_collective_offers_for_filters(
    filters: schemas.CollectiveOffersFilter, offers_limit: int
) -> list[models.CollectiveOffer]:
    query = get_collective_offers_by_filters(filters=filters)

    query = query.order_by(models.CollectiveOffer.dateCreated.desc())
    offers = (
        query.options(
            sa_orm.joinedload(models.CollectiveOffer.venue).options(
                sa_orm.joinedload(offerers_models.Venue.managingOfferer),
                sa_orm.joinedload(offerers_models.Venue.offererAddress).joinedload(
                    offerers_models.OffererAddress.address
                ),
            ),
            *_get_collective_offer_address_joinedload_with_expression(),
        )
        .options(
            sa_orm.joinedload(models.CollectiveOffer.collectiveStock).joinedload(
                models.CollectiveStock.collectiveBookings
            )
        )
        .options(sa_orm.joinedload(models.CollectiveOffer.institution))
        .limit(offers_limit)
        .populate_existing()
        .all()
    )
    return offers


def get_collective_offers_template_for_filters(
    filters: schemas.CollectiveOffersFilter, offers_limit: int
) -> list[models.CollectiveOfferTemplate]:
    query = get_collective_offers_template_by_filters(filters=filters)

    query = query.order_by(models.CollectiveOfferTemplate.dateCreated.desc())

    offers = (
        query.options(
            sa_orm.joinedload(models.CollectiveOfferTemplate.venue).options(
                sa_orm.joinedload(offerers_models.Venue.managingOfferer),
                sa_orm.joinedload(offerers_models.Venue.offererAddress).joinedload(
                    offerers_models.OffererAddress.address
                ),
            ),
            *_get_collective_offer_template_address_joinedload_with_expression(),
        )
        .limit(offers_limit)
        .populate_existing()
        .all()
    )
    return offers


def _get_filtered_collective_bookings_query(
    pro_user: User,
    period: tuple[date, date] | None = None,
    status_filter: models.CollectiveBookingStatusFilter | None = None,
    event_date: date | None = None,
    venue_id: int | None = None,
    *,
    extra_joins: tuple[tuple[typing.Any, ...], ...] = (),
) -> sa_orm.Query:
    collective_bookings_query = (
        db.session.query(models.CollectiveBooking)
        .join(models.CollectiveBooking.offerer)
        .join(offerers_models.Offerer.UserOfferers)
        .join(models.CollectiveBooking.collectiveStock)
        .join(models.CollectiveBooking.venue, isouter=True)
    )
    for join_key, *join_conditions in extra_joins:
        if join_conditions:
            collective_bookings_query = collective_bookings_query.join(join_key, *join_conditions, isouter=True)
        else:
            collective_bookings_query = collective_bookings_query.join(join_key, isouter=True)

    if not pro_user.has_admin_role:
        collective_bookings_query = collective_bookings_query.filter(offerers_models.UserOfferer.user == pro_user)

    collective_bookings_query = collective_bookings_query.filter(offerers_models.UserOfferer.isValidated)

    if period:
        period_attribute_filter = (
            BOOKING_DATE_STATUS_MAPPING[status_filter]
            if status_filter
            else BOOKING_DATE_STATUS_MAPPING[models.CollectiveBookingStatusFilter.BOOKED]
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
        collective_bookings_query = collective_bookings_query.filter(models.CollectiveBooking.venueId == venue_id)

    if event_date:
        collective_bookings_query = collective_bookings_query.filter(
            field_to_venue_timezone(models.CollectiveStock.startDatetime) == event_date
        )

    return collective_bookings_query


def list_public_collective_offers(
    *,
    required_id: int,
    status: offer_mixin.CollectiveOfferStatus | None = None,
    displayedStatus: models.CollectiveOfferDisplayedStatus | None = None,
    venue_id: int | None = None,
    period_beginning_date: str | None = None,
    period_ending_date: str | None = None,
    ids: list[int] | None = None,
    limit: int = 500,
) -> list[models.CollectiveOffer]:
    query = db.session.query(models.CollectiveOffer)

    query = query.join(providers_models.Provider, models.CollectiveOffer.provider)

    query = query.join(models.CollectiveStock, models.CollectiveOffer.collectiveStock)

    filters = [
        models.CollectiveOffer.providerId == required_id,
        models.CollectiveOffer.validation != offer_mixin.OfferValidationStatus.DRAFT,
    ]

    if status is not None:
        filters.append(models.CollectiveOffer.status == status)  # type: ignore[arg-type]
    if venue_id:
        filters.append(models.CollectiveOffer.venueId == venue_id)
    if period_beginning_date:
        filters.append(models.CollectiveStock.startDatetime >= period_beginning_date)
    if period_ending_date:
        filters.append(models.CollectiveStock.startDatetime <= period_ending_date)
    if ids is not None:
        filters.append(models.CollectiveOffer.id.in_(ids))

    query = query.filter(*filters)
    query = query.options(
        sa_orm.joinedload(models.CollectiveOffer.collectiveStock)
        .load_only(
            models.CollectiveStock.bookingLimitDatetime,
            models.CollectiveStock.startDatetime,
            models.CollectiveStock.endDatetime,
        )
        .joinedload(models.CollectiveStock.collectiveBookings)
        .load_only(
            models.CollectiveBooking.id,
            models.CollectiveBooking.status,
            models.CollectiveBooking.confirmationDate,
            models.CollectiveBooking.cancellationLimitDate,
            models.CollectiveBooking.reimbursementDate,
            models.CollectiveBooking.dateUsed,
            models.CollectiveBooking.dateCreated,
        )
    )

    if displayedStatus is not None:
        query = filter_collective_offers_by_statuses(query, statuses=[displayedStatus])

    query = query.order_by(models.CollectiveOffer.id)
    query = query.limit(limit)
    return query.all()


def _get_filtered_collective_bookings_pro(
    pro_user: User,
    period: tuple[date, date] | None = None,
    status_filter: models.CollectiveBookingStatusFilter | None = None,
    event_date: datetime | None = None,
    venue_id: int | None = None,
) -> sa_orm.Query:
    bookings_query = (
        _get_filtered_collective_bookings_query(
            pro_user,
            period,
            status_filter,
            event_date,
            venue_id,
            extra_joins=(
                (models.CollectiveStock.collectiveOffer,),
                (models.CollectiveBooking.educationalInstitution,),
            ),
        )
        .options(sa_orm.joinedload(models.CollectiveBooking.collectiveStock))
        .options(
            sa_orm.joinedload(models.CollectiveBooking.collectiveStock).joinedload(
                models.CollectiveStock.collectiveOffer
            )
        )
        .options(sa_orm.joinedload(models.CollectiveBooking.educationalInstitution))
        .options(sa_orm.joinedload(models.CollectiveBooking.venue))
        .options(sa_orm.joinedload(models.CollectiveBooking.offerer))
        .distinct(models.CollectiveBooking.id)
    )
    return bookings_query


def find_collective_bookings_by_pro_user(
    *,
    user: User,
    booking_period: tuple[date, date] | None = None,
    status_filter: models.CollectiveBookingStatusFilter | None = None,
    event_date: datetime | None = None,
    venue_id: int | None = None,
    page: int = 1,
    per_page_limit: int = 1000,
) -> tuple[int, list[models.CollectiveBooking]]:
    total_collective_bookings = (
        _get_filtered_collective_bookings_query(
            pro_user=user,
            period=booking_period,
            status_filter=status_filter,
            event_date=event_date,
            venue_id=venue_id,
        )
        .with_entities(models.CollectiveBooking.id)
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
            models.CollectiveBooking.id.desc(), models.CollectiveBooking.dateCreated.desc()
        )
        .offset((page - 1) * per_page_limit)
        .limit(per_page_limit)
        .all()
    )
    return total_collective_bookings, collective_bookings_page


def get_filtered_collective_booking_report(
    pro_user: User,
    period: tuple[date, date] | None,
    status_filter: models.CollectiveBookingStatusFilter | None,
    event_date: datetime | None = None,
    venue_id: int | None = None,
) -> sa_orm.Query:
    with_entities: tuple[typing.Any, ...] = (
        offerers_models.Venue.common_name.label("venueName"),  # type: ignore[attr-defined]
        offerers_models.Offerer.postalCode.label("offererPostalCode"),
        models.CollectiveOffer.name.label("offerName"),
        models.CollectiveStock.price,
        models.CollectiveStock.startDatetime.label("stockStartDatetime"),
        models.CollectiveStock.bookingLimitDatetime.label("stockBookingLimitDatetime"),
        models.EducationalRedactor.firstName,
        models.EducationalRedactor.lastName,
        models.EducationalRedactor.email,
        models.CollectiveBooking.id,
        models.CollectiveBooking.dateCreated.label("bookedAt"),
        models.CollectiveBooking.dateUsed.label("usedAt"),
        models.CollectiveBooking.reimbursementDate.label("reimbursedAt"),
        models.CollectiveBooking.status,
        models.CollectiveBooking.isConfirmed,
        models.EducationalInstitution.institutionId,
        models.EducationalInstitution.name.label("institutionName"),
        models.EducationalInstitution.institutionType,
        # `get_batch` function needs a field called exactly `id` to work,
        # the label prevents SA from using a bad (prefixed) label for this field
        models.CollectiveBooking.id.label("id"),
        models.CollectiveBooking.educationalRedactorId,
        geography_models.Address.departmentCode.label("venueDepartmentCode"),
    )

    bookings_query = _get_filtered_collective_bookings_query(
        pro_user,
        period,
        status_filter,
        event_date,
        venue_id,
        extra_joins=(
            (models.CollectiveStock.collectiveOffer,),
            (models.CollectiveBooking.educationalRedactor,),
            (models.CollectiveBooking.educationalInstitution,),
            (
                offerers_models.OffererAddress,
                offerers_models.Venue.offererAddressId == offerers_models.OffererAddress.id,
            ),
            (geography_models.Address, offerers_models.OffererAddress.addressId == geography_models.Address.id),
        ),
    )
    bookings_query = bookings_query.with_entities(*with_entities)
    bookings_query = bookings_query.distinct(models.CollectiveBooking.id)

    return bookings_query


def get_collective_offer_by_id_query(offer_id: int) -> sa_orm.Query:
    return (
        db.session.query(models.CollectiveOffer)
        .filter(models.CollectiveOffer.id == offer_id)
        .outerjoin(models.CollectiveStock, models.CollectiveStock.collectiveOfferId == offer_id)
        .options(
            sa_orm.joinedload(models.CollectiveOffer.venue, innerjoin=True).options(
                sa_orm.joinedload(offerers_models.Venue.managingOfferer, innerjoin=True),
                sa_orm.joinedload(offerers_models.Venue.offererAddress).joinedload(
                    offerers_models.OffererAddress.address
                ),
            )
        )
        .options(sa_orm.joinedload(models.CollectiveOffer.domains))
        .options(
            sa_orm.contains_eager(models.CollectiveOffer.collectiveStock)
            .joinedload(models.CollectiveStock.collectiveBookings)
            .joinedload(models.CollectiveBooking.educationalRedactor)
        )
        .options(sa_orm.joinedload(models.CollectiveOffer.nationalProgram))
        .options(sa_orm.joinedload(models.CollectiveOffer.provider))
        .options(sa_orm.joinedload(models.CollectiveOffer.teacher))
        .options(sa_orm.joinedload(models.CollectiveOffer.institution))
        .options(*_get_collective_offer_address_joinedload_with_expression())
    )


def get_collective_offer_by_id(offer_id: int) -> models.CollectiveOffer:
    try:
        return get_collective_offer_by_id_query(offer_id=offer_id).one()
    except sa_orm.exc.NoResultFound:
        raise exceptions.CollectiveOfferNotFound()


def get_collective_offer_and_extra_data(offer_id: int) -> models.CollectiveOffer | None:
    is_non_free_offer_subquery = (
        sa.select(1)
        .select_from(models.CollectiveStock)
        .where(
            models.CollectiveStock.collectiveOfferId == models.CollectiveOffer.id,
            models.CollectiveStock.price > 0,
        )
        .correlate(models.CollectiveOffer)
        .exists()
    )

    collective_offer = (
        get_collective_offer_by_id_query(offer_id=offer_id)
        .options(
            # venue -> managingOfferer -> confidenceRule -> confidenceLevel
            sa_orm.joinedload(models.CollectiveOffer.venue, innerjoin=True)
            .joinedload(offerers_models.Venue.managingOfferer, innerjoin=True)
            .joinedload(offerers_models.Offerer.confidenceRule)
            .load_only(offerers_models.OffererConfidenceRule.confidenceLevel),
            # venue -> confidenceRule -> confidenceLevel
            sa_orm.joinedload(models.CollectiveOffer.venue, innerjoin=True)
            .joinedload(offerers_models.Venue.confidenceRule)
            .load_only(offerers_models.OffererConfidenceRule.confidenceLevel),
        )
        .options(sa_orm.with_expression(models.CollectiveOffer.isNonFreeOffer, is_non_free_offer_subquery))
        .one_or_none()
    )

    return collective_offer


def get_collective_offer_request_by_id(request_id: int) -> models.CollectiveOfferRequest:
    try:
        query = (
            db.session.query(models.CollectiveOfferRequest)
            .filter(models.CollectiveOfferRequest.id == request_id)
            .options(
                sa_orm.joinedload(models.CollectiveOfferRequest.collectiveOfferTemplate)
                .load_only(models.CollectiveOfferTemplate.id)
                .joinedload(models.CollectiveOfferTemplate.venue)
                .load_only(offerers_models.Venue.managingOffererId),
                sa_orm.joinedload(models.CollectiveOfferRequest.educationalRedactor).load_only(
                    models.EducationalRedactor.firstName,
                    models.EducationalRedactor.lastName,
                    models.EducationalRedactor.email,
                ),
                sa_orm.joinedload(models.CollectiveOfferRequest.educationalInstitution),
            )
        )

        return query.one()
    except sa_orm.exc.NoResultFound:
        raise exceptions.CollectiveOfferRequestNotFound()


def get_offerer_ids_from_collective_offers_template_ids(offers_ids: list[int]) -> set[int]:
    query = db.session.query(offerers_models.Offerer.id)
    query = query.join(offerers_models.Offerer, offerers_models.Venue.managingOfferer)
    query = query.join(models.CollectiveOfferTemplate, offerers_models.Venue.collectiveOfferTemplates)
    query = query.filter(models.CollectiveOfferTemplate.id.in_(offers_ids))
    return {result[0] for result in query.all()}


def get_collective_offer_template_by_id(offer_id: int) -> models.CollectiveOfferTemplate:
    try:
        return (
            db.session.query(models.CollectiveOfferTemplate)
            .filter(models.CollectiveOfferTemplate.id == offer_id)
            .options(
                sa_orm.joinedload(models.CollectiveOfferTemplate.venue, innerjoin=True).joinedload(
                    offerers_models.Venue.managingOfferer, innerjoin=True
                )
            )
            .options(sa_orm.joinedload(models.CollectiveOfferTemplate.domains))
            .options(sa_orm.joinedload(models.CollectiveOfferTemplate.nationalProgram))
            .options(*_get_collective_offer_template_address_joinedload_with_expression())
            .one()
        )
    except sa_orm.exc.NoResultFound:
        raise exceptions.CollectiveOfferTemplateNotFound()


def get_collective_offer_templates_for_playlist_query(
    institution_id: int,
    playlist_type: models.PlaylistType,
    max_distance: int | None = None,
    min_distance: int | None = None,
) -> "sa_orm.Query[models.CollectivePlaylist]":
    query = db.session.query(models.CollectivePlaylist).filter(
        models.CollectivePlaylist.type == playlist_type,
        models.CollectivePlaylist.institutionId == institution_id,
    )

    if max_distance:
        query = query.filter(models.CollectivePlaylist.distanceInKm <= max_distance)

    if min_distance:
        query = query.filter(models.CollectivePlaylist.distanceInKm > min_distance)

    query = query.options(
        sa_orm.joinedload(models.CollectivePlaylist.collective_offer_template).options(
            sa_orm.joinedload(models.CollectiveOfferTemplate.venue, innerjoin=True).options(
                sa_orm.joinedload(offerers_models.Venue.managingOfferer, innerjoin=True),
                sa_orm.joinedload(offerers_models.Venue.googlePlacesInfo),
                sa_orm.joinedload(offerers_models.Venue.offererAddress).joinedload(
                    offerers_models.OffererAddress.address
                ),
            ),
            sa_orm.joinedload(models.CollectiveOfferTemplate.domains),
            *_get_collective_offer_template_address_joinedload_with_expression(),
        ),
        sa_orm.joinedload(models.CollectivePlaylist.venue).options(
            sa_orm.joinedload(offerers_models.Venue.googlePlacesInfo),
            sa_orm.joinedload(offerers_models.Venue.offererAddress).joinedload(offerers_models.OffererAddress.address),
        ),
    ).populate_existing()
    return query


def user_has_bookings(user: User) -> bool:
    bookings_query = (
        db.session.query(models.CollectiveBooking)
        .join(models.CollectiveBooking.offerer)
        .join(offerers_models.Offerer.UserOfferers)
    )
    return db.session.query(bookings_query.filter(offerers_models.UserOfferer.userId == user.id).exists()).scalar()


def get_collective_offer_by_id_for_adage(offer_id: int) -> models.CollectiveOffer:
    query = (
        db.session.query(models.CollectiveOffer)
        .filter(
            models.CollectiveOffer.validation == offer_mixin.OfferValidationStatus.APPROVED,
        )
        .options(
            sa_orm.joinedload(models.CollectiveOffer.nationalProgram),
            sa_orm.joinedload(models.CollectiveOffer.teacher).load_only(
                models.EducationalRedactor.email,
                models.EducationalRedactor.firstName,
                models.EducationalRedactor.lastName,
                models.EducationalRedactor.civility,
            ),
            sa_orm.joinedload(models.CollectiveOffer.collectiveStock).joinedload(
                models.CollectiveStock.collectiveBookings
            ),
            sa_orm.joinedload(models.CollectiveOffer.institution),
            sa_orm.joinedload(models.CollectiveOffer.venue).options(
                sa_orm.joinedload(offerers_models.Venue.managingOfferer).load_only(
                    offerers_models.Offerer.name,
                    offerers_models.Offerer.validationStatus,
                    offerers_models.Offerer.isActive,
                ),
                sa_orm.joinedload(offerers_models.Venue.googlePlacesInfo),
                sa_orm.joinedload(offerers_models.Venue.offererAddress).joinedload(
                    offerers_models.OffererAddress.address
                ),
            ),
            sa_orm.joinedload(models.CollectiveOffer.domains),
            *_get_collective_offer_address_joinedload_with_expression(),
        )
    )
    return query.filter(models.CollectiveOffer.id == offer_id).populate_existing().one()


def _get_collective_offer_template_by_id_for_adage_base_query() -> sa_orm.Query:
    return (
        db.session.query(models.CollectiveOfferTemplate)
        .filter(
            models.CollectiveOfferTemplate.validation == offer_mixin.OfferValidationStatus.APPROVED,
        )
        .options(
            sa_orm.joinedload(models.CollectiveOfferTemplate.nationalProgram),
            sa_orm.joinedload(models.CollectiveOfferTemplate.venue).options(
                sa_orm.joinedload(offerers_models.Venue.managingOfferer).load_only(
                    offerers_models.Offerer.name,
                    offerers_models.Offerer.validationStatus,
                    offerers_models.Offerer.isActive,
                ),
                sa_orm.joinedload(offerers_models.Venue.googlePlacesInfo),
                sa_orm.joinedload(offerers_models.Venue.offererAddress).joinedload(
                    offerers_models.OffererAddress.address
                ),
            ),
            sa_orm.joinedload(models.CollectiveOfferTemplate.domains),
            *_get_collective_offer_template_address_joinedload_with_expression(),
        )
    )


def get_collective_offer_template_by_id_for_adage(offer_id: int) -> models.CollectiveOffer:
    query = _get_collective_offer_template_by_id_for_adage_base_query()
    return query.filter(models.CollectiveOfferTemplate.id == offer_id).populate_existing().one()


def get_collective_offer_templates_by_ids_for_adage(offer_ids: typing.Collection[int]) -> sa_orm.Query:
    query = _get_collective_offer_template_by_id_for_adage_base_query()
    # Filter out the archived offers
    query = query.filter(models.CollectiveOfferTemplate.isArchived == False)
    # Filter out the offers not displayed on adage
    query = query.filter(
        models.CollectiveOfferTemplate.isActive == True,
        models.CollectiveOfferTemplate.hasEndDatePassed == False,
    )

    return query.filter(models.CollectiveOfferTemplate.id.in_(offer_ids)).populate_existing()


def get_query_for_collective_offers_by_ids_for_user(user: User, ids: typing.Iterable[int]) -> sa_orm.Query:
    query = db.session.query(models.CollectiveOffer)

    if not user.has_admin_role:
        query = query.join(offerers_models.Venue, models.CollectiveOffer.venue)
        query = query.join(offerers_models.Offerer, offerers_models.Venue.managingOfferer)
        query = query.join(offerers_models.UserOfferer, offerers_models.Offerer.UserOfferers)
        query = query.filter(offerers_models.UserOfferer.userId == user.id, offerers_models.UserOfferer.isValidated)

    query = query.filter(models.CollectiveOffer.id.in_(ids))
    query = query.options(
        sa_orm.joinedload(models.CollectiveOffer.collectiveStock).joinedload(models.CollectiveStock.collectiveBookings)
    )
    return query


def get_query_for_collective_offers_template_by_ids_for_user(user: User, ids: typing.Iterable[int]) -> sa_orm.Query:
    query = db.session.query(models.CollectiveOfferTemplate)
    if not user.has_admin_role:
        query = query.join(offerers_models.Venue, models.CollectiveOfferTemplate.venue)
        query = query.join(offerers_models.Offerer, offerers_models.Venue.managingOfferer)
        query = query.join(offerers_models.UserOfferer, offerers_models.Offerer.UserOfferers)
        query = query.filter(offerers_models.UserOfferer.userId == user.id, offerers_models.UserOfferer.isValidated)
    query = query.filter(models.CollectiveOfferTemplate.id.in_(ids))
    return query


def get_educational_domains_from_ids(ids: typing.Iterable[int]) -> list[models.EducationalDomain]:
    return (
        db.session.query(models.EducationalDomain)
        .filter(models.EducationalDomain.id.in_(ids))
        .options(sa_orm.joinedload(models.EducationalDomain.nationalPrograms))
        .all()
    )


def get_all_educational_domains_ordered_by_name() -> list[models.EducationalDomain]:
    return (
        db.session.query(models.EducationalDomain)
        .order_by(models.EducationalDomain.name)
        .options(sa_orm.joinedload(models.EducationalDomain.nationalPrograms))
        .all()
    )


def get_all_educational_institutions(offset: int = 0, limit: int = 0) -> tuple[tuple, int]:
    query = db.session.query(sa.func.count(models.EducationalInstitution.id))
    query = query.filter(models.EducationalInstitution.isActive)
    total = query.one()[0]

    query = db.session.query(models.EducationalInstitution)
    query = query.filter(models.EducationalInstitution.isActive)
    query = query.order_by(
        models.EducationalInstitution.name,
        models.EducationalInstitution.id,
    )
    query = query.with_entities(
        models.EducationalInstitution.name,
        models.EducationalInstitution.id,
        models.EducationalInstitution.postalCode,
        models.EducationalInstitution.city,
        models.EducationalInstitution.institutionType,
        models.EducationalInstitution.phoneNumber,
        models.EducationalInstitution.institutionId,
    )

    if offset != 0:
        query = query.offset(offset)
    if limit != 0:
        query = query.limit(limit)

    return query.all(), total


def search_educational_institution(
    *,
    educational_institution_id: int | None,
    name: str | None,
    institution_type: str | None,
    city: str | None,
    postal_code: str | None,
    uai: str | None,
    limit: int,
) -> models.EducationalInstitution:
    filters = []
    if educational_institution_id is not None:
        filters.append(models.EducationalInstitution.id == educational_institution_id)

    if name is not None:
        name = name.replace(" ", "%")
        name = name.replace("-", "%")
        filters.append(
            sa.func.unaccent(models.EducationalInstitution.name).ilike(f"%{clean_accents(name)}%"),
        )

    if institution_type is not None:
        institution_type = institution_type.replace(" ", "%")
        institution_type = institution_type.replace("-", "%")
        filters.append(
            sa.func.unaccent(models.EducationalInstitution.institutionType).ilike(
                f"%{clean_accents(institution_type)}%"
            ),
        )

    if city is not None:
        city = city.replace(" ", "%")
        city = city.replace("-", "%")
        filters.append(
            sa.func.unaccent(models.EducationalInstitution.city).ilike(f"%{clean_accents(city)}%"),
        )

    if postal_code is not None:
        postal_code = postal_code.replace(" ", "%")
        postal_code = postal_code.replace("-", "%")
        filters.append(
            sa.func.unaccent(models.EducationalInstitution.postalCode).ilike(f"%{postal_code}%"),
        )

    if uai is not None:
        filters.append(models.EducationalInstitution.institutionId == uai)

    return (
        db.session.query(models.EducationalInstitution)
        .filter(
            *filters,
            models.EducationalInstitution.isActive,
        )
        .order_by(models.EducationalInstitution.id)
        .limit(limit)
        .all()
    )


def find_pending_booking_confirmation_limit_date_in_3_days() -> list[models.CollectiveBooking]:
    target_day = datetime.utcnow() + timedelta(days=3)
    start = datetime.combine(target_day, time.min)
    end = datetime.combine(target_day, time.max)
    query = (
        db.session.query(models.CollectiveBooking)
        .filter(models.CollectiveBooking.confirmationLimitDate.between(start, end))
        .filter(models.CollectiveBooking.status == models.CollectiveBookingStatus.PENDING)
        .distinct()
    )
    query = query.options(sa_orm.joinedload(models.CollectiveBooking.collectiveStock, innerjoin=True))
    query = query.options(
        sa_orm.joinedload(models.CollectiveBooking.collectiveStock, innerjoin=True).joinedload(
            models.CollectiveStock.collectiveOffer, innerjoin=True
        )
    )
    query = query.options(
        sa_orm.joinedload(models.CollectiveBooking.collectiveStock, innerjoin=True)
        .joinedload(models.CollectiveStock.collectiveOffer, innerjoin=True)
        .joinedload(models.CollectiveOffer.venue, innerjoin=True)
    )
    query = query.options(sa_orm.joinedload(models.CollectiveBooking.educationalRedactor, innerjoin=True))
    return query.all()


def get_paginated_active_collective_offer_template_ids(batch_size: int, page: int = 1) -> list[int]:
    query = (
        db.session.query(models.CollectiveOfferTemplate)
        .with_entities(models.CollectiveOfferTemplate.id)
        .filter(
            models.CollectiveOfferTemplate.isActive.is_(True),
        )
        .order_by(models.CollectiveOfferTemplate.id)
        .offset((page - 1) * batch_size)  # first page is 1, not 0
        .limit(batch_size)
    )
    return [offer_id for (offer_id,) in query]


def get_booking_related_bank_account(booking_id: int) -> offerers_models.VenueBankAccountLink | None:
    return (
        db.session.query(finance_models.BankAccount)
        .join(
            offerers_models.VenueBankAccountLink,
            sa.and_(
                offerers_models.VenueBankAccountLink.bankAccountId == finance_models.BankAccount.id,
                offerers_models.VenueBankAccountLink.timespan.contains(datetime.utcnow()),
            ),
        )
        .join(offerers_models.Venue, offerers_models.VenueBankAccountLink.venueId == offerers_models.Venue.id)
        .join(
            models.CollectiveBooking,
            models.CollectiveBooking.venueId == offerers_models.Venue.id,
        )
        .filter(models.CollectiveBooking.id == booking_id)
        .options(sa_orm.load_only(finance_models.BankAccount.status, finance_models.BankAccount.dsApplicationId))
        .one_or_none()
    )


def get_educational_institution_public(
    institution_id: int | None, uai: str | None
) -> models.EducationalInstitution | None:
    return (
        db.session.query(models.EducationalInstitution)
        .filter(
            sa.or_(
                models.EducationalInstitution.institutionId == uai,
                models.EducationalInstitution.id == institution_id,
            ),
        )
        .one_or_none()
    )


def get_all_offer_template_by_redactor_id(redactor_id: int) -> list[models.CollectiveOfferTemplate]:
    return (
        db.session.query(models.CollectiveOfferTemplate)
        .join(
            models.EducationalRedactor,
            models.CollectiveOfferTemplate.educationalRedactorsFavorite,
        )
        .options(
            sa_orm.joinedload(models.CollectiveOfferTemplate.venue).options(
                sa_orm.joinedload(offerers_models.Venue.managingOfferer),
                sa_orm.joinedload(offerers_models.Venue.googlePlacesInfo),
                sa_orm.joinedload(offerers_models.Venue.offererAddress).joinedload(
                    offerers_models.OffererAddress.address
                ),
            ),
            sa_orm.joinedload(models.CollectiveOfferTemplate.domains),
            *_get_collective_offer_template_address_joinedload_with_expression(),
        )
        .filter(models.EducationalRedactor.id == redactor_id)
        .populate_existing()
        .all()
    )


def get_venue_base_query() -> sa_orm.Query:
    return (
        db.session.query(offerers_models.Venue)
        .filter(
            offerers_models.Venue.adageId.is_not(None),
        )
        .options(sa_orm.joinedload(offerers_models.Venue.adage_addresses))
    )


def fetch_venue_for_new_offer(venue_id: int, requested_provider_id: int) -> offerers_models.Venue:
    query = (
        db.session.query(offerers_models.Venue)
        .filter(offerers_models.Venue.id == venue_id)
        .join(providers_models.VenueProvider, offerers_models.Venue.venueProviders)
        .filter(providers_models.VenueProvider.providerId == requested_provider_id)
        .options(
            sa_orm.joinedload(offerers_models.Venue.offererAddress),
            sa_orm.joinedload(offerers_models.Venue.managingOfferer)
            .joinedload(offerers_models.Offerer.confidenceRule)
            .load_only(offerers_models.OffererConfidenceRule.confidenceLevel),
            sa_orm.joinedload(offerers_models.Venue.confidenceRule).load_only(
                offerers_models.OffererConfidenceRule.confidenceLevel
            ),
        )
    )

    venue = query.one_or_none()
    if not venue:
        raise offerers_exceptions.VenueNotFoundException()
    return typing.cast(offerers_models.Venue, venue)


def has_collective_offers_for_program_and_venue_ids(program_name: str, venue_ids: typing.Iterable[str]) -> bool:
    query = (
        db.session.query(models.CollectiveOffer)
        .join(models.EducationalInstitution, models.CollectiveOffer.institution)
        .join(
            models.EducationalInstitution.programAssociations,
        )
        .join(
            models.EducationalInstitutionProgramAssociation.program,
        )
        .filter(
            models.CollectiveOffer.venueId.in_(venue_ids),
            models.CollectiveOffer.validation == offer_mixin.OfferValidationStatus.APPROVED,
            models.EducationalInstitutionProgram.name == program_name,
            models.EducationalInstitutionProgramAssociation.timespan.contains(datetime.utcnow()),
        )
        .exists()
    )

    return db.session.query(query).scalar()


def field_to_venue_timezone(field: sa_orm.InstrumentedAttribute) -> sa.cast:
    # TODO(OA) - use Venue.offererAddress.address.timezone when the virtual venues are migrated
    return sa.cast(sa.func.timezone(Venue.timezone, sa.func.timezone("UTC", field)), sa.Date)


def offerer_has_ongoing_collective_bookings(offerer_id: int, include_used: bool = False) -> bool:
    statuses = [
        models.CollectiveBookingStatus.CONFIRMED,
        models.CollectiveBookingStatus.PENDING,
    ]
    if include_used:
        statuses.append(models.CollectiveBookingStatus.USED)

    return db.session.query(
        db.session.query(models.CollectiveBooking)
        .filter(
            models.CollectiveBooking.offererId == offerer_id,
            models.CollectiveBooking.status.in_(statuses),
        )
        .exists()
    ).scalar()


def get_offers_for_my_institution(uai: str) -> "sa_orm.Query[models.CollectiveOffer]":
    return (
        db.session.query(models.CollectiveOffer)
        .join(models.EducationalInstitution, models.CollectiveOffer.institution)
        .options(
            sa_orm.joinedload(models.CollectiveOffer.collectiveStock).joinedload(
                models.CollectiveStock.collectiveBookings
            ),
            sa_orm.joinedload(models.CollectiveOffer.venue).options(
                sa_orm.joinedload(offerers_models.Venue.managingOfferer),
                sa_orm.joinedload(offerers_models.Venue.googlePlacesInfo),
                sa_orm.joinedload(offerers_models.Venue.offererAddress).joinedload(
                    offerers_models.OffererAddress.address
                ),
            ),
            sa_orm.joinedload(models.CollectiveOffer.institution),
            sa_orm.joinedload(models.CollectiveOffer.teacher),
            sa_orm.joinedload(models.CollectiveOffer.nationalProgram),
            sa_orm.joinedload(models.CollectiveOffer.domains),
            *_get_collective_offer_address_joinedload_with_expression(),
        )
        .filter(
            models.EducationalInstitution.institutionId == uai,
            models.CollectiveOffer.isArchived == False,
        )
        .populate_existing()
    )


def get_active_national_programs() -> "sa_orm.Query[models.NationalProgram]":
    return db.session.query(models.NationalProgram).filter(models.NationalProgram.isActive.is_(True))


def get_national_program_or_none(program_id: int) -> models.NationalProgram | None:
    return db.session.query(models.NationalProgram).filter(models.NationalProgram.id == program_id).one_or_none()


def _get_collective_offer_template_address_joinedload_with_expression() -> tuple[sa_orm.Load, ...]:
    """
    Use this when querying CollectiveOfferTemplate and you need to load its address, including the isLinkedToVenue expression
    """

    return (
        sa_orm.joinedload(models.CollectiveOfferTemplate.offererAddress).joinedload(
            offerers_models.OffererAddress.address
        ),
        sa_orm.joinedload(models.CollectiveOfferTemplate.offererAddress).with_expression(
            offerers_models.OffererAddress._isLinkedToVenue,
            offerers_models.OffererAddress.isLinkedToVenue.expression,  # type: ignore [attr-defined]
        ),
    )


def _get_collective_offer_address_joinedload_with_expression() -> tuple[sa_orm.Load, ...]:
    """
    Use this when querying CollectiveOffer and you need to load its address, including the isLinkedToVenue expression
    """

    return (
        sa_orm.joinedload(models.CollectiveOffer.offererAddress).joinedload(offerers_models.OffererAddress.address),
        sa_orm.joinedload(models.CollectiveOffer.offererAddress).with_expression(
            offerers_models.OffererAddress._isLinkedToVenue,
            offerers_models.OffererAddress.isLinkedToVenue.expression,  # type: ignore [attr-defined]
        ),
    )

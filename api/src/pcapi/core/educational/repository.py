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
from sqlalchemy.sql.selectable import ScalarSelect

from pcapi.core.educational import exceptions
from pcapi.core.educational import models
from pcapi.core.educational import schemas
from pcapi.core.geography import models as geography_models
from pcapi.core.offerers import exceptions as offerers_exceptions
from pcapi.core.offerers import models as offerers_models
from pcapi.core.providers import models as providers_models
from pcapi.core.users.models import User
from pcapi.models import db
from pcapi.models import offer_mixin
from pcapi.utils import date as date_utils
from pcapi.utils.clean_accents import clean_accents


def find_bookings_starting_in_x_days(number_of_days: int) -> list[models.CollectiveBooking]:
    target_day = date_utils.get_naive_utc_now() + timedelta(days=number_of_days)
    start = datetime.combine(target_day, time.min)
    end = datetime.combine(target_day, time.max)
    return find_bookings_in_interval(start, end, models.CollectiveStock.startDatetime)


def find_bookings_ending_in_x_days(number_of_days: int) -> list[models.CollectiveBooking]:
    target_day = date_utils.get_naive_utc_now() + timedelta(days=number_of_days)
    start = datetime.combine(target_day, time.min)
    end = datetime.combine(target_day, time.max)
    return find_bookings_in_interval(start, end, models.CollectiveStock.endDatetime)


def find_bookings_in_interval(
    start: datetime, end: datetime, dateColumn: sa.Column | sa_orm.Mapped[datetime]
) -> list[models.CollectiveBooking]:
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
    )
    query = query.options(sa_orm.joinedload(models.CollectiveBooking.educationalRedactor, innerjoin=True))
    query = query.options(sa_orm.joinedload(models.CollectiveBooking.educationalInstitution, innerjoin=True))
    return query.distinct().all()


def get_and_lock_educational_deposit(
    educational_institution_id: int, educational_year: models.EducationalYear, confirmation_datetime: datetime
) -> models.EducationalDeposit:
    """Returns educational_deposit with a FOR UPDATE lock
    Raises exceptions.EducationalDepositNotFound if no stock is found.
    WARNING: MAKE SURE YOU FREE THE LOCK (with COMMIT or ROLLBACK) and don't hold it longer than
    strictly necessary.
    """
    is_confirmed_in_same_year = (
        educational_year.beginningDate <= confirmation_datetime <= educational_year.expirationDate
    )

    if is_confirmed_in_same_year:
        # confirmation and event are in the same educational year
        # -> the period must contain the confirmation date
        date_for_period_filter = confirmation_datetime
    else:
        # confirmation and event are NOT in the same educational year
        # -> the period must contain the event educational year start
        date_for_period_filter = educational_year.beginningDate

    educational_deposit = (
        db.session.query(models.EducationalDeposit)
        .filter(
            models.EducationalDeposit.educationalInstitutionId == educational_institution_id,
            models.EducationalDeposit.educationalYearId == educational_year.adageId,
            models.EducationalDeposit.period.op("@>")(date_for_period_filter),
        )
        .populate_existing()
        .with_for_update()
        .one_or_none()
    )

    if not educational_deposit:
        raise exceptions.EducationalDepositNotFound()

    return educational_deposit


def get_confirmed_collective_bookings_amount(deposit: models.EducationalDeposit) -> Decimal:
    query = (
        db.session.query(sa.func.sum(models.CollectiveStock.price).label("amount"))
        .join(models.CollectiveBooking, models.CollectiveStock.collectiveBookings)
        .filter(
            models.CollectiveBooking.educationalDepositId == deposit.id,
            models.CollectiveBooking.status.not_in(
                [models.CollectiveBookingStatus.CANCELLED, models.CollectiveBookingStatus.PENDING]
            ),
        )
    )

    result = query.first()
    return result.amount if (result and result.amount) else Decimal(0)


def find_collective_booking_by_id(booking_id: int) -> models.CollectiveBooking | None:
    query = (
        _get_bookings_for_adage_base_query()
        .options(sa_orm.joinedload(models.CollectiveBooking.educationalYear))
        .filter(models.CollectiveBooking.id == booking_id)
    )
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


def find_educational_deposits_by_institution_id_and_year(
    educational_institution_id: int, educational_year_id: str
) -> list[models.EducationalDeposit]:
    return (
        db.session.query(models.EducationalDeposit)
        .filter(
            models.EducationalDeposit.educationalInstitutionId == educational_institution_id,
            models.EducationalDeposit.educationalYearId == educational_year_id,
        )
        .order_by(models.EducationalDeposit.period)
        .all()
    )


def get_educational_deposits_by_year(year_id: str) -> list[models.EducationalDeposit]:
    return (
        db.session.query(models.EducationalDeposit)
        .join(models.EducationalDeposit.educationalInstitution)
        .filter(models.EducationalDeposit.educationalYearId == year_id)
        .options(sa_orm.joinedload(models.EducationalDeposit.educationalInstitution))
        .order_by(models.EducationalDeposit.period)
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


def _get_bookings_for_adage_base_query() -> sa_orm.Query[models.CollectiveBooking]:
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
                    offerers_models.Venue.publicName,
                    offerers_models.Venue.name,
                    offerers_models.Venue.siret,
                ),
                sa_orm.joinedload(offerers_models.Venue.managingOfferer, innerjoin=True).load_only(
                    offerers_models.Offerer.name
                ),
                sa_orm.joinedload(offerers_models.Venue.offererAddress)
                .joinedload(offerers_models.OffererAddress.address)
                .load_only(geography_models.Address.departmentCode, geography_models.Address.timezone),
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

    db.session.add(redactor)
    db.session.flush()
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
                sa_orm.load_only(offerers_models.Venue.id, offerers_models.Venue.name),
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
                models.CollectiveOfferTemplate.hasEndDatePassed.is_(True),
                models.CollectiveOfferTemplate.isArchived.is_(True),
            )
        )
    )


def find_expiring_collective_bookings_query() -> sa_orm.Query[models.CollectiveBooking]:
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
                sa_orm.joinedload(models.CollectiveOffer.venue)
                .joinedload(offerers_models.Venue.offererAddress)
                .joinedload(offerers_models.OffererAddress.address),
            ),
            sa_orm.joinedload(models.CollectiveStock.collectiveBookings),
        )
        .one_or_none()
    )


def get_collective_offers_by_filters(filters: schemas.CollectiveOffersFilter) -> sa_orm.Query[models.CollectiveOffer]:
    query = (
        db.session.query(models.CollectiveOffer)
        .join(models.CollectiveOffer.venue)
        .join(offerers_models.Venue.managingOfferer)
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
        venue_oa = sa_orm.aliased(offerers_models.OffererAddress)
        venue_address = sa_orm.aliased(geography_models.Address)

        subquery = (
            db.session.query(models.CollectiveStock)
            .with_entities(models.CollectiveStock.collectiveOfferId)
            .distinct(models.CollectiveStock.collectiveOfferId)
            .join(models.CollectiveStock.collectiveOffer)
            .join(models.CollectiveOffer.venue)
            .join(venue_oa, offerers_models.Venue.offererAddress)
            .join(venue_address, venue_oa.address)
        )
        if filters.period_beginning_date is not None:
            subquery = subquery.filter(
                sa.func.timezone(
                    venue_address.timezone,
                    sa.func.timezone("UTC", models.CollectiveStock.startDatetime),
                )
                >= filters.period_beginning_date
            )
        if filters.period_ending_date is not None:
            subquery = subquery.filter(
                sa.func.timezone(
                    venue_address.timezone,
                    sa.func.timezone("UTC", models.CollectiveStock.startDatetime),
                )
                <= datetime.combine(filters.period_ending_date, time.max),
            )
        if filters.venue_id is not None:
            subquery = subquery.filter(models.CollectiveOffer.venueId == filters.venue_id)
        elif filters.offerer_id is not None:
            subquery = subquery.filter(offerers_models.Venue.managingOffererId == filters.offerer_id)

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


def get_collective_offers_template_by_filters(
    filters: schemas.CollectiveOffersFilter,
) -> sa_orm.Query[models.CollectiveOfferTemplate]:
    """
    Filters
        period_beginning_date:
            Applied on the lower part of dateRange.
        period_ending_date
            Applied on the lower part of dateRange.
    """
    query = (
        db.session.query(models.CollectiveOfferTemplate)
        .join(models.CollectiveOfferTemplate.venue)
        .join(offerers_models.Venue.managingOfferer)
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
        query = query.filter(models.CollectiveOfferTemplate.displayedStatus.in_(status_values))

    date_filters = []
    if filters.period_beginning_date is not None or filters.period_ending_date is not None:
        if filters.period_beginning_date is not None:
            date_filters.append(
                sa.func.lower(models.CollectiveOfferTemplate.dateRange) >= filters.period_beginning_date
            )
        if filters.period_ending_date is not None:
            date_filters.append(
                sa.func.lower(models.CollectiveOfferTemplate.dateRange)
                <= datetime.combine(filters.period_ending_date, time.max),
            )
        query = query.filter(sa.or_(models.CollectiveOfferTemplate.dateRange == None, sa.and_(*date_filters)))

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


def get_last_booking_id_subquery() -> ScalarSelect[int]:
    # to use this subquery, a join on CollectiveStock is needed in the enclosing query
    # so that correlate finds the correct stock

    return (
        sa.select(models.CollectiveBooking.id)
        .where(models.CollectiveBooking.collectiveStockId == models.CollectiveStock.id)
        .order_by(models.CollectiveBooking.dateCreated.desc())
        .limit(1)
        .correlate(models.CollectiveStock)
        .scalar_subquery()
    )


def filter_collective_offers_by_statuses(
    query: sa_orm.Query[models.CollectiveOffer], statuses: list[models.CollectiveOfferDisplayedStatus] | None
) -> sa_orm.Query[models.CollectiveOffer]:
    """
    Filter a SQLAlchemy query for CollectiveOffers based on a list of statuses.

    This function modifies the input query to filter CollectiveOffers based on their displayedStatus.
    As displayedStatus is a (non-hybrid) python property, we generate the SQL clauses corresponding to each status.

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

    # to compute the status, we need information from the offer, the stock and the last booking
    last_booking_id = get_last_booking_id_subquery()
    query_with_booking = query.outerjoin(models.CollectiveOffer.collectiveStock).outerjoin(
        models.CollectiveBooking, models.CollectiveBooking.id == last_booking_id
    )

    if models.CollectiveOfferDisplayedStatus.ARCHIVED in statuses:
        on_collective_offer_filters.append(models.CollectiveOffer.isArchived.is_(True))

    if models.CollectiveOfferDisplayedStatus.DRAFT in statuses:
        on_collective_offer_filters.append(
            sa.and_(
                models.CollectiveOffer.validation == offer_mixin.OfferValidationStatus.DRAFT,
                models.CollectiveOffer.isArchived.is_(False),
            )
        )

    if models.CollectiveOfferDisplayedStatus.UNDER_REVIEW in statuses:
        on_collective_offer_filters.append(
            sa.and_(
                models.CollectiveOffer.validation == offer_mixin.OfferValidationStatus.PENDING,
                models.CollectiveOffer.isArchived.is_(False),
            )
        )

    if models.CollectiveOfferDisplayedStatus.REJECTED in statuses:
        on_collective_offer_filters.append(
            sa.and_(
                models.CollectiveOffer.validation == offer_mixin.OfferValidationStatus.REJECTED,
                models.CollectiveOffer.isArchived.is_(False),
            )
        )

    if models.CollectiveOfferDisplayedStatus.HIDDEN in statuses:
        # if the statuses filter contains HIDDEN only, we need to return no collective_offer
        # otherwise we return offers depending on the other statuses in the filter
        on_collective_offer_filters.append(sa.false())

    approved_and_active_filters = (
        models.CollectiveOffer.validation == offer_mixin.OfferValidationStatus.APPROVED,
        models.CollectiveOffer.isActive == True,
    )

    if models.CollectiveOfferDisplayedStatus.PUBLISHED in statuses:
        on_booking_status_filter.append(
            sa.and_(
                *approved_and_active_filters,
                models.CollectiveBooking.status == None,
                models.CollectiveStock.hasBookingLimitDatetimePassed == False,
            )
        )

    if models.CollectiveOfferDisplayedStatus.PREBOOKED in statuses:
        on_booking_status_filter.append(
            sa.and_(
                *approved_and_active_filters,
                models.CollectiveBooking.status == models.CollectiveBookingStatus.PENDING,
                models.CollectiveStock.hasBookingLimitDatetimePassed == False,
            )
        )

    if models.CollectiveOfferDisplayedStatus.BOOKED in statuses:
        on_booking_status_filter.append(
            sa.and_(
                *approved_and_active_filters,
                models.CollectiveBooking.status == models.CollectiveBookingStatus.CONFIRMED,
                models.CollectiveStock.hasEndDatetimePassed == False,
            )
        )

    if models.CollectiveOfferDisplayedStatus.ENDED in statuses:
        on_booking_status_filter.append(
            sa.and_(
                *approved_and_active_filters,
                sa.or_(
                    models.CollectiveBooking.status == models.CollectiveBookingStatus.USED,
                    models.CollectiveBooking.status == models.CollectiveBookingStatus.CONFIRMED,
                ),
                models.CollectiveStock.hasEndDatetimePassed == True,
            )
        )

    if models.CollectiveOfferDisplayedStatus.REIMBURSED in statuses:
        on_booking_status_filter.append(
            sa.and_(
                *approved_and_active_filters,
                models.CollectiveBooking.status == models.CollectiveBookingStatus.REIMBURSED,
            )
        )

    if models.CollectiveOfferDisplayedStatus.EXPIRED in statuses:
        # expired with a pending booking or no booking
        on_booking_status_filter.append(
            sa.and_(
                *approved_and_active_filters,
                models.CollectiveStock.hasBookingLimitDatetimePassed == True,
                models.CollectiveStock.hasStartDatetimePassed == False,
                sa.or_(
                    models.CollectiveBooking.status == models.CollectiveBookingStatus.PENDING,
                    models.CollectiveBooking.status == None,
                ),
            )
        )
        # expired with a booking cancelled with reason EXPIRED
        on_booking_status_filter.append(
            sa.and_(
                *approved_and_active_filters,
                models.CollectiveStock.hasBookingLimitDatetimePassed == True,
                models.CollectiveStock.hasStartDatetimePassed == False,
                models.CollectiveBooking.status == models.CollectiveBookingStatus.CANCELLED,
                models.CollectiveBooking.cancellationReason == models.CollectiveBookingCancellationReasons.EXPIRED,
            )
        )

    if models.CollectiveOfferDisplayedStatus.CANCELLED in statuses:
        # Cancelled due to expired booking and event started
        on_booking_status_filter.append(
            sa.and_(
                *approved_and_active_filters,
                models.CollectiveBooking.status == models.CollectiveBookingStatus.CANCELLED,
                models.CollectiveBooking.cancellationReason == models.CollectiveBookingCancellationReasons.EXPIRED,
                models.CollectiveStock.hasStartDatetimePassed == True,
            )
        )

        # Cancelled by admin, pro user or ADAGE
        on_booking_status_filter.append(
            sa.and_(
                *approved_and_active_filters,
                models.CollectiveBooking.status == models.CollectiveBookingStatus.CANCELLED,
                models.CollectiveBooking.cancellationReason != models.CollectiveBookingCancellationReasons.EXPIRED,
            ),
        )

        # Cancelled due to no booking when the event has started
        on_booking_status_filter.append(
            sa.and_(
                *approved_and_active_filters,
                models.CollectiveBooking.status == None,
                models.CollectiveStock.hasStartDatetimePassed == True,
            ),
        )

    # Add filters on CollectiveBooking and CollectiveStock
    if on_booking_status_filter:
        subquery = (
            query_with_booking.filter(sa.or_(*on_booking_status_filter))
            .with_entities(models.CollectiveOffer.id)
            .subquery()
        )
        on_collective_offer_filters.append(models.CollectiveOffer.id.in_(sa.select(subquery.c.id)))

    # Add filters on CollectiveOffer
    if on_collective_offer_filters:
        query = query.filter(sa.or_(*on_collective_offer_filters))

    return query


def list_collective_offers(filters: schemas.CollectiveOffersFilter, offers_limit: int) -> list[models.CollectiveOffer]:
    query = get_collective_offers_by_filters(filters=filters)

    offers = (
        query.order_by(models.CollectiveOffer.isArchived, models.CollectiveOffer.dateCreated.desc())
        .options(
            sa_orm.joinedload(models.CollectiveOffer.venue).options(
                sa_orm.joinedload(offerers_models.Venue.managingOfferer),
                sa_orm.joinedload(offerers_models.Venue.offererAddress).joinedload(
                    offerers_models.OffererAddress.address
                ),
            ),
            _get_collective_offer_address_joinedload(),
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


def list_collective_offer_templates(
    filters: schemas.CollectiveOffersFilter, offers_limit: int
) -> list[models.CollectiveOfferTemplate]:
    query = get_collective_offers_template_by_filters(filters=filters)

    offers = (
        query.order_by(models.CollectiveOfferTemplate.isArchived, models.CollectiveOfferTemplate.dateCreated.desc())
        .options(
            sa_orm.joinedload(models.CollectiveOfferTemplate.venue).options(
                sa_orm.joinedload(offerers_models.Venue.managingOfferer),
                sa_orm.joinedload(offerers_models.Venue.offererAddress).joinedload(
                    offerers_models.OffererAddress.address
                ),
            ),
            _get_collective_offer_template_address_joinedload(),
        )
        .limit(offers_limit)
        .populate_existing()
        .all()
    )

    return offers


def list_public_collective_offers(
    *,
    required_id: int,
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


def get_collective_offer_by_id_query(offer_id: int) -> sa_orm.Query[models.CollectiveOffer]:
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
        .options(_get_collective_offer_address_joinedload())
    )


def get_collective_offer_by_id(offer_id: int) -> models.CollectiveOffer:
    try:
        return get_collective_offer_by_id_query(offer_id=offer_id).populate_existing().one()
    except sa_orm.exc.NoResultFound:
        raise exceptions.CollectiveOfferNotFound()


def get_collective_offer_and_confidence_rules(offer_id: int) -> models.CollectiveOffer | None:
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
            .options(_get_collective_offer_template_address_joinedload())
            .one()
        )
    except sa_orm.exc.NoResultFound:
        raise exceptions.CollectiveOfferTemplateNotFound()


def get_collective_offer_templates_for_playlist_query(
    institution_id: int,
    playlist_type: models.PlaylistType,
    max_distance: int | None = None,
    min_distance: int | None = None,
) -> sa_orm.Query[models.CollectivePlaylist]:
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
            _get_collective_offer_template_address_joinedload(),
        ),
        sa_orm.joinedload(models.CollectivePlaylist.venue).options(
            sa_orm.joinedload(offerers_models.Venue.googlePlacesInfo),
            sa_orm.joinedload(offerers_models.Venue.offererAddress).joinedload(offerers_models.OffererAddress.address),
        ),
    ).populate_existing()
    return query


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
            _get_collective_offer_address_joinedload(),
        )
    )
    return query.filter(models.CollectiveOffer.id == offer_id).populate_existing().one()


def _get_collective_offer_template_by_id_for_adage_base_query() -> sa_orm.Query[models.CollectiveOfferTemplate]:
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
            _get_collective_offer_template_address_joinedload(),
        )
    )


def get_collective_offer_template_by_id_for_adage(offer_id: int) -> models.CollectiveOffer:
    query = _get_collective_offer_template_by_id_for_adage_base_query()
    return query.filter(models.CollectiveOfferTemplate.id == offer_id).populate_existing().one()


def get_collective_offer_templates_by_ids_for_adage(
    offer_ids: typing.Collection[int],
) -> sa_orm.Query[models.CollectiveOfferTemplate]:
    query = _get_collective_offer_template_by_id_for_adage_base_query()
    # Filter out the archived offers
    query = query.filter(models.CollectiveOfferTemplate.isArchived.is_(False))
    # Filter out the offers not displayed on adage
    query = query.filter(
        models.CollectiveOfferTemplate.isActive == True,
        models.CollectiveOfferTemplate.hasEndDatePassed == False,
    )

    return query.filter(models.CollectiveOfferTemplate.id.in_(offer_ids)).populate_existing()


def get_query_for_collective_offers_by_ids_for_user(
    user: User, ids: typing.Iterable[int]
) -> sa_orm.Query[models.CollectiveOffer]:
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


def get_query_for_collective_offers_template_by_ids_for_user(
    user: User, ids: typing.Iterable[int]
) -> sa_orm.Query[models.CollectiveOfferTemplate]:
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


def get_educational_domains_from_names(names: list[str]) -> list[models.EducationalDomain]:
    return db.session.query(models.EducationalDomain).filter(models.EducationalDomain.name.in_(names)).all()


def get_all_educational_domains_ordered_by_name() -> list[models.EducationalDomain]:
    return (
        db.session.query(models.EducationalDomain)
        .order_by(models.EducationalDomain.name)
        .options(sa_orm.joinedload(models.EducationalDomain.nationalPrograms))
        .all()
    )


def get_all_educational_institutions(
    offset: int = 0, limit: int = 0
) -> tuple[list[models.EducationalInstitution], int]:
    active_institutions_query = db.session.query(models.EducationalInstitution).filter(
        models.EducationalInstitution.isActive.is_(True)
    )
    total = active_institutions_query.count()

    query = active_institutions_query.order_by(models.EducationalInstitution.name, models.EducationalInstitution.id)

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
) -> list[models.EducationalInstitution]:
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
    target_day = date_utils.get_naive_utc_now() + timedelta(days=3)
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
            _get_collective_offer_template_address_joinedload(),
        )
        .filter(models.EducationalRedactor.id == redactor_id)
        .populate_existing()
        .all()
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
    return venue


def has_collective_offers_for_program_and_venue_ids(program_name: str, venue_ids: typing.Iterable[str | int]) -> bool:
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
            models.EducationalInstitutionProgramAssociation.timespan.contains(date_utils.get_naive_utc_now()),
        )
        .exists()
    )

    return db.session.query(query).scalar()


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


def get_offers_for_my_institution(uai: str) -> sa_orm.Query[models.CollectiveOffer]:
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
            _get_collective_offer_address_joinedload(),
        )
        .filter(
            models.EducationalInstitution.institutionId == uai,
            models.CollectiveOffer.isArchived.is_(False),
        )
        .populate_existing()
    )


def get_active_national_programs() -> sa_orm.Query[models.NationalProgram]:
    return db.session.query(models.NationalProgram).filter(models.NationalProgram.isActive.is_(True))


def get_national_program_or_none(program_id: int) -> models.NationalProgram | None:
    return db.session.query(models.NationalProgram).filter(models.NationalProgram.id == program_id).one_or_none()


def _get_collective_offer_template_address_joinedload() -> sa_orm.strategy_options._AbstractLoad:
    """
    Use this when querying CollectiveOfferTemplate and you need to load its address
    """

    return sa_orm.joinedload(models.CollectiveOfferTemplate.offererAddress).joinedload(
        offerers_models.OffererAddress.address
    )


def _get_collective_offer_address_joinedload() -> sa_orm.interfaces.LoaderOption:
    """
    Use this when querying CollectiveOffer and you need to load its address
    """

    return sa_orm.joinedload(models.CollectiveOffer.offererAddress).joinedload(offerers_models.OffererAddress.address)


def get_synchronized_collective_offers_with_provider_for_venue(
    venue_id: int, provider_id: int
) -> sa_orm.Query[models.CollectiveOffer]:
    return (
        db.session.query(models.CollectiveOffer)
        .filter(models.CollectiveOffer.venueId == venue_id)
        .filter(models.CollectiveOffer.providerId == provider_id)
    )

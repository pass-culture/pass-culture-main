import typing
from collections.abc import Sequence
from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

from pcapi.core.bookings import constants
from pcapi.core.bookings import models
from pcapi.core.categories import subcategories
from pcapi.core.finance.models import BookingFinanceIncident
from pcapi.core.finance.models import FinanceIncident
from pcapi.core.geography.models import Address
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers import repository as offerers_repository
from pcapi.core.offers import models as offers_models
from pcapi.core.providers.models import VenueProvider
from pcapi.core.users.models import User
from pcapi.models import db
from pcapi.utils import date as date_utils
from pcapi.utils.token import random_token


BOOKING_DATE_STATUS_MAPPING: dict[models.BookingStatusFilter, sa_orm.InstrumentedAttribute] = {
    models.BookingStatusFilter.BOOKED: models.Booking.dateCreated,
    models.BookingStatusFilter.VALIDATED: models.Booking.dateUsed,
    models.BookingStatusFilter.REIMBURSED: models.Booking.reimbursementDate,
}

BOOKING_LOAD_OPTIONS = Sequence[typing.Literal["offerer", "venue", "offer", "address"]]


def duplicate_booking_when_quantity_is_two(bookings_recap_query: sa_orm.Query) -> sa_orm.Query:
    duplicated_booking_rows = (
        sa.func.generate_series(1, models.Booking.quantity).table_valued("duplicate_index").lateral()
    )
    return bookings_recap_query.join(duplicated_booking_rows, sa.true())


def find_by_venue(
    *,
    pro_user_id: int,
    venue_id: int,
    booking_period: tuple[date, date] | None = None,
    status_filter: models.BookingStatusFilter | None = None,
    event_date: date | None = None,
    offer_id: int | None = None,
    offerer_address_id: int | None = None,
    page: int = 1,
    per_page_limit: int = constants.BOOKINGS_PER_PAGE_LIMIT,
) -> tuple[sa_orm.Query, int]:
    total_bookings_recap = _get_filtered_bookings_count(
        pro_user_id=pro_user_id,
        venue_id=venue_id,
        period=booking_period,
        status_filter=status_filter,
        event_date=event_date,
        offer_id=offer_id,
        offerer_address_id=offerer_address_id,
    )

    bookings_query = _get_filtered_booking_pro(
        pro_user_id=pro_user_id,
        venue_id=venue_id,
        period=booking_period,
        status_filter=status_filter,
        event_date=event_date,
        offer_id=offer_id,
        offerer_address_id=offerer_address_id,
    )
    bookings_query = duplicate_booking_when_quantity_is_two(bookings_query)
    bookings_query = (
        bookings_query.order_by(sa.text('"bookedAt" DESC')).offset((page - 1) * per_page_limit).limit(per_page_limit)
    )

    return bookings_query, total_bookings_recap


def find_ongoing_bookings_by_stock(stock_id: int) -> list[models.Booking]:
    return (
        db.session.query(models.Booking)
        .filter(
            models.Booking.stockId == stock_id,
            models.Booking.status == models.BookingStatus.CONFIRMED,
        )
        .all()
    )


def find_not_cancelled_bookings_by_stock(stock: offers_models.Stock) -> list[models.Booking]:
    return (
        db.session.query(models.Booking)
        .filter(models.Booking.stockId == stock.id, models.Booking.status != models.BookingStatus.CANCELLED)
        .all()
    )


def token_exists(token: str) -> bool:
    return db.session.query(db.session.query(models.Booking).filter_by(token=token.upper()).exists()).scalar()


def get_booking_by_token(token: str, load_options: BOOKING_LOAD_OPTIONS = ()) -> models.Booking | None:
    query = db.session.query(models.Booking).filter_by(token=token.upper())
    if "offerer" in load_options:
        query = query.options(sa_orm.joinedload(models.Booking.offerer))
    if "venue" in load_options:
        query = query.options(sa_orm.joinedload(models.Booking.venue))
    if "offer" in load_options or "address" in load_options:
        query_options = sa_orm.joinedload(models.Booking.stock).joinedload(offers_models.Stock.offer)
        if "address" in load_options:
            query_options = query_options.joinedload(offers_models.Offer.offererAddress).joinedload(
                offerers_models.OffererAddress.address
            )
        query = query.options(query_options)
    return query.one_or_none()


def find_expiring_individual_bookings_query() -> sa_orm.Query:
    today_at_midnight = datetime.combine(date.today(), time(0, 0))
    return (
        db.session.query(models.Booking)
        .join(offers_models.Stock)
        .join(offers_models.Offer)
        .filter(
            models.Booking.status == models.BookingStatus.CONFIRMED,
            offers_models.Offer.canExpire,
            sa.case(
                (
                    offers_models.Offer.subcategoryId == subcategories.LIVRE_PAPIER.id,
                    (models.Booking.dateCreated + constants.BOOKS_BOOKINGS_AUTO_EXPIRY_DELAY) <= today_at_midnight,
                ),
                else_=((models.Booking.dateCreated + constants.BOOKINGS_AUTO_EXPIRY_DELAY) <= today_at_midnight),
            ),
        )
    )


def find_soon_to_be_expiring_individual_bookings_ordered_by_user(given_date: date | None = None) -> sa_orm.Query:
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
        db.session.query(models.Booking)
        .join(offers_models.Stock)
        .join(offers_models.Offer)
        .filter(
            models.Booking.status == models.BookingStatus.CONFIRMED,
            offers_models.Offer.canExpire,
            sa.case(
                (
                    offers_models.Offer.subcategoryId == subcategories.LIVRE_PAPIER.id,
                    ((models.Booking.dateCreated + constants.BOOKS_BOOKINGS_AUTO_EXPIRY_DELAY).between(*books_window)),
                ),
                else_=(models.Booking.dateCreated + constants.BOOKINGS_AUTO_EXPIRY_DELAY).between(*rest_window),
            ),
        )
        .order_by(models.Booking.userId)
    )


def generate_booking_token() -> str:
    for _ in range(100):
        token = random_token()
        if not token_exists(token):
            return token
    raise ValueError("Could not generate new booking token")


def find_user_ids_with_expired_individual_bookings(expired_on: date | None = None) -> list[int]:
    expired_on = expired_on or date.today()
    return [
        user_id
        for (user_id,) in (
            db.session.query(User.id)
            .join(models.Booking, User.userBookings)
            .filter(
                models.Booking.status == models.BookingStatus.CANCELLED,
                models.Booking.cancellationDate >= expired_on,
                models.Booking.cancellationDate < (expired_on + timedelta(days=1)),
                models.Booking.cancellationReason == models.BookingCancellationReasons.EXPIRED,
            )
            .all()
        )
    ]


def get_expired_individual_bookings_for_user(user: User, expired_on: date | None = None) -> list[models.Booking]:
    expired_on = expired_on or date.today()
    return (
        db.session.query(models.Booking)
        .filter(
            models.Booking.userId == user.id,
            models.Booking.status == models.BookingStatus.CANCELLED,
            models.Booking.cancellationDate >= expired_on,
            models.Booking.cancellationDate < (expired_on + timedelta(days=1)),
            models.Booking.cancellationReason == models.BookingCancellationReasons.EXPIRED,
        )
        .all()
    )


def find_expired_individual_bookings_ordered_by_offerer(expired_on: date | None = None) -> list[models.Booking]:
    expired_on = expired_on or date.today()
    return (
        db.session.query(models.Booking)
        .filter(models.Booking.status == models.BookingStatus.CANCELLED)
        .filter(sa.cast(models.Booking.cancellationDate, sa.Date) == expired_on)
        .filter(models.Booking.cancellationReason == models.BookingCancellationReasons.EXPIRED)
        .order_by(models.Booking.offererId)
        .all()
    )


def get_bookings_from_deposit(deposit_id: int) -> Sequence[models.Booking]:
    query = (
        sa.select(models.Booking)
        .where(
            models.Booking.depositId == deposit_id,
            models.Booking.status != models.BookingStatus.CANCELLED,
        )
        .options(
            sa_orm.load_only(
                models.Booking.amount,
                models.Booking.depositId,
                models.Booking.quantity,
                models.Booking.status,
            )
        )
        .options(
            sa_orm.joinedload(models.Booking.stock)
            .load_only()
            .joinedload(offers_models.Stock.offer)
            .load_only(offers_models.Offer.subcategoryId, offers_models.Offer.url),
            sa_orm.joinedload(models.Booking.incidents)
            .load_only(BookingFinanceIncident.newTotalAmount)
            .joinedload(BookingFinanceIncident.incident)
            .load_only(FinanceIncident.status),
        )
    )
    return db.session.scalars(query).unique().all()


def export_query(offer_id: int, event_beginning_date: date) -> sa_orm.Query:
    VenueOffererAddress = sa_orm.aliased(offerers_models.OffererAddress)
    VenueAddress = sa_orm.aliased(Address)

    with_entities: tuple[typing.Any, ...] = (
        models.Booking.id.label("id"),
        offerers_models.Venue.publicName.label("venueName"),
        offers_models.Offer.name.label("offerName"),
        offers_models.Stock.beginningDatetime.label("stockBeginningDatetime"),
        offers_models.Stock.offerId,
        offers_models.Offer.ean,
        User.firstName.label("beneficiaryFirstName"),
        User.lastName.label("beneficiaryLastName"),
        User.email.label("beneficiaryEmail"),
        User.phoneNumber.label("beneficiaryPhoneNumber"),
        User.postalCode.label("beneficiaryPostalCode"),
        models.Booking.token,
        models.Booking.priceCategoryLabel,
        models.Booking.amount,
        models.Booking.quantity,
        models.Booking.status,
        models.Booking.dateCreated.label("bookedAt"),
        models.Booking.dateUsed.label("usedAt"),
        models.Booking.reimbursementDate.label("reimbursedAt"),
        models.Booking.cancellationDate.label("cancelledAt"),
        models.Booking.isExternal.label("isExternal"),
        models.Booking.isConfirmed,
        offerers_models.Offerer.is_caledonian,
        # `get_batch` function needs a field called exactly `id` to work,
        # the label prevents SA from using a bad (prefixed) label for this field
        models.Booking.userId,
        Address.departmentCode.label("offerDepartmentCode"),
        VenueAddress.departmentCode.label("venueDepartmentCode"),
        # TODO(OA): no more need to publicName here since the offer OA has a label
        sa.func.coalesce(
            sa.func.nullif(offerers_models.OffererAddress.label, ""), offerers_models.Venue.publicName
        ).label("locationName"),
        Address.street.label("locationStreet"),
        Address.postalCode.label("locationPostalCode"),
        Address.city.label("locationCity"),
    )

    query = (
        db.session.query(models.Booking)
        .join(models.Booking.offerer)
        .join(models.Booking.user)
        .join(offerers_models.Offerer.UserOfferers)
        .join(models.Booking.venue)
        .join(models.Booking.stock)
        .join(offers_models.Stock.offer)
        .outerjoin(offers_models.Offer.offererAddress)
        .outerjoin(offerers_models.OffererAddress.address)
        .join(VenueOffererAddress, offerers_models.Venue.offererAddress)
        .join(VenueAddress, VenueOffererAddress.address)
    )
    timezone_column = sa.func.coalesce(Address.timezone, VenueAddress.timezone)

    query = (
        query.filter(
            offers_models.Stock.offerId == offer_id,
            field_to_venue_timezone(offers_models.Stock.beginningDatetime, timezone_column) == event_beginning_date,
        )
        .order_by(models.Booking.id)
        .with_entities(*with_entities)
    )
    return query.distinct(models.Booking.id)


def validated_bookings_by_offer_id_query(offer_id: int, event_beginning_date: date) -> sa_orm.Query[models.Booking]:
    offer_validated_bookings_query = export_query(offer_id, event_beginning_date)
    return offer_validated_bookings_query.filter(
        sa.or_(
            sa.and_(models.Booking.isConfirmed.is_(True), models.Booking.status != models.BookingStatus.CANCELLED),
            models.Booking.status == models.BookingStatus.USED,
        )
    )


def field_to_venue_timezone(
    field: sa_orm.InstrumentedAttribute, column: sa_orm.Mapped[typing.Any] | sa.sql.functions.Function
) -> sa.Cast[date]:
    return sa.cast(sa.func.timezone(column, sa.func.timezone("UTC", field)), sa.Date)


def _get_filtered_bookings_query(
    *,
    pro_user_id: int,
    venue_ids: list[int],
    period: tuple[date, date] | None = None,
    status_filter: models.BookingStatusFilter | None = None,
    event_date: date | None = None,
    offer_id: int | None = None,
    offerer_address_id: int | None = None,
    extra_joins: tuple[tuple[typing.Any, ...], ...] = (),
) -> sa_orm.Query[models.Booking]:
    VenueOffererAddress = sa_orm.aliased(offerers_models.OffererAddress)
    VenueAddress = sa_orm.aliased(Address)
    bookings_query = (
        db.session.query(models.Booking)
        .join(models.Booking.stock)
        .join(offers_models.Stock.offer)
        .join(models.Booking.venue, isouter=True)
        .outerjoin(offers_models.Offer.offererAddress)
        .outerjoin(offerers_models.OffererAddress.address)
        .join(VenueOffererAddress, offerers_models.Venue.offererAddress)
        .join(VenueAddress, VenueOffererAddress.address)
    )
    timezone_column = sa.func.coalesce(Address.timezone, VenueAddress.timezone)
    for join_key, *join_conditions in extra_joins:
        if join_conditions:
            bookings_query = bookings_query.join(join_key, *join_conditions, isouter=True)
        else:
            bookings_query = bookings_query.join(join_key, isouter=True)

    if period:
        date_column_to_filter_on = BOOKING_DATE_STATUS_MAPPING[status_filter or models.BookingStatusFilter.BOOKED]

        datetime_period_by_timezones = offerers_repository.convert_date_period_to_datetime_period_for_timezones(
            period,
            pro_user_id,
            offer_id=offer_id,
            offerer_address_id=offerer_address_id,
        )

        if len(datetime_period_by_timezones) == 1:  # ie. all bookings are on a single timezone
            [(_, datetime_period)] = datetime_period_by_timezones.items()
            bookings_query = bookings_query.filter(date_column_to_filter_on.between(*datetime_period, symmetric=True))
        else:  # ie. bookings are dispatched on several timezones
            bookings_query = bookings_query.filter(
                sa.or_(
                    *[
                        sa.and_(
                            timezone_column == timezone,
                            date_column_to_filter_on.between(*datetime_period, symmetric=True),
                        )
                        for timezone, datetime_period in datetime_period_by_timezones.items()
                    ]
                )
            )
    if venue_ids is not None:
        bookings_query = bookings_query.filter(models.Booking.venueId.in_(venue_ids))

    if offer_id is not None:
        bookings_query = bookings_query.filter(offers_models.Stock.offerId == offer_id)

    if offerer_address_id:
        bookings_query = bookings_query.filter(offers_models.Offer.offererAddressId == offerer_address_id)

    if event_date:
        bookings_query = bookings_query.filter(
            field_to_venue_timezone(offers_models.Stock.beginningDatetime, timezone_column) == event_date
        )
    if offerer_address_id:
        bookings_query = bookings_query.filter(offerers_models.OffererAddress.id == offerer_address_id)
    return bookings_query


def _get_filtered_bookings_count(
    *,
    pro_user_id: int,
    venue_id: int,
    period: tuple[date, date] | None = None,
    status_filter: models.BookingStatusFilter | None = None,
    event_date: date | None = None,
    offer_id: int | None = None,
    offerer_address_id: int | None = None,
) -> int:
    bookings = (
        _get_filtered_bookings_query(
            pro_user_id=pro_user_id,
            venue_ids=[venue_id],
            period=period,
            status_filter=status_filter,
            event_date=event_date,
            offer_id=offer_id,
            offerer_address_id=offerer_address_id,
        ).with_entities(models.Booking.id, models.Booking.quantity)
    ).cte()
    # We really want total quantities here (and not the number of bookings),
    # since we'll build two rows for each "duo" bookings later.
    bookings_count = db.session.query(sa.func.coalesce(sa.func.sum(bookings.c.quantity), 0))
    return bookings_count.scalar()


def get_filtered_booking_report(
    *,
    pro_user_id: int,
    venue_ids: list[int],
    period: tuple[date, date] | None,
    status_filter: models.BookingStatusFilter | None,
    event_date: date | None = None,
    offer_id: int | None = None,
    offerer_address_id: int | None = None,
) -> sa_orm.Query:
    VenueOffererAddress = sa_orm.aliased(offerers_models.OffererAddress)
    VenueAddress = sa_orm.aliased(Address)

    with_entities: tuple[typing.Any, ...] = (
        offerers_models.Venue.publicName.label("venueName"),
        offers_models.Offer.name.label("offerName"),
        offers_models.Stock.beginningDatetime.label("stockBeginningDatetime"),
        offers_models.Stock.offerId,
        offers_models.Offer.ean,
        User.firstName.label("beneficiaryFirstName"),
        User.lastName.label("beneficiaryLastName"),
        User.email.label("beneficiaryEmail"),
        User.phoneNumber.label("beneficiaryPhoneNumber"),
        User.postalCode.label("beneficiaryPostalCode"),
        models.Booking.id,
        models.Booking.token,
        models.Booking.priceCategoryLabel,
        models.Booking.amount,
        models.Booking.quantity,
        models.Booking.status,
        models.Booking.dateCreated.label("bookedAt"),
        models.Booking.dateUsed.label("usedAt"),
        models.Booking.reimbursementDate.label("reimbursedAt"),
        models.Booking.cancellationDate.label("cancelledAt"),
        models.Booking.isExternal.label("isExternal"),
        models.Booking.isConfirmed,
        offerers_models.Offerer.is_caledonian,
        # `get_batch` function needs a field called exactly `id` to work,
        # the label prevents SA from using a bad (prefixed) label for this field
        models.Booking.id.label("id"),
        models.Booking.userId,
        Address.departmentCode.label("offerDepartmentCode"),
        VenueAddress.departmentCode.label("venueDepartmentCode"),
        # TODO(OA): no more need to publicName here since the offer OA has a label
        sa.func.coalesce(
            sa.func.nullif(offerers_models.OffererAddress.label, ""), offerers_models.Venue.publicName
        ).label("locationName"),
        Address.street.label("locationStreet"),
        Address.postalCode.label("locationPostalCode"),
        Address.city.label("locationCity"),
    )

    bookings_query = _get_filtered_bookings_query(
        pro_user_id=pro_user_id,
        venue_ids=venue_ids,
        period=period,
        status_filter=status_filter,
        event_date=event_date,
        offer_id=offer_id,
        offerer_address_id=offerer_address_id,
        extra_joins=(
            (models.Booking.offerer,),
            (offers_models.Stock.offer,),
            (models.Booking.user,),
            (offers_models.Offer.offererAddress,),
            (offerers_models.OffererAddress.address,),
            (VenueOffererAddress, offerers_models.Venue.offererAddress),
            (VenueAddress, VenueOffererAddress.address),
        ),
    ).with_entities(*with_entities)

    return bookings_query


def _get_filtered_booking_pro(
    *,
    pro_user_id: int,
    venue_id: int,
    period: tuple[date, date] | None = None,
    status_filter: models.BookingStatusFilter | None = None,
    event_date: date | None = None,
    offer_id: int | None = None,
    offerer_address_id: int | None = None,
) -> sa_orm.Query:
    VenueOffererAddress = sa_orm.aliased(offerers_models.OffererAddress)
    VenueAddress = sa_orm.aliased(Address)

    with_entities: tuple[typing.Any, ...] = (
        models.Booking.token.label("bookingToken"),
        models.Booking.dateCreated.label("bookedAt"),
        models.Booking.quantity,
        models.Booking.amount.label("bookingAmount"),
        models.Booking.priceCategoryLabel,
        models.Booking.dateUsed.label("usedAt"),
        models.Booking.cancellationDate.label("cancelledAt"),
        models.Booking.cancellationLimitDate,
        models.Booking.status,
        models.Booking.reimbursementDate.label("reimbursedAt"),
        models.Booking.isExternal.label("isExternal"),
        models.Booking.isConfirmed,
        offers_models.Offer.name.label("offerName"),
        offers_models.Offer.id.label("offerId"),
        offers_models.Offer.ean.label("offerEan"),
        User.firstName.label("beneficiaryFirstname"),
        User.lastName.label("beneficiaryLastname"),
        User.email.label("beneficiaryEmail"),
        User.phoneNumber.label("beneficiaryPhoneNumber"),
        offers_models.Stock.beginningDatetime.label("stockBeginningDatetime"),
        models.Booking.stockId,
        Address.departmentCode.label("offerDepartmentCode"),
        VenueAddress.departmentCode.label("venueDepartmentCode"),
    )

    bookings_query = _get_filtered_bookings_query(
        pro_user_id=pro_user_id,
        venue_ids=[venue_id],
        period=period,
        status_filter=status_filter,
        event_date=event_date,
        offer_id=offer_id,
        offerer_address_id=offerer_address_id,
        extra_joins=(
            (offers_models.Stock.offer,),
            (models.Booking.user,),
            (offers_models.Offer.offererAddress,),
            (offerers_models.OffererAddress.address,),
            (VenueOffererAddress, offerers_models.Venue.offererAddress),
            (VenueAddress, VenueOffererAddress.address),
        ),
    ).with_entities(*with_entities)

    return bookings_query


def get_soon_expiring_bookings(expiration_days_delta: int) -> typing.Generator[models.Booking]:
    """Find bookings expiring in exactly `expiration_days_delta` days"""
    query = (
        db.session.query(models.Booking)
        .options(
            sa_orm.contains_eager(models.Booking.stock)
            .load_only(offers_models.Stock.id)
            .contains_eager(offers_models.Stock.offer)
            .load_only(offers_models.Offer.subcategoryId)
        )
        .join(models.Booking.stock)
        .join(offers_models.Stock.offer)
        .filter_by(canExpire=True)
        .filter(models.Booking.status == models.BookingStatus.CONFIRMED)
        .yield_per(1_000)
    )

    delta = timedelta(days=expiration_days_delta)
    for booking in query:
        expiration_date = booking.expirationDate
        if expiration_date and expiration_date.date() == date.today() + delta:
            yield booking


def venues_have_bookings(*venues: offerers_models.Venue) -> bool:
    """At least one venue which has email as bookingEmail has at least one non-cancelled booking"""
    return db.session.query(
        db.session.query(models.Booking)
        .filter(
            models.Booking.venueId.in_([venue.id for venue in venues]),
            models.Booking.status != models.BookingStatus.CANCELLED,
        )
        .exists()
    ).scalar()


def user_has_bookings(user: User) -> bool:
    bookings_query = (
        db.session.query(models.Booking).join(models.Booking.offerer).join(offerers_models.Offerer.UserOfferers)
    )
    return db.session.query(bookings_query.filter(offerers_models.UserOfferer.userId == user.id).exists()).scalar()


def offerer_has_ongoing_bookings(offerer_id: int) -> bool:
    return db.session.query(
        db.session.query(models.Booking)
        .filter(
            models.Booking.offererId == offerer_id,
            models.Booking.status == models.BookingStatus.CONFIRMED,
        )
        .exists()
    ).scalar()


def find_individual_bookings_event_happening_tomorrow_query() -> list[models.Booking]:
    tomorrow = date_utils.get_naive_utc_now() + timedelta(days=1)
    tomorrow_min = datetime.combine(tomorrow, time.min)
    tomorrow_max = datetime.combine(tomorrow, time.max)

    return (
        db.session.query(models.Booking)
        .join(
            models.Booking.user,
        )
        .join(models.Booking.stock)
        .join(offers_models.Stock.offer)
        .join(offers_models.Offer.venue)
        .outerjoin(models.Booking.activationCode)
        .outerjoin(offers_models.Offer.criteria)
        .filter(
            offers_models.Stock.beginningDatetime >= tomorrow_min, offers_models.Stock.beginningDatetime <= tomorrow_max
        )
        .filter(offers_models.Offer.isEvent)
        .filter(sa.not_(offers_models.Offer.hasUrl))
        .filter(models.Booking.status != models.BookingStatus.CANCELLED)
        .options(sa_orm.contains_eager(models.Booking.user))
        .options(sa_orm.contains_eager(models.Booking.activationCode))
        .options(
            sa_orm.contains_eager(models.Booking.stock)
            .contains_eager(offers_models.Stock.offer)
            .options(
                sa_orm.contains_eager(offers_models.Offer.venue),
                sa_orm.contains_eager(offers_models.Offer.criteria),
                sa_orm.joinedload(offers_models.Offer.offererAddress)
                .load_only(offerers_models.OffererAddress.label)
                .joinedload(offerers_models.OffererAddress.address),
            )
        )
        .all()
    )


def get_external_bookings_by_cinema_id_and_barcodes(
    venueIdAtOfferProvider: str, barcodes: list[str]
) -> list[models.ExternalBooking]:
    return (
        db.session.query(models.ExternalBooking)
        .join(models.Booking)
        .join(VenueProvider, models.Booking.venueId == VenueProvider.venueId)
        .filter(VenueProvider.venueIdAtOfferProvider == venueIdAtOfferProvider)
        .filter(models.ExternalBooking.barcode.in_(barcodes))
        .all()
    )

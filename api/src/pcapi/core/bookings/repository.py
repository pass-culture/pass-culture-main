import csv
from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta
from io import BytesIO
from io import StringIO
import typing
from typing import Iterable

from flask_sqlalchemy import BaseQuery
import sqlalchemy as sa
from sqlalchemy.orm import contains_eager
from sqlalchemy.orm import joinedload
import xlsxwriter
from xlsxwriter.format import Format
from xlsxwriter.worksheet import Worksheet

from pcapi.core.bookings import constants
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingCancellationReasons
from pcapi.core.bookings.models import BookingExportType
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.bookings.models import BookingStatusFilter
from pcapi.core.bookings.models import ExternalBooking
from pcapi.core.bookings.utils import convert_booking_dates_utc_to_venue_timezone
from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.educational import models as educational_models
from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.models import UserOfferer
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.core.offers.serialize import serialize_offer_type_educational_or_individual
from pcapi.core.providers.models import VenueProvider
from pcapi.core.users.models import User
from pcapi.domain.booking_recap import utils as booking_recap_utils
from pcapi.models import db
from pcapi.utils.token import random_token


BOOKING_STATUS_LABELS = {
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


# FIXME (Gautier, 03-25-2022): also used in collective_booking. SHould we move it to core or some other place?
def field_to_venue_timezone(field: typing.Any) -> sa.cast:
    return sa.cast(sa.func.timezone(Venue.timezone, sa.func.timezone("UTC", field)), sa.Date)


def _get_bookings_export_entities() -> tuple:
    entities = (
        Venue.common_name.label("venueName"),  # type: ignore[attr-defined]
        Venue.departementCode.label("venueDepartmentCode"),
        Offerer.postalCode.label("offererPostalCode"),
        Offer.name.label("offerName"),
        Stock.beginningDatetime.label("stockBeginningDatetime"),
        Stock.offerId,
        Offer.extraData["ean"].label("ean"),
        User.firstName.label("beneficiaryFirstName"),
        User.lastName.label("beneficiaryLastName"),
        User.email.label("beneficiaryEmail"),
        User.phoneNumber.label("beneficiaryPhoneNumber"),  # type: ignore[attr-defined]
        User.postalCode.label("beneficiaryPostalCode"),
        Booking.id,
        Booking.token,
        Booking.priceCategoryLabel,
        Booking.amount,
        Booking.quantity,
        Booking.status,
        Booking.dateCreated.label("bookedAt"),
        Booking.dateUsed.label("usedAt"),
        Booking.reimbursementDate.label("reimbursedAt"),
        Booking.cancellationDate.label("cancelledAt"),
        Booking.isExternal.label("isExternal"),  # type: ignore[attr-defined]
        Booking.isConfirmed,
        # `get_batch` function needs a field called exactly `id` to work,
        # the label prevents SA from using a bad (prefixed) label for this field
        Booking.id.label("id"),
        Booking.userId,
    )
    return entities


def _get_filtered_bookings_query(
    pro_user: User,
    booking_period: tuple[date, date] | None = None,
    status_filter: BookingStatusFilter | None = None,
    event_date: date | None = None,
    venue_id: int | None = None,
    offer_id: int | None = None,
    extra_joins: Iterable[sa.Column] | None = None,
) -> BaseQuery:
    extra_joins = extra_joins or tuple()

    bookings_query = (
        Booking.query.join(Booking.offerer)
        .join(Offerer.UserOfferers)
        .join(Booking.stock)
        .join(Booking.externalBookings, isouter=True)
        .join(Booking.venue, isouter=True)
    )
    for join_key in extra_joins:
        bookings_query = bookings_query.join(join_key, isouter=True)

    if not pro_user.has_admin_role:
        bookings_query = bookings_query.filter(UserOfferer.user == pro_user)

    bookings_query = bookings_query.filter(UserOfferer.isValidated)

    if booking_period:
        period_attribut_filter = (
            BOOKING_DATE_STATUS_MAPPING[status_filter]
            if status_filter
            else BOOKING_DATE_STATUS_MAPPING[BookingStatusFilter.BOOKED]
        )

        bookings_query = bookings_query.filter(
            field_to_venue_timezone(period_attribut_filter).between(*booking_period, symmetric=True)
        )

    if venue_id is not None:
        bookings_query = bookings_query.filter(Booking.venueId == venue_id)

    if offer_id is not None:
        bookings_query = bookings_query.filter(Stock.offerId == offer_id)

    if event_date:
        bookings_query = bookings_query.filter(field_to_venue_timezone(Stock.beginningDatetime) == event_date)
    return bookings_query


def _get_filtered_booking_report(
    pro_user: User,
    booking_period: tuple[date, date] | None,
    status_filter: BookingStatusFilter | None,
    event_date: date | None = None,
    venue_id: int | None = None,
    offer_id: int | None = None,
) -> BaseQuery:
    bookings_query = (
        _get_filtered_bookings_query(
            pro_user,
            booking_period,
            status_filter,
            event_date,
            venue_id,
            offer_id,
            extra_joins=(Stock.offer, Booking.user),
        )
        .with_entities(*_get_bookings_export_entities())
        .distinct(Booking.id)
    )

    return bookings_query


def _get_filtered_bookings_count(
    pro_user: User,
    booking_period: tuple[date, date] | None = None,
    status_filter: BookingStatusFilter | None = None,
    event_date: date | None = None,
    venue_id: int | None = None,
    offer_id: int | None = None,
) -> int:
    bookings = (
        _get_filtered_bookings_query(pro_user, booking_period, status_filter, event_date, venue_id, offer_id)
        .with_entities(Booking.id, Booking.quantity)
        .distinct(Booking.id)
    ).cte()
    # We really want total quantities here (and not the number of bookings),
    # since we'll build two rows for each "duo" bookings later.
    bookings_count = db.session.query(sa.func.coalesce(sa.func.sum(bookings.c.quantity), 0))
    return bookings_count.scalar()


def _get_filtered_booking_pro(
    pro_user: User,
    booking_period: tuple[date, date] | None = None,
    status_filter: BookingStatusFilter | None = None,
    event_date: date | None = None,
    venue_id: int | None = None,
    offer_id: int | None = None,
) -> BaseQuery:
    bookings_query = (
        _get_filtered_bookings_query(
            pro_user,
            booking_period,
            status_filter,
            event_date,
            venue_id,
            offer_id,
            extra_joins=(
                Stock.offer,
                Booking.user,
            ),
        )
        .with_entities(
            Booking.token.label("bookingToken"),
            Booking.dateCreated.label("bookedAt"),
            Booking.quantity,
            Booking.amount.label("bookingAmount"),
            Booking.priceCategoryLabel,
            Booking.dateUsed.label("usedAt"),
            Booking.cancellationDate.label("cancelledAt"),
            Booking.cancellationLimitDate,
            Booking.status,
            Booking.reimbursementDate.label("reimbursedAt"),
            Booking.isExternal.label("isExternal"),  # type: ignore[attr-defined]
            Booking.isConfirmed,
            Offer.name.label("offerName"),
            Offer.id.label("offerId"),
            Offer.extraData["ean"].label("offerEan"),
            User.firstName.label("beneficiaryFirstname"),
            User.lastName.label("beneficiaryLastname"),
            User.email.label("beneficiaryEmail"),
            User.phoneNumber.label("beneficiaryPhoneNumber"),  # type: ignore[attr-defined]
            Stock.beginningDatetime.label("stockBeginningDatetime"),
            Booking.stockId,
            Venue.departementCode.label("venueDepartmentCode"),
            Offerer.postalCode.label("offererPostalCode"),
        )
        .distinct(Booking.id)
    )

    return bookings_query


def _create_export_query(offer_id: int, event_beginning_date: date, validated: bool = False) -> BaseQuery:
    query = (
        Booking.query.join(Booking.offerer)
        .join(Booking.user)
        .join(Offerer.UserOfferers)
        .join(Booking.venue)
        .join(Booking.stock)
        .join(Stock.offer)
        .filter(Stock.offerId == offer_id, field_to_venue_timezone(Stock.beginningDatetime) == event_beginning_date)
        .order_by(Booking.id)
        .with_entities(*_get_bookings_export_entities())
        .distinct(Booking.id)
    )
    if validated:
        query = query.filter(
            sa.or_(
                sa.and_(Booking.isConfirmed, Booking.status != BookingStatus.CANCELLED),  # type: ignore[type-var]
                Booking.status == BookingStatus.USED,
            )
        )
    return query


def _get_booking_status(status: BookingStatus | str, is_confirmed: bool) -> str:
    if is_confirmed and status == BookingStatus.CONFIRMED:
        status = "confirmed"
    return BOOKING_STATUS_LABELS[status]


def _build_export_columns(booking: Booking, duo_column: str, is_csv: bool) -> list[dict]:
    booking_token = booking_recap_utils.get_booking_token(
        booking.token,
        booking.status,
        bool(booking.isExternal),
        booking.stockBeginningDatetime,
    )
    price_category_label = booking.priceCategoryLabel
    beneficiary_postal_code = booking.beneficiaryPostalCode
    stock_beginning_datetime = convert_booking_dates_utc_to_venue_timezone(booking.stockBeginningDatetime, booking)
    booked_at = convert_booking_dates_utc_to_venue_timezone(booking.bookedAt, booking)
    used_at = convert_booking_dates_utc_to_venue_timezone(booking.usedAt, booking)
    reimbursed_at = convert_booking_dates_utc_to_venue_timezone(booking.reimbursedAt, booking)
    if is_csv:
        price_category_label = price_category_label or ""
        beneficiary_postal_code = beneficiary_postal_code or ""
    else:
        stock_beginning_datetime = str(stock_beginning_datetime)  # type: ignore[assignment]
        booked_at = str(booked_at)  # type: ignore[assignment]
        used_at = str(used_at)  # type: ignore[assignment]
        reimbursed_at = str(reimbursed_at)  # type: ignore[assignment]
    columns = [
        {"value": booking.venueName},
        {"value": booking.offerName},
        {"value": stock_beginning_datetime},
        {"value": booking.ean},
        {"value": f"{booking.beneficiaryLastName} {booking.beneficiaryFirstName}"},
        {"value": booking.beneficiaryEmail},
        {"value": booking.beneficiaryPhoneNumber},
        {"value": booked_at},
        {"value": used_at},
        {"value": booking_token},
        {"value": price_category_label},
        {"value": booking.amount, "type": "currency"},
        {"value": _get_booking_status(booking.status, bool(booking.isConfirmed))},
        {"value": reimbursed_at},
        {"value": serialize_offer_type_educational_or_individual(offer_is_educational=False)},
        {"value": beneficiary_postal_code},
        {"value": duo_column},
    ]
    return columns


def _write_csv_row(writer: typing.Any, booking: Booking, duo_column: str) -> None:
    columns = _build_export_columns(booking, duo_column, True)
    writer.writerow([column["value"] for column in columns])


def _write_bookings_to_csv(query: BaseQuery, duplicate_duo: bool = True) -> str:
    output = StringIO()
    writer = csv.writer(output, dialect=csv.excel, delimiter=";", quoting=csv.QUOTE_NONNUMERIC)
    writer.writerow(constants.BOOKING_EXPORT_HEADERS)
    for booking in query.yield_per(1000):
        if booking.quantity == constants.DUO_QUANTITY:
            if duplicate_duo:
                _write_csv_row(writer, booking, "DUO 1")
                _write_csv_row(writer, booking, "DUO 2")
            else:
                _write_csv_row(writer, booking, "Oui")
        else:
            _write_csv_row(writer, booking, "Non")

    return output.getvalue()


def _write_excel_row(
    worksheet: Worksheet, row: int, booking: Booking, currency_format: Format, duo_column: str
) -> None:
    columns = _build_export_columns(booking, duo_column, False)
    for i, column in enumerate(columns):
        if column.get("type") == "currency":
            write_args: tuple = (currency_format,)
        else:
            write_args = tuple()
        worksheet.write(row, i, column["value"], *write_args)


def _write_bookings_to_excel(query: BaseQuery, duplicate_duo: bool = True) -> bytes:
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)

    bold = workbook.add_format({"bold": 1})
    currency_format = workbook.add_format({"num_format": "###0.00[$€-fr-FR]"})
    col_width = 18

    worksheet = workbook.add_worksheet()

    row = 0
    for col_num, title in enumerate(constants.BOOKING_EXPORT_HEADERS):
        worksheet.write(row, col_num, title, bold)
        worksheet.set_column(col_num, col_num, col_width)

    row = 1
    for booking in query.yield_per(1000):
        if booking.quantity == constants.DUO_QUANTITY:
            if duplicate_duo:
                _write_excel_row(worksheet, row, booking, currency_format, "DUO 1")
                row += 1
                _write_excel_row(worksheet, row, booking, currency_format, "DUO 2")
            else:
                _write_excel_row(worksheet, row, booking, currency_format, "Oui")
        else:
            _write_excel_row(worksheet, row, booking, currency_format, "Non")
        row += 1

    workbook.close()
    return output.getvalue()


def export_bookings_by_offer_id(
    offer_id: int, event_beginning_date: date, export_type: BookingExportType, validated: bool = False
) -> str | bytes:
    query = _create_export_query(offer_id, event_beginning_date, validated=validated)
    if export_type == BookingExportType.EXCEL:
        return _write_bookings_to_excel(query)
    return _write_bookings_to_csv(query)


def _duplicate_booking_when_quantity_is_two(bookings_recap_query: BaseQuery) -> BaseQuery:
    return bookings_recap_query.union_all(bookings_recap_query.filter(Booking.quantity == constants.DUO_QUANTITY))


def get_export(
    user: User,
    booking_period: tuple[date, date] | None = None,
    status_filter: BookingStatusFilter | None = BookingStatusFilter.BOOKED,
    event_date: date | None = None,
    venue_id: int | None = None,
    offer_id: int | None = None,
    export_type: BookingExportType | None = BookingExportType.CSV,
) -> str | bytes:
    bookings_query = _get_filtered_booking_report(
        pro_user=user,
        booking_period=booking_period,
        status_filter=status_filter,
        event_date=event_date,
        venue_id=venue_id,
        offer_id=offer_id,
    )
    bookings_query = _duplicate_booking_when_quantity_is_two(bookings_query)
    if export_type == BookingExportType.EXCEL:
        return _write_bookings_to_excel(bookings_query, duplicate_duo=False)
    return _write_bookings_to_csv(bookings_query, duplicate_duo=False)


def find_by_pro_user(
    user: User,
    booking_period: tuple[date, date] | None = None,
    status_filter: BookingStatusFilter | None = None,
    event_date: date | None = None,
    venue_id: int | None = None,
    offer_id: int | None = None,
    page: int = 1,
    per_page_limit: int = 1000,
) -> tuple[BaseQuery, int]:
    total_bookings_recap = _get_filtered_bookings_count(
        user,
        booking_period,
        status_filter=status_filter,
        event_date=event_date,
        venue_id=venue_id,
        offer_id=offer_id,
    )

    bookings_query = _get_filtered_booking_pro(
        pro_user=user,
        booking_period=booking_period,
        status_filter=status_filter,
        event_date=event_date,
        venue_id=venue_id,
        offer_id=offer_id,
    )
    bookings_query = _duplicate_booking_when_quantity_is_two(bookings_query)
    bookings_query = (
        bookings_query.order_by(sa.text('"bookedAt" DESC')).offset((page - 1) * per_page_limit).limit(per_page_limit)
    )

    return bookings_query, total_bookings_recap


def find_ongoing_bookings_by_stock(stock_id: int) -> list[Booking]:
    return Booking.query.filter(
        Booking.stockId == stock_id,
        Booking.status == BookingStatus.CONFIRMED,
    ).all()


def find_not_cancelled_bookings_by_stock(stock_id: int) -> list[Booking]:
    return Booking.query.filter(
        Booking.stockId == stock_id,
        Booking.status != BookingStatus.CANCELLED,
    ).all()


def find_expiring_individual_bookings_query() -> BaseQuery:
    today_at_midnight = datetime.combine(date.today(), time.min)
    return (
        Booking.query.join(Stock)
        .join(Offer)
        .filter(
            Booking.status == BookingStatus.CONFIRMED,
            Offer.canExpire,
            sa.case(
                (
                    Offer.subcategoryId == subcategories.LIVRE_PAPIER.id,
                    (Booking.dateCreated + constants.BOOKS_BOOKINGS_AUTO_EXPIRY_DELAY) <= today_at_midnight,
                ),
                else_=((Booking.dateCreated + constants.BOOKINGS_AUTO_EXPIRY_DELAY) <= today_at_midnight),
            ),
        )
    )


def find_soon_to_be_expiring_individual_bookings_ordered_by_user(given_date: date | None = None) -> BaseQuery:
    given_date = given_date or date.today()
    books_expiring_date = datetime.combine(given_date, time.min) + constants.BOOKS_BOOKINGS_EXPIRY_NOTIFICATION_DELAY
    other_expiring_date = datetime.combine(given_date, time.min) + constants.BOOKINGS_EXPIRY_NOTIFICATION_DELAY
    books_window = (
        datetime.combine(books_expiring_date, time.min),
        datetime.combine(books_expiring_date, time.max),
    )
    rest_window = (
        datetime.combine(other_expiring_date, time.min),
        datetime.combine(other_expiring_date, time.max),
    )
    return (
        Booking.query.join(Stock)
        .join(Offer)
        .filter(
            Booking.status == BookingStatus.CONFIRMED,
            Offer.canExpire,
            sa.case(
                (
                    Offer.subcategoryId == subcategories.LIVRE_PAPIER.id,
                    ((Booking.dateCreated + constants.BOOKS_BOOKINGS_AUTO_EXPIRY_DELAY).between(*books_window)),
                ),
                else_=(Booking.dateCreated + constants.BOOKINGS_AUTO_EXPIRY_DELAY).between(*rest_window),
            ),
        )
        .order_by(Booking.userId)
    )


def _token_exists(token: str) -> bool:
    return db.session.query(Booking.query.filter_by(token=token.upper()).exists()).scalar()


def generate_booking_token() -> str:
    for _ in range(100):
        token = random_token()
        if not _token_exists(token):
            return token
    raise ValueError("Could not generate new booking token")


def _is_expired(expired_on: date | None = None) -> tuple:
    expired_on = expired_on or date.today()
    expired_on_min = datetime.combine(expired_on, time.min)
    expired_on_max = datetime.combine(expired_on, time.max)
    return (
        Booking.status == BookingStatus.CANCELLED,
        Booking.cancellationDate >= expired_on_min,
        Booking.cancellationDate <= expired_on_max,
        Booking.cancellationReason == BookingCancellationReasons.EXPIRED,
    )


def find_user_ids_with_expired_individual_bookings(expired_on: date | None = None) -> list[int]:
    return [user_id for user_id, in db.session.query(User.id).join(Booking).filter(*_is_expired(expired_on)).all()]


def get_expired_individual_bookings_for_user(user: User, expired_on: date | None = None) -> list[Booking]:
    return Booking.query.filter(Booking.user == user).filter(*_is_expired(expired_on)).all()


def find_expired_individual_bookings_ordered_by_offerer(expired_on: date | None = None) -> list[Booking]:
    return Booking.query.filter(*_is_expired(expired_on)).order_by(Booking.offererId).all()


def get_active_bookings_quantity_for_venue(venue_id: int) -> int:
    # Stock.dnBookedQuantity cannot be used here because we exclude used/confirmed bookings.
    active_individual_bookings_quantity = (
        Booking.query.join(
            Stock,
            Booking.stock,
        )
        .filter(
            Booking.venueId == venue_id,
            Booking.status == BookingStatus.CONFIRMED,
            sa.not_(Booking.isConfirmed),
        )
        .with_entities(sa.func.coalesce(sa.func.sum(Booking.quantity), 0))
        .scalar()
    )

    active_collective_bookings_quantity = (
        educational_models.CollectiveBooking.query.join(
            educational_models.CollectiveStock,
            educational_models.CollectiveBooking.collectiveStock,
        )
        .filter(
            educational_models.CollectiveBooking.venueId == venue_id,
            sa.or_(
                sa.and_(
                    educational_models.CollectiveBooking.status == educational_models.CollectiveBookingStatus.PENDING,
                    sa.not_(educational_models.CollectiveStock.hasBookingLimitDatetimePassed),
                ),
                sa.and_(
                    educational_models.CollectiveBooking.status == educational_models.CollectiveBookingStatus.CONFIRMED,
                    sa.not_(educational_models.CollectiveBooking.isConfirmed),
                ),
            ),
        )
        .with_entities(sa.func.coalesce(sa.func.sum(1), 0))
        .scalar()
    )

    return active_individual_bookings_quantity + active_collective_bookings_quantity


def get_validated_bookings_quantity_for_venue(venue_id: int) -> int:
    validated_individual_bookings_quantity = (
        Booking.query.filter(
            Booking.venueId == venue_id,
            Booking.status != BookingStatus.CANCELLED,
            sa.or_(  # type: ignore[type-var]
                Booking.is_used_or_reimbursed,
                Booking.isConfirmed,
            ),
        )
        .with_entities(sa.func.coalesce(sa.func.sum(Booking.quantity), 0))
        .scalar()
    )

    validated_collective_bookings_quantity = (
        educational_models.CollectiveBooking.query.filter(
            educational_models.CollectiveBooking.venueId == venue_id,
            educational_models.CollectiveBooking.status != educational_models.CollectiveBookingStatus.CANCELLED,
            educational_models.CollectiveBooking.status != educational_models.CollectiveBookingStatus.PENDING,
            sa.or_(  # type: ignore[type-var]
                educational_models.CollectiveBooking.is_used_or_reimbursed,
                educational_models.CollectiveBooking.isConfirmed,
            ),
        )
        .with_entities(sa.func.coalesce(sa.func.sum(1), 0))
        .scalar()
    )

    return validated_individual_bookings_quantity + validated_collective_bookings_quantity


def find_cancellable_bookings_by_offerer(offerer_id: int) -> list[Booking]:
    return Booking.query.filter(
        Booking.offererId == offerer_id,
        Booking.status == BookingStatus.CONFIRMED,
    ).all()


def get_bookings_from_deposit(deposit_id: int) -> list[Booking]:
    return (
        Booking.query.filter(
            Booking.depositId == deposit_id,
            Booking.status != BookingStatus.CANCELLED,
        )
        .options(joinedload(Booking.stock).joinedload(Stock.offer))
        .all()
    )


def get_soon_expiring_bookings(expiration_days_delta: int) -> typing.Generator[Booking, None, None]:
    """Find bookings expiring in exactly `expiration_days_delta` days"""
    dt = date.today() + timedelta(days=expiration_days_delta)
    query = (
        Booking.query.join(Booking.stock)
        .join(Stock.offer)
        .filter(
            Offer.canExpire,
            Booking.status == BookingStatus.CONFIRMED,
        )
        .options(
            contains_eager(Booking.stock).load_only(Stock.id).contains_eager(Stock.offer).load_only(Offer.subcategoryId)
        )
    )
    for booking in query.yield_per(1000):
        expiration_date = booking.expirationDate
        if expiration_date and expiration_date.date() == dt:
            yield booking


def venues_have_bookings(*venues: Venue) -> bool:
    """At least one venue which has email as bookingEmail has at least one non-cancelled booking"""
    return db.session.query(
        Booking.query.filter(
            Booking.venueId.in_([venue.id for venue in venues]), Booking.status != BookingStatus.CANCELLED
        ).exists()
    ).scalar()


def user_has_bookings(user_id: int) -> bool:
    return db.session.query(
        Booking.query.join(Booking.offerer).join(Offerer.UserOfferers).filter(UserOfferer.userId == user_id).exists()
    ).scalar()


def offerer_has_ongoing_bookings(offerer_id: int) -> bool:
    return db.session.query(
        Booking.query.filter(
            Booking.offererId == offerer_id,
            Booking.status == BookingStatus.CONFIRMED,
        ).exists()
    ).scalar()


def find_individual_bookings_event_happening_tomorrow() -> list[Booking]:
    tomorrow = datetime.utcnow() + timedelta(days=1)
    tomorrow_min = datetime.combine(tomorrow, time.min)
    tomorrow_max = datetime.combine(tomorrow, time.max)
    return (
        Booking.query.join(Booking.user)
        .join(Booking.stock)
        .join(Stock.offer)
        .join(Offer.venue)
        .outerjoin(Booking.activationCode)
        .outerjoin(Offer.criteria)
        .filter(
            Stock.beginningDatetime >= tomorrow_min,
            Stock.beginningDatetime <= tomorrow_max,
            Offer.isEvent,
            sa.not_(Offer.isDigital),
            Booking.status != BookingStatus.CANCELLED,
        )
        .options(contains_eager(Booking.user))
        .options(contains_eager(Booking.activationCode))
        .options(
            contains_eager(Booking.stock)
            .contains_eager(Stock.offer)
            .options(
                contains_eager(Offer.venue),
                contains_eager(Offer.criteria),
            )
        )
        .all()
    )


def get_external_bookings_by_cinema_id_and_barcodes(cinema_id: str, barcodes: list[str]) -> list[ExternalBooking]:
    return (
        ExternalBooking.query.join(Booking)
        .join(VenueProvider, Booking.venueId == VenueProvider.venueId)
        .filter(
            VenueProvider.venueIdAtOfferProvider == cinema_id,
            ExternalBooking.barcode.in_(barcodes),
        )
        .all()
    )

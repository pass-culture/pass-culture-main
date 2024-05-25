import csv
from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta
from io import BytesIO
from io import StringIO
from operator import and_
import typing
from typing import Iterable

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
from pcapi.routes.serialization.bookings_recap_serialize import OfferType
from pcapi.utils.token import random_token


DUO_QUANTITY = 2


BOOKING_STATUS_LABELS = {
    BookingStatus.CONFIRMED: "réservé",
    BookingStatus.CANCELLED: "annulé",
    BookingStatus.USED: "validé",
    BookingStatus.REIMBURSED: "remboursé",
    "confirmed": "confirmé",
}

BOOKING_DATE_STATUS_MAPPING: dict[BookingStatusFilter, InstrumentedAttribute] = {
    BookingStatusFilter.BOOKED: Booking.dateCreated,
    BookingStatusFilter.VALIDATED: Booking.dateUsed,
    BookingStatusFilter.REIMBURSED: Booking.reimbursementDate,
}

BOOKING_EXPORT_HEADER = [
    "Lieu",
    "Nom de l’offre",
    "Date de l'évènement",
    "EAN",
    "Nom et prénom du bénéficiaire",
    "Email du bénéficiaire",
    "Téléphone du bénéficiaire",
    "Date et heure de réservation",
    "Date et heure de validation",
    "Contremarque",
    "Intitulé du tarif",
    "Prix de la réservation",
    "Statut de la contremarque",
    "Date et heure de remboursement",
    "Type d'offre",
    "Code postal du bénéficiaire",
    "Duo",
]


# FIXME (Gautier, 03-25-2022): also used in collective_booking. SHould we move it to core or some other place?
def field_to_venue_timezone(field: InstrumentedAttribute) -> cast:
    return cast(func.timezone(Venue.timezone, func.timezone("UTC", field)), Date)


def _get_filtered_bookings_query(
    pro_user: User,
    period: tuple[date, date] | None = None,
    status_filter: BookingStatusFilter | None = None,
    event_date: date | None = None,
    venue_id: int | None = None,
    offer_id: int | None = None,
    offer_type: OfferType | None = None,
    extra_joins: Iterable[Column] | None = None,
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

    if period:
        period_attribut_filter = (
            BOOKING_DATE_STATUS_MAPPING[status_filter]
            if status_filter
            else BOOKING_DATE_STATUS_MAPPING[BookingStatusFilter.BOOKED]
        )

        bookings_query = bookings_query.filter(
            field_to_venue_timezone(period_attribut_filter).between(*period, symmetric=True)
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
    period: tuple[date, date] | None,
    status_filter: BookingStatusFilter | None,
    event_date: date | None = None,
    venue_id: int | None = None,
    offer_id: int | None = None,
    offer_type: OfferType | None = None,
) -> str:
    bookings_query = (
        _get_filtered_bookings_query(
            pro_user,
            period,
            status_filter,
            event_date,
            venue_id,
            offer_id,
            offer_type,
            extra_joins=(Stock.offer, Booking.user),
        )
        .with_entities(
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
        .distinct(Booking.id)
    )

    return bookings_query


def _get_filtered_bookings_count(
    pro_user: User,
    period: tuple[date, date] | None = None,
    status_filter: BookingStatusFilter | None = None,
    event_date: date | None = None,
    venue_id: int | None = None,
    offer_id: int | None = None,
    offer_type: OfferType | None = None,
) -> int:
    bookings = (
        _get_filtered_bookings_query(pro_user, period, status_filter, event_date, venue_id, offer_id, offer_type)
        .with_entities(Booking.id, Booking.quantity)
        .distinct(Booking.id)
    ).cte()
    # We really want total quantities here (and not the number of bookings),
    # since we'll build two rows for each "duo" bookings later.
    bookings_count = db.session.query(func.coalesce(func.sum(bookings.c.quantity), 0))
    return bookings_count.scalar()


def _get_filtered_booking_pro(
    pro_user: User,
    period: tuple[date, date] | None = None,
    status_filter: BookingStatusFilter | None = None,
    event_date: date | None = None,
    venue_id: int | None = None,
    offer_id: int | None = None,
    offer_type: OfferType | None = None,
) -> BaseQuery:
    bookings_query = (
        _get_filtered_bookings_query(
            pro_user,
            period,
            status_filter,
            event_date,
            venue_id,
            offer_id,
            offer_type,
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


def _create_export_query(offer_id: int, event_beginning_date: date) -> BaseQuery:
    return (
        Booking.query.join(Booking.offerer)
        .join(Booking.user)
        .join(Offerer.UserOfferers)
        .join(Booking.venue)
        .join(Booking.stock)
        .join(Stock.offer)
        .filter(Stock.offerId == offer_id, field_to_venue_timezone(Stock.beginningDatetime) == event_beginning_date)
        .order_by(Booking.id)
        .with_entities(
            Booking.id.label("id"),
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
            Booking.userId,
        )
        .distinct(Booking.id)
    )


def _write_csv_row(csv_writer: typing.Any, booking: Booking, booking_duo_column: str) -> None:
    csv_writer.writerow(
        (
            booking.venueName,
            booking.offerName,
            convert_booking_dates_utc_to_venue_timezone(booking.stockBeginningDatetime, booking),
            booking.ean,
            f"{booking.beneficiaryLastName} {booking.beneficiaryFirstName}",
            booking.beneficiaryEmail,
            booking.beneficiaryPhoneNumber,
            convert_booking_dates_utc_to_venue_timezone(booking.bookedAt, booking),
            convert_booking_dates_utc_to_venue_timezone(booking.usedAt, booking),
            booking_recap_utils.get_booking_token(
                booking.token,
                booking.status,
                booking.isExternal,
                booking.stockBeginningDatetime,
            ),
            booking.priceCategoryLabel or "",
            booking.amount,
            _get_booking_status(booking.status, booking.isConfirmed),
            convert_booking_dates_utc_to_venue_timezone(booking.reimbursedAt, booking),
            serialize_offer_type_educational_or_individual(offer_is_educational=False),
            booking.beneficiaryPostalCode or "",
            booking_duo_column,
        )
    )


def _write_bookings_to_csv(query: BaseQuery) -> str:
    output = StringIO()
    writer = csv.writer(output, dialect=csv.excel, delimiter=";", quoting=csv.QUOTE_NONNUMERIC)
    writer.writerow(BOOKING_EXPORT_HEADER)
    for booking in query.yield_per(1000):
        if booking.quantity == DUO_QUANTITY:
            _write_csv_row(writer, booking, "DUO 1")
            _write_csv_row(writer, booking, "DUO 2")
        else:
            _write_csv_row(writer, booking, "Non")

    return output.getvalue()


def export_bookings_by_offer_id(
    offer_id: int, event_beginning_date: date, export_type: BookingExportType
) -> str | bytes:
    offer_bookings_query = _create_export_query(offer_id, event_beginning_date)
    if export_type == BookingExportType.EXCEL:
        return _write_bookings_to_excel(offer_bookings_query)
    return _write_bookings_to_csv(offer_bookings_query)


def export_validated_bookings_by_offer_id(
    offer_id: int, event_beginning_date: date, export_type: BookingExportType
) -> str | bytes:
    offer_validated_bookings_query = _create_export_query(offer_id, event_beginning_date)
    offer_validated_bookings_query = offer_validated_bookings_query.filter(
        or_(
            and_(Booking.isConfirmed, Booking.status != BookingStatus.CANCELLED),
            Booking.status == BookingStatus.USED,
        )
    )
    if export_type == BookingExportType.EXCEL:
        return _write_bookings_to_excel(offer_validated_bookings_query)
    return _write_bookings_to_csv(offer_validated_bookings_query)


def _duplicate_booking_when_quantity_is_two(bookings_recap_query: BaseQuery) -> BaseQuery:
    return bookings_recap_query.union_all(bookings_recap_query.filter(Booking.quantity == DUO_QUANTITY))


def get_export(
    user: User,
    booking_period: tuple[date, date] | None = None,
    status_filter: BookingStatusFilter | None = BookingStatusFilter.BOOKED,
    event_date: date | None = None,
    venue_id: int | None = None,
    offer_id: int | None = None,
    offer_type: OfferType | None = None,
    export_type: BookingExportType | None = BookingExportType.CSV,
) -> str | bytes:
    bookings_query = _get_filtered_booking_report(
        pro_user=user,
        period=booking_period,
        status_filter=status_filter,
        event_date=event_date,
        venue_id=venue_id,
        offer_id=offer_id,
        offer_type=offer_type,
    )
    bookings_query = _duplicate_booking_when_quantity_is_two(bookings_query)
    if export_type == BookingExportType.EXCEL:
        return _serialize_excel_report(bookings_query)
    return _serialize_csv_report(bookings_query)


def find_by_pro_user(
    user: User,
    booking_period: tuple[date, date] | None = None,
    status_filter: BookingStatusFilter | None = None,
    event_date: date | None = None,
    venue_id: int | None = None,
    offer_id: int | None = None,
    offer_type: OfferType | None = None,
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
        offer_type=offer_type,
    )

    bookings_query = _get_filtered_booking_pro(
        pro_user=user,
        period=booking_period,
        status_filter=status_filter,
        event_date=event_date,
        venue_id=venue_id,
        offer_type=offer_type,
        offer_id=offer_id,
    )
    bookings_query = _duplicate_booking_when_quantity_is_two(bookings_query)
    bookings_query = (
        bookings_query.order_by(text('"bookedAt" DESC')).offset((page - 1) * per_page_limit).limit(per_page_limit)
    )

    return bookings_query, total_bookings_recap


def find_ongoing_bookings_by_stock(stock_id: int) -> list[Booking]:
    return Booking.query.filter(
        Booking.stockId == stock_id,
        Booking.status == BookingStatus.CONFIRMED,
    ).all()


def find_not_cancelled_bookings_by_stock(stock: Stock) -> list[Booking]:
    return Booking.query.filter(Booking.stockId == stock.id, Booking.status != BookingStatus.CANCELLED).all()


def token_exists(token: str) -> bool:
    return db.session.query(Booking.query.filter_by(token=token.upper()).exists()).scalar()


def find_expiring_individual_bookings_query() -> BaseQuery:
    today_at_midnight = datetime.combine(date.today(), time(0, 0))
    return (
        Booking.query.join(Stock)
        .join(Offer)
        .filter(
            Booking.status == BookingStatus.CONFIRMED,
            Offer.canExpire,
            case(
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
        Booking.query.join(Stock)
        .join(Offer)
        .filter(
            Booking.status == BookingStatus.CONFIRMED,
            Offer.canExpire,
            case(
                (
                    Offer.subcategoryId == subcategories.LIVRE_PAPIER.id,
                    ((Booking.dateCreated + constants.BOOKS_BOOKINGS_AUTO_EXPIRY_DELAY).between(*books_window)),
                ),
                else_=(Booking.dateCreated + constants.BOOKINGS_AUTO_EXPIRY_DELAY).between(*rest_window),
            ),
        )
        .order_by(Booking.userId)
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
        for user_id, in (
            db.session.query(User.id)
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


def get_expired_individual_bookings_for_user(user: User, expired_on: date | None = None) -> list[Booking]:
    expired_on = expired_on or date.today()
    return Booking.query.filter(
        Booking.user == user,
        Booking.status == BookingStatus.CANCELLED,
        Booking.cancellationDate >= expired_on,
        Booking.cancellationDate < (expired_on + timedelta(days=1)),
        Booking.cancellationReason == BookingCancellationReasons.EXPIRED,
    ).all()


def find_expired_individual_bookings_ordered_by_offerer(expired_on: date | None = None) -> list[Booking]:
    expired_on = expired_on or date.today()
    return (
        Booking.query.filter(Booking.status == BookingStatus.CANCELLED)
        .filter(cast(Booking.cancellationDate, Date) == expired_on)
        .filter(Booking.cancellationReason == BookingCancellationReasons.EXPIRED)
        .order_by(Booking.offererId)
        .all()
    )


def get_active_bookings_quantity_for_venue(venue_id: int) -> int:
    # Stock.dnBookedQuantity cannot be used here because we exclude used/confirmed bookings.
    active_bookings_query = Booking.query.join(Stock, Booking.stock).filter(
        Booking.venueId == venue_id,
        Booking.status == BookingStatus.CONFIRMED,
        not_(Booking.isConfirmed),
    )

    n_active_bookings = active_bookings_query.with_entities(coalesce(func.sum(Booking.quantity), 0)).one()[0]

    n_active_collective_bookings = (
        educational_models.CollectiveBooking.query.join(
            educational_models.CollectiveStock, educational_models.CollectiveBooking.collectiveStock
        )
        .filter(
            educational_models.CollectiveBooking.venueId == venue_id,
            or_(
                and_(
                    educational_models.CollectiveBooking.status == educational_models.CollectiveBookingStatus.PENDING,
                    not_(educational_models.CollectiveStock.hasBookingLimitDatetimePassed),
                ),
                and_(
                    educational_models.CollectiveBooking.status == educational_models.CollectiveBookingStatus.CONFIRMED,
                    not_(educational_models.CollectiveBooking.isConfirmed),
                ),
            ),
        )
        .with_entities(coalesce(func.sum(1), 0))
        .one()[0]
    )

    return n_active_bookings + n_active_collective_bookings


def get_validated_bookings_quantity_for_venue(venue_id: int) -> int:
    validated_bookings_quantity_query = Booking.query.filter(
        Booking.venueId == venue_id,
        Booking.status != BookingStatus.CANCELLED,
        or_(Booking.is_used_or_reimbursed, Booking.isConfirmed),  # type: ignore[type-var]
    )

    n_validated_bookings_quantity = validated_bookings_quantity_query.with_entities(
        coalesce(func.sum(Booking.quantity), 0)
    ).one()[0]

    n_validated_collective_bookings_quantity = (
        educational_models.CollectiveBooking.query.filter(
            educational_models.CollectiveBooking.venueId == venue_id,
            educational_models.CollectiveBooking.status != educational_models.CollectiveBookingStatus.CANCELLED,
            educational_models.CollectiveBooking.status != educational_models.CollectiveBookingStatus.PENDING,
            or_(  # type: ignore[type-var]
                educational_models.CollectiveBooking.is_used_or_reimbursed,
                educational_models.CollectiveBooking.isConfirmed,
            ),
        )
        .with_entities(coalesce(func.sum(1), 0))
        .one()[0]
    )

    return n_validated_bookings_quantity + n_validated_collective_bookings_quantity


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


def _get_booking_status(status: BookingStatus, is_confirmed: bool) -> str:
    cancellation_limit_date_exists_and_past = is_confirmed
    if cancellation_limit_date_exists_and_past and status == BookingStatus.CONFIRMED:
        return BOOKING_STATUS_LABELS["confirmed"]
    return BOOKING_STATUS_LABELS[status]


def _write_bookings_to_excel(query: BaseQuery) -> bytes:
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
        if booking.quantity == DUO_QUANTITY:
            _write_excel_row(worksheet, row, booking, currency_format, "DUO 1")
            row += 1
            _write_excel_row(worksheet, row, booking, currency_format, "DUO 2")
        else:
            _write_excel_row(worksheet, row, booking, currency_format, "Non")
        row += 1
    workbook.close()
    return output.getvalue()


def _write_excel_row(
    worksheet: Worksheet, row: int, booking: Booking, currency_format: Format, duo_column: str
) -> None:
    worksheet.write(row, 0, booking.venueName)
    worksheet.write(row, 1, booking.offerName)
    worksheet.write(row, 2, str(convert_booking_dates_utc_to_venue_timezone(booking.stockBeginningDatetime, booking)))
    worksheet.write(row, 3, booking.ean)
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
            booking.isExternal,
            booking.stockBeginningDatetime,
        ),
    )
    worksheet.write(row, 10, booking.priceCategoryLabel)
    worksheet.write(row, 11, booking.amount, currency_format)
    worksheet.write(row, 12, _get_booking_status(booking.status, booking.isConfirmed))
    worksheet.write(row, 13, str(convert_booking_dates_utc_to_venue_timezone(booking.reimbursedAt, booking)))
    worksheet.write(row, 14, serialize_offer_type_educational_or_individual(offer_is_educational=False))
    worksheet.write(row, 15, booking.beneficiaryPostalCode)
    worksheet.write(
        row,
        16,
        duo_column,
    )


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
                booking.ean,
                f"{booking.beneficiaryLastName} {booking.beneficiaryFirstName}",
                booking.beneficiaryEmail,
                booking.beneficiaryPhoneNumber,
                convert_booking_dates_utc_to_venue_timezone(booking.bookedAt, booking),
                convert_booking_dates_utc_to_venue_timezone(booking.usedAt, booking),
                booking_recap_utils.get_booking_token(
                    booking.token,
                    booking.status,
                    booking.isExternal,
                    booking.stockBeginningDatetime,
                ),
                booking.priceCategoryLabel or "",
                booking.amount,
                _get_booking_status(booking.status, booking.isConfirmed),
                convert_booking_dates_utc_to_venue_timezone(booking.reimbursedAt, booking),
                # This method is still used in the old Payment model
                serialize_offer_type_educational_or_individual(offer_is_educational=False),
                booking.beneficiaryPostalCode or "",
                "Oui" if booking.quantity == DUO_QUANTITY else "Non",
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
        worksheet.write(row, 3, booking.ean)
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
                booking.isExternal,
                booking.stockBeginningDatetime,
            ),
        )
        worksheet.write(row, 10, booking.priceCategoryLabel)
        worksheet.write(row, 11, booking.amount, currency_format)
        worksheet.write(row, 12, _get_booking_status(booking.status, booking.isConfirmed))
        worksheet.write(row, 13, str(convert_booking_dates_utc_to_venue_timezone(booking.reimbursedAt, booking)))
        worksheet.write(row, 14, serialize_offer_type_educational_or_individual(offer_is_educational=False))
        worksheet.write(row, 15, booking.beneficiaryPostalCode)
        worksheet.write(
            row,
            16,
            "Oui" if booking.quantity == DUO_QUANTITY else "Non",
        )
        row += 1

    workbook.close()
    return output.getvalue()


def get_soon_expiring_bookings(expiration_days_delta: int) -> typing.Generator[Booking, None, None]:
    """Find bookings expiring in exactly `expiration_days_delta` days"""
    query = (
        Booking.query.options(
            contains_eager(Booking.stock).load_only(Stock.id).contains_eager(Stock.offer).load_only(Offer.subcategoryId)
        )
        .join(Booking.stock)
        .join(Stock.offer)
        .filter_by(canExpire=True)
        .filter(Booking.status == BookingStatus.CONFIRMED)
        .yield_per(1_000)
    )

    delta = timedelta(days=expiration_days_delta)
    for booking in query:
        expiration_date = booking.expirationDate
        if expiration_date and expiration_date.date() == date.today() + delta:
            yield booking


def venues_have_bookings(*venues: Venue) -> bool:
    """At least one venue which has email as bookingEmail has at least one non-cancelled booking"""
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
            Booking.status == BookingStatus.CONFIRMED,
        ).exists()
    ).scalar()


def find_individual_bookings_event_happening_tomorrow_query() -> list[Booking]:
    tomorrow = datetime.utcnow() + timedelta(days=1)
    tomorrow_min = datetime.combine(tomorrow, time.min)
    tomorrow_max = datetime.combine(tomorrow, time.max)

    return (
        Booking.query.join(
            Booking.user,
        )
        .join(Booking.stock)
        .join(Stock.offer)
        .join(Offer.venue)
        .outerjoin(Booking.activationCode)
        .outerjoin(Offer.criteria)
        .filter(Stock.beginningDatetime >= tomorrow_min, Stock.beginningDatetime <= tomorrow_max)
        .filter(Offer.isEvent)
        .filter(not_(Offer.isDigital))
        .filter(Booking.status != BookingStatus.CANCELLED)
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


def get_external_bookings_by_cinema_id_and_barcodes(
    venueIdAtOfferProvider: str, barcodes: list[str]
) -> list[ExternalBooking]:
    return (
        ExternalBooking.query.join(Booking)
        .join(VenueProvider, Booking.venueId == VenueProvider.venueId)
        .filter(VenueProvider.venueIdAtOfferProvider == venueIdAtOfferProvider)
        .filter(ExternalBooking.barcode.in_(barcodes))
        .all()
    )

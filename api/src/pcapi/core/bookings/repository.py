import csv
from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta
from io import BytesIO
from io import StringIO
import typing

from flask_sqlalchemy import BaseQuery
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import TIMESTAMP
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
from pcapi.utils.date import utc_to_local_datetime
from pcapi.utils.token import random_token


DUO_QUANTITY = 2

BOOKING_STATUS_LABELS = {
    BookingStatus.CONFIRMED: "réservé",
    BookingStatus.CANCELLED: "annulé",
    BookingStatus.USED: "validé",
    BookingStatus.REIMBURSED: "remboursé",
    "confirmed": "confirmé",
}

BOOKING_EXPORT_HEADERS = (
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
)


# FIXME (Gautier, 2022-03-25): also used in collective_bookings. Should we move it to core or some other place?
def field_to_venue_timezone(field: typing.Any) -> sa.cast:
    return sa.cast(sa.func.timezone(Venue.timezone, sa.func.timezone("UTC", field)), sa.Date)


def _bookings_export_entities(full_entities: bool = True) -> list:
    entities = [
        Booking.id.label("id"),
        Booking.quantity.label("quantity"),
        Booking.dateCreated.label("bookedAt"),
        Booking.dateUsed.label("usedAt"),
        Booking.reimbursementDate.label("reimbursedAt"),
        Venue.timezone.label("venueTimezone"),
    ]
    if full_entities:
        extra_entities = [
            Booking.status.label("status"),
            Booking.token.label("bookingToken"),
            Booking.priceCategoryLabel.label("priceCategoryLabel"),
            Booking.amount.label("bookingAmount"),
            Booking.cancellationDate.label("cancelledAt"),
            Booking.isExternal.label("isExternal"),  # type: ignore[attr-defined]
            Booking.isConfirmed.label("isConfirmed"),  # type: ignore[attr-defined]
            Booking.stockId.label("stockId"),
            Venue.common_name.label("venueName"),  # type: ignore[attr-defined]
            Stock.beginningDatetime.label("stockBeginningDatetime"),
            Offer.id.label("offerId"),
            Offer.name.label("offerName"),
            Offer.extraData["ean"].label("offerEan"),
            User.firstName.label("beneficiaryFirstName"),
            User.lastName.label("beneficiaryLastName"),
            User.email.label("beneficiaryEmail"),
            User.phoneNumber.label("beneficiaryPhoneNumber"),  # type: ignore[attr-defined]
            User.postalCode.label("beneficiaryPostalCode"),
        ]
        entities.extend(extra_entities)
    return entities


def _filter_booking_period(
    query: BaseQuery,
    booking_period: tuple[date, date],
    status_filter: BookingStatusFilter | None = None,
    with_tz: bool = False,
) -> BaseQuery:
    if not status_filter:
        status_filter = BookingStatusFilter.BOOKED
    field = {
        BookingStatusFilter.BOOKED: sa.column("bookedAt") if with_tz else Booking.dateCreated,
        BookingStatusFilter.VALIDATED: sa.column("usedAt") if with_tz else Booking.dateUsed,
        BookingStatusFilter.REIMBURSED: sa.column("reimbursedAt") if with_tz else Booking.reimbursementDate,
    }[status_filter]
    start = datetime.combine(booking_period[0], time.min) - timedelta(days=1)
    end = datetime.combine(booking_period[1], time.min) + timedelta(days=2)
    if with_tz:
        field = sa.func.timezone(sa.column("venueTimezone"), sa.func.timezone("UTC", field))
        start += timedelta(days=1)
        end -= timedelta(days=1)
    query = query.filter(field >= sa.cast(start, TIMESTAMP))  # type: ignore[type-var]
    query = query.filter(field < sa.cast(end, TIMESTAMP))  # type: ignore[type-var]
    return query


def _get_bookings_export_query(
    pro_user: User | None = None,
    booking_period: tuple[date, date] | None = None,
    status_filter: BookingStatusFilter | None = None,
    validated: bool = False,
    event_date: date | None = None,
    venue_id: int | None = None,
    offer_id: int | None = None,
    ordered: bool = False,
    full_entities: bool = True,
    duplicate_duo: bool = False,
    offset: int | None = None,
    limit: int | None = None,
) -> BaseQuery:
    if not pro_user and not offer_id:
        raise ValueError("Missing either pro_user or offer_id")

    query = Booking.query.join(Booking.venue)
    query = query.join(Booking.stock)
    if full_entities:
        query = query.join(Stock.offer)
        query = query.join(Booking.user)

    if pro_user is not None and not pro_user.has_admin_role:
        subquery = UserOfferer.query.filter(
            UserOfferer.user == pro_user,
            UserOfferer.isValidated,
        ).with_entities(UserOfferer.offererId)
        query = query.filter(Booking.offererId.in_(subquery))

    if booking_period:
        query = _filter_booking_period(query, booking_period, status_filter=status_filter)

    if validated:
        query = query.filter(
            sa.or_(
                sa.and_(Booking.isConfirmed, Booking.status != BookingStatus.CANCELLED),  # type: ignore[type-var]
                Booking.status == BookingStatus.USED,
            )
        )

    if venue_id is not None:
        query = query.filter(Booking.venueId == venue_id)

    if offer_id is not None:
        query = query.filter(Stock.offerId == offer_id)

    if event_date:
        query = query.filter(field_to_venue_timezone(Stock.beginningDatetime) == event_date)

    if ordered:
        query = query.order_by(Booking.id)

    entities = _bookings_export_entities(full_entities=full_entities)
    query = query.with_entities(*entities)

    if duplicate_duo:
        query = query.union_all(query.filter(Booking.quantity == DUO_QUANTITY))

    query_cte = None
    if booking_period:
        query_cte = query.cte()
        query = db.session.query(*query_cte.c)
        query = _filter_booking_period(query, booking_period, status_filter=status_filter, with_tz=True)

    if not full_entities:
        quantity_c = query_cte.c.quantity if query_cte is not None else Booking.quantity
        # We really want total quantities here (and not the number of bookings),
        # since we'll build two rows for each "duo" bookings later.
        query = query.with_entities(sa.func.coalesce(sa.func.sum(quantity_c), 0))

    if offset is not None and limit is not None:
        query = query.order_by(sa.column("bookedAt").desc()).offset(offset).limit(limit)

    return query


def _get_booking_status(status: BookingStatus | str, is_confirmed: bool) -> str:
    if is_confirmed and status == BookingStatus.CONFIRMED:
        status = "confirmed"
    return BOOKING_STATUS_LABELS[status]


def _build_export_columns(booking: Booking, duo_column: str, is_csv: bool) -> list[dict]:
    booking_token = booking_recap_utils.get_booking_token(
        booking.bookingToken,
        booking.status,
        bool(booking.isExternal),
        booking.stockBeginningDatetime,
    )
    timezone = booking.venueTimezone
    stock_beginning_datetime = utc_to_local_datetime(booking.stockBeginningDatetime, timezone)
    booked_at = utc_to_local_datetime(booking.bookedAt, timezone)
    used_at = utc_to_local_datetime(booking.usedAt, timezone)
    price_category_label = booking.priceCategoryLabel
    reimbursed_at = utc_to_local_datetime(booking.reimbursedAt, timezone)
    beneficiary_postal_code = booking.beneficiaryPostalCode
    columns = [
        {"value": booking.venueName},
        {"value": booking.offerName},
        {"value": stock_beginning_datetime if is_csv else str(stock_beginning_datetime)},
        {"value": booking.offerEan},
        {"value": f"{booking.beneficiaryLastName} {booking.beneficiaryFirstName}"},
        {"value": booking.beneficiaryEmail},
        {"value": booking.beneficiaryPhoneNumber},
        {"value": booked_at if is_csv else str(booked_at)},
        {"value": used_at if is_csv else str(used_at)},
        {"value": booking_token},
        {"value": (price_category_label or "") if is_csv else price_category_label},
        {"value": booking.bookingAmount, "type": "currency"},
        {"value": _get_booking_status(booking.status, bool(booking.isConfirmed))},
        {"value": reimbursed_at if is_csv else str(reimbursed_at)},
        {"value": serialize_offer_type_educational_or_individual(offer_is_educational=False)},
        {"value": (beneficiary_postal_code or "") if is_csv else beneficiary_postal_code},
        {"value": duo_column},
    ]
    return columns


def _write_csv_row(writer: typing.Any, booking: Booking, duo_column: str) -> None:
    columns = _build_export_columns(booking, duo_column, True)
    writer.writerow(tuple(column["value"] for column in columns))


def _write_bookings_to_csv(query: BaseQuery) -> str:
    output = StringIO()
    writer = csv.writer(output, dialect=csv.excel, delimiter=";", quoting=csv.QUOTE_NONNUMERIC)
    writer.writerow(BOOKING_EXPORT_HEADERS)
    for booking in query.yield_per(1000):
        if booking.quantity == DUO_QUANTITY:
            _write_csv_row(writer, booking, "DUO 1")
            _write_csv_row(writer, booking, "DUO 2")
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


def _write_bookings_to_excel(query: BaseQuery) -> bytes:
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)

    bold = workbook.add_format({"bold": 1})
    currency_format = workbook.add_format({"num_format": "###0.00[$€-fr-FR]"})
    col_width = 18

    worksheet = workbook.add_worksheet()

    row = 0
    for col_num, title in enumerate(BOOKING_EXPORT_HEADERS):
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


def get_export(
    user: User,
    booking_period: tuple[date, date] | None = None,
    status_filter: BookingStatusFilter | None = None,
    event_date: date | None = None,
    venue_id: int | None = None,
    offer_id: int | None = None,
    export_type: BookingExportType | None = BookingExportType.CSV,
) -> str | bytes:
    query = _get_bookings_export_query(
        pro_user=user,
        booking_period=booking_period,
        status_filter=status_filter,
        event_date=event_date,
        venue_id=venue_id,
        offer_id=offer_id,
    )
    if export_type == BookingExportType.EXCEL:
        return _write_bookings_to_excel(query)
    return _write_bookings_to_csv(query)


def export_bookings_by_offer_id(
    offer_id: int, event_date: date, export_type: BookingExportType, validated: bool = True
) -> str | bytes:
    query = _get_bookings_export_query(
        validated=validated,
        event_date=event_date,
        offer_id=offer_id,
        ordered=True,
    )
    if export_type == BookingExportType.EXCEL:
        return _write_bookings_to_excel(query)
    return _write_bookings_to_csv(query)


def _get_bookings_count(
    pro_user: User,
    booking_period: tuple[date, date] | None = None,
    status_filter: BookingStatusFilter | None = None,
    event_date: date | None = None,
    venue_id: int | None = None,
    offer_id: int | None = None,
) -> int:
    query = _get_bookings_export_query(
        pro_user=pro_user,
        booking_period=booking_period,
        status_filter=status_filter,
        event_date=event_date,
        venue_id=venue_id,
        offer_id=offer_id,
        full_entities=False,
    )
    return query.scalar()


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
    total_bookings_recap = _get_bookings_count(
        user,
        booking_period=booking_period,
        status_filter=status_filter,
        event_date=event_date,
        venue_id=venue_id,
        offer_id=offer_id,
    )
    bookings_query = _get_bookings_export_query(
        pro_user=user,
        booking_period=booking_period,
        status_filter=status_filter,
        event_date=event_date,
        venue_id=venue_id,
        offer_id=offer_id,
        duplicate_duo=True,
        offset=(page - 1) * per_page_limit,
        limit=per_page_limit,
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
    return (
        Booking.status == BookingStatus.CANCELLED,
        sa.cast(Booking.cancellationDate, sa.Date) == expired_on,
        Booking.cancellationReason == BookingCancellationReasons.EXPIRED,
    )


def find_user_ids_with_expired_individual_bookings(expired_on: date | None = None) -> list[int]:
    query = db.session.query(User.id).join(Booking).filter(*_is_expired(expired_on)).all()
    return [user_id for user_id, in query]


def get_expired_individual_bookings_for_user(user: User, expired_on: date | None = None) -> list[Booking]:
    return Booking.query.filter(Booking.user == user).filter(*_is_expired(expired_on)).all()


def find_expired_individual_bookings_ordered_by_offerer(expired_on: date | None = None) -> list[Booking]:
    return Booking.query.filter(*_is_expired(expired_on)).order_by(Booking.offererId).all()


def get_active_bookings_quantity_for_venue(venue_id: int) -> int:
    # Stock.dnBookedQuantity cannot be used here because we exclude used/confirmed bookings.
    n_active_bookings = (
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

    n_active_collective_bookings = (
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

    return n_active_bookings + n_active_collective_bookings


def get_validated_bookings_quantity_for_venue(venue_id: int) -> int:
    n_validated_bookings_quantity = (
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

    n_validated_collective_bookings_quantity = (
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


def get_soon_expiring_bookings(expiration_days_delta: int) -> typing.Generator[Booking, None, None]:
    """Find bookings expiring in exactly `expiration_days_delta` days"""
    dt = date.today() + timedelta(days=expiration_days_delta)
    query = (
        Booking.query.options(
            contains_eager(Booking.stock).load_only(Stock.id).contains_eager(Stock.offer).load_only(Offer.subcategoryId)
        )
        .join(Stock)
        .join(Offer)
        .filter(
            Offer.canExpire,
            Booking.status == BookingStatus.CONFIRMED,
        )
        .yield_per(1000)
    )
    for booking in query:
        expiration_date = booking.expirationDate
        if expiration_date and expiration_date.date() == dt:
            yield booking


def venues_have_bookings(*venues: Venue) -> bool:
    """At least one venue which has email as bookingEmail has at least one non-canceled booking"""
    return db.session.query(
        Booking.query.filter(
            Booking.venueId.in_([venue.id for venue in venues]),
            Booking.status != BookingStatus.CANCELLED,
        ).exists()
    ).scalar()


def user_has_bookings(user: User) -> bool:
    return db.session.query(
        Booking.query.join(Booking.offerer).join(Offerer.UserOfferers).filter(UserOfferer.userId == user.id).exists()
    ).scalar()


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
            Booking.stock,
            Stock.offer,
            Offer.venue,
        )
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

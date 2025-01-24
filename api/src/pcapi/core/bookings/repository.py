import csv
from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta
from io import BytesIO
from io import StringIO
from operator import and_
import typing

from flask_sqlalchemy import BaseQuery
import sqlalchemy as sa
from sqlalchemy import Date
from sqlalchemy import case
from sqlalchemy import cast
from sqlalchemy import func
from sqlalchemy import or_
from sqlalchemy import text
from sqlalchemy.orm import aliased
from sqlalchemy.orm import contains_eager
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.sql.elements import not_
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
from pcapi.core.bookings.utils import convert_date_period_to_utc_datetime_period
from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.finance.models import BookingFinanceIncident
from pcapi.core.geography.models import Address
from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.models import OffererAddress
from pcapi.core.offerers.models import UserOfferer
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.core.providers.models import VenueProvider
from pcapi.core.users.models import User
from pcapi.domain.booking_recap import utils as booking_recap_utils
from pcapi.models import db
from pcapi.models.feature import FeatureToggle
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

LEGACY_BOOKING_EXPORT_HEADER = [
    "Lieu",
    "Nom de l’offre",
    "Date de l'évènement",
    "EAN",
    "Prénom du bénéficiaire",
    "Nom du bénéficiaire",
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

BOOKING_EXPORT_HEADER = [
    "Structure",
    "Nom de l’offre",
    "Localisation",
    "Date de l'évènement",
    "EAN",
    "Prénom du bénéficiaire",
    "Nom du bénéficiaire",
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


def booking_export_header() -> list[str]:
    if FeatureToggle.WIP_ENABLE_OFFER_ADDRESS.is_active():
        return BOOKING_EXPORT_HEADER
    return LEGACY_BOOKING_EXPORT_HEADER


def find_by_pro_user(
    user: User,
    *,
    booking_period: tuple[date, date] | None = None,
    status_filter: BookingStatusFilter | None = None,
    event_date: date | None = None,
    venue_id: int | None = None,
    offer_id: int | None = None,
    offerer_address_id: int | None = None,
    page: int = 1,
    per_page_limit: int = 1000,
) -> tuple[BaseQuery, int]:
    total_bookings_recap = _get_filtered_bookings_count(
        user,
        period=booking_period,
        status_filter=status_filter,
        event_date=event_date,
        venue_id=venue_id,
        offer_id=offer_id,
        offerer_address_id=offerer_address_id,
    )

    bookings_query = _get_filtered_booking_pro(
        pro_user=user,
        period=booking_period,
        status_filter=status_filter,
        event_date=event_date,
        venue_id=venue_id,
        offer_id=offer_id,
        offerer_address_id=offerer_address_id,
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
            .join(Booking, User.userBookings)
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
        .options(
            joinedload(Booking.stock).joinedload(Stock.offer),
            joinedload(Booking.incidents).joinedload(BookingFinanceIncident.incident),
        )
        .all()
    )


def _create_export_query(offer_id: int, event_beginning_date: date) -> BaseQuery:
    VenueOffererAddress = aliased(OffererAddress)
    VenueAddress = aliased(Address)

    with_entities: tuple[typing.Any, ...] = (
        Booking.id.label("id"),
        Venue.common_name.label("venueName"),  # type: ignore[attr-defined]
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
    if FeatureToggle.WIP_USE_OFFERER_ADDRESS_AS_DATA_SOURCE.is_active():
        with_entities += (
            Address.departmentCode.label("offerDepartmentCode"),
            VenueAddress.departmentCode.label("venueDepartmentCode"),
            func.coalesce(func.nullif(OffererAddress.label, ""), Venue.common_name).label("locationName"),
            Address.street.label("locationStreet"),
            Address.postalCode.label("locationPostalCode"),
            Address.city.label("locationCity"),
        )
    else:
        with_entities += (Venue.departementCode.label("venueDepartmentCode"),)

    query = (
        Booking.query.join(Booking.offerer)
        .join(Booking.user)
        .join(Offerer.UserOfferers)
        .join(Booking.venue)
        .join(Booking.stock)
        .join(Stock.offer)
    )
    timezone_column: sa.orm.Mapped[typing.Any] | sa.sql.functions.Function = Venue.timezone
    if FeatureToggle.WIP_USE_OFFERER_ADDRESS_AS_DATA_SOURCE.is_active():
        query = (
            query.outerjoin(Offer.offererAddress)
            .outerjoin(OffererAddress.address)
            .join(VenueOffererAddress, Venue.offererAddressId == VenueOffererAddress.id)
            .join(VenueAddress, VenueOffererAddress.addressId == VenueAddress.id)
        )
        # NB: unfortunatly, we still have to use Venue.timezone for digital offers
        # as they are still on virtual venues that don't have assocaited OA.
        # Venue.timezone removal here requires that all venues have their OA
        timezone_column = func.coalesce(Address.timezone, VenueAddress.timezone, Venue.timezone)

    query = (
        query.filter(
            Stock.offerId == offer_id,
            field_to_venue_timezone(Stock.beginningDatetime, timezone_column) == event_beginning_date,
        )
        .order_by(Booking.id)
        .with_entities(*with_entities)
    )
    return query.distinct(Booking.id)


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


def export_bookings_by_offer_id(
    offer_id: int, event_beginning_date: date, export_type: BookingExportType
) -> str | bytes:
    offer_bookings_query = _create_export_query(offer_id, event_beginning_date)
    if export_type == BookingExportType.EXCEL:
        return _write_bookings_to_excel(offer_bookings_query)
    return _write_bookings_to_csv(offer_bookings_query)


def get_export(
    user: User,
    *,
    booking_period: tuple[date, date] | None = None,
    status_filter: BookingStatusFilter | None = BookingStatusFilter.BOOKED,
    event_date: date | None = None,
    venue_id: int | None = None,
    offer_id: int | None = None,
    offerer_address_id: int | None = None,
    export_type: BookingExportType | None = BookingExportType.CSV,
) -> str | bytes:
    bookings_query = _get_filtered_booking_report(
        pro_user=user,
        period=booking_period,
        status_filter=status_filter,
        event_date=event_date,
        venue_id=venue_id,
        offer_id=offer_id,
        offerer_address_id=offerer_address_id,
    )
    bookings_query = _duplicate_booking_when_quantity_is_two(bookings_query)
    if export_type == BookingExportType.EXCEL:
        return _serialize_excel_report(bookings_query)
    return _serialize_csv_report(bookings_query)


def get_pro_user_timezones(user: User) -> set[str]:
    # Timezones based on offerer addresses
    addresses_timezones_query = (
        Address.query.with_entities(Address.timezone)
        .join(OffererAddress, OffererAddress.addressId == Address.id)
        .join(Offerer, OffererAddress.offererId == Offerer.id)
        .join(UserOfferer, UserOfferer.offererId == Offerer.id)
        .filter(UserOfferer.userId == user.id)
        .distinct()
    )
    # Timezones based on offerer venues
    # For digital offers that do not have an address
    venues_timezones_query = (
        Venue.query.with_entities(Venue.timezone)
        .join(Offerer, Venue.managingOffererId == Offerer.id)
        .join(UserOfferer, UserOfferer.offererId == Offerer.id)
        .filter(UserOfferer.userId == user.id)
        .distinct()
    )
    query = addresses_timezones_query.union_all(venues_timezones_query)

    return {row[0] for row in query}


def field_to_venue_timezone(
    field: InstrumentedAttribute, column: sa.orm.Mapped[typing.Any] | sa.sql.functions.Function
) -> cast:
    return cast(func.timezone(column, func.timezone("UTC", field)), Date)


def serialize_offer_type_educational_or_individual(offer_is_educational: bool) -> str:
    return "offre collective" if offer_is_educational else "offre grand public"


def _get_filtered_bookings_query(
    pro_user: User,
    *,
    period: tuple[date, date] | None = None,
    status_filter: BookingStatusFilter | None = None,
    event_date: date | None = None,
    venue_id: int | None = None,
    offer_id: int | None = None,
    offerer_address_id: int | None = None,
    extra_joins: tuple[tuple[typing.Any, ...], ...] = (),
) -> BaseQuery:
    VenueOffererAddress = aliased(OffererAddress)
    VenueAddress = aliased(Address)
    bookings_query = (
        Booking.query.join(Booking.offerer)
        .join(Offerer.UserOfferers)
        .join(Booking.stock)
        .join(Stock.offer)
        .join(Booking.externalBookings, isouter=True)
        .join(Booking.venue, isouter=True)
    )
    timezone_column: sa.orm.Mapped[typing.Any] | sa.sql.functions.Function = Venue.timezone
    if FeatureToggle.WIP_USE_OFFERER_ADDRESS_AS_DATA_SOURCE.is_active():
        bookings_query = (
            bookings_query.outerjoin(Offer.offererAddress)
            .outerjoin(OffererAddress.address)
            .outerjoin(VenueOffererAddress, Venue.offererAddressId == VenueOffererAddress.id)
            .outerjoin(VenueAddress, VenueOffererAddress.addressId == VenueAddress.id)
        )
        # NB: unfortunatly, we still have to use Venue.timezone for digital offers
        # as they are still on virtual venues that don't have assocaited OA.
        # Venue.timezone removal here requires that all venues have their OA
        timezone_column = func.coalesce(Address.timezone, VenueAddress.timezone, Venue.timezone)
    for join_key, *join_conditions in extra_joins:
        if join_conditions:
            bookings_query = bookings_query.join(join_key, *join_conditions, isouter=True)
        else:
            bookings_query = bookings_query.join(join_key, isouter=True)

    if not pro_user.has_admin_role:
        bookings_query = bookings_query.filter(UserOfferer.user == pro_user)

    bookings_query = bookings_query.filter(UserOfferer.isValidated)

    if period:
        date_column_to_filter_on = BOOKING_DATE_STATUS_MAPPING[status_filter or BookingStatusFilter.BOOKED]

        datetime_period_by_timezones = _convert_date_period_to_datetime_period_for_timezones(
            period,
            pro_user,
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

    if venue_id is not None:
        bookings_query = bookings_query.filter(Booking.venueId == venue_id)

    if offer_id is not None:
        bookings_query = bookings_query.filter(Stock.offerId == offer_id)

    if offerer_address_id:
        bookings_query = bookings_query.filter(Offer.offererAddressId == offerer_address_id)

    if event_date:
        bookings_query = bookings_query.filter(
            field_to_venue_timezone(Stock.beginningDatetime, timezone_column) == event_date
        )
    if offerer_address_id:
        bookings_query = bookings_query.filter(OffererAddress.id == offerer_address_id)
    return bookings_query


def _get_offerer_address_timezone(offerer_address_id: int) -> str:
    return (
        Address.query.with_entities(Address.timezone)
        .join(OffererAddress, OffererAddress.addressId == Address.id)
        .filter(OffererAddress.id == offerer_address_id)
        .scalar()
    )


def _get_offer_timezone(offer_id: int) -> str:
    """
    Retrieve the timezone associated with an offer.

    The function determines the timezone for the specified offer based on the following priority:
    1. If an address is directly linked to the offer, return its timezone.
    2. If no address is linked to the offer, return the timezone of the address linked to the offer's venue.
    3. If no address is linked to the venue (e.g., for virtual venues), return the venue's timezone.

    Note:
        - This behavior accounts for digital offers that are linked to virtual venues,
          which do not have associated offerer addresses. Once virtual venues are removed
          from the system, this fallback logic (step 3) should be simplified.

    Args:
        offer_id (int): The ID of the offer whose timezone is to be retrieved.

    Returns:
        str: The timezone associated with the offer.
    """
    VenueAddress = aliased(Address)
    VenueOffererAddress = aliased(OffererAddress)
    return (
        Offer.query.with_entities(
            # TODO: Simplify when the virtual venues are removed
            # Unfortunately, we still have to use Venue.timezone for digital offers
            # as they are still on virtual venues that don't have associated OA.
            # Venue.timezone removal here requires that all venues have their OA
            func.coalesce(Address.timezone, VenueAddress.timezone, Venue.timezone)
        )
        .join(Offer.venue)
        .outerjoin(Offer.offererAddress)
        .outerjoin(OffererAddress.address)
        .outerjoin(VenueOffererAddress, Venue.offererAddressId == VenueOffererAddress.id)
        .outerjoin(VenueAddress, VenueOffererAddress.addressId == VenueAddress.id)
        .filter(Offer.id == offer_id)
        .scalar()
    )


def _convert_date_period_to_datetime_period_for_timezones(
    period: tuple[date, date],
    pro_user: User,
    *,
    offer_id: int | None = None,
    offerer_address_id: int | None = None,
) -> dict[str, tuple[datetime, datetime]]:
    """
    Convert a date period to a UTC datetime period based on relevant timezones.

    The function determines the timezone(s) to use for the conversion based on the input parameters:
    1. If `offerer_address_id` is provided, fetch the timezone of the corresponding address.
    2. If `offer_id` is provided, fetch the timezone of the corresponding offer.
    3. Otherwise, fetch all the timezones linked to the `pro_user`.

    The conversion process transforms the given `period` (a date range) into a datetime range in UTC.
    The function returns a dictionary where:
        - Keys are the timezones.
        - Values are the corresponding UTC datetime ranges for the `period`.
    """
    if offerer_address_id:
        timezone = _get_offerer_address_timezone(offerer_address_id)
        return {timezone: convert_date_period_to_utc_datetime_period(period, timezone)}

    if offer_id:
        timezone = _get_offer_timezone(offer_id)
        return {timezone: convert_date_period_to_utc_datetime_period(period, timezone)}

    timezones = get_pro_user_timezones(pro_user)

    return {timezone: convert_date_period_to_utc_datetime_period(period, timezone) for timezone in timezones}


def _get_filtered_bookings_count(
    pro_user: User,
    *,
    period: tuple[date, date] | None = None,
    status_filter: BookingStatusFilter | None = None,
    event_date: date | None = None,
    venue_id: int | None = None,
    offer_id: int | None = None,
    offerer_address_id: int | None = None,
) -> int:
    bookings = (
        _get_filtered_bookings_query(
            pro_user,
            period=period,
            status_filter=status_filter,
            event_date=event_date,
            venue_id=venue_id,
            offer_id=offer_id,
            offerer_address_id=offerer_address_id,
        )
        .with_entities(Booking.id, Booking.quantity)
        .distinct(Booking.id)
    ).cte()
    # We really want total quantities here (and not the number of bookings),
    # since we'll build two rows for each "duo" bookings later.
    bookings_count = db.session.query(func.coalesce(func.sum(bookings.c.quantity), 0))
    return bookings_count.scalar()


def _get_filtered_booking_report(
    pro_user: User,
    *,
    period: tuple[date, date] | None,
    status_filter: BookingStatusFilter | None,
    event_date: date | None = None,
    venue_id: int | None = None,
    offer_id: int | None = None,
    offerer_address_id: int | None = None,
) -> BaseQuery:
    VenueOffererAddress = aliased(OffererAddress)
    VenueAddress = aliased(Address)

    with_entities: tuple[typing.Any, ...] = (
        Venue.common_name.label("venueName"),  # type: ignore[attr-defined]
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
    if FeatureToggle.WIP_USE_OFFERER_ADDRESS_AS_DATA_SOURCE.is_active():
        with_entities += (
            Address.departmentCode.label("offerDepartmentCode"),
            VenueAddress.departmentCode.label("venueDepartmentCode"),
            func.coalesce(func.nullif(OffererAddress.label, ""), Venue.common_name).label("locationName"),
            Address.street.label("locationStreet"),
            Address.postalCode.label("locationPostalCode"),
            Address.city.label("locationCity"),
        )
    else:
        with_entities += (Venue.departementCode.label("venueDepartmentCode"),)

    bookings_query = (
        _get_filtered_bookings_query(
            pro_user,
            period=period,
            status_filter=status_filter,
            event_date=event_date,
            venue_id=venue_id,
            offer_id=offer_id,
            offerer_address_id=offerer_address_id,
            extra_joins=(
                (Stock.offer,),
                (Booking.user,),
                (Offer.offererAddress,),
                (OffererAddress.address,),
                (VenueOffererAddress, Venue.offererAddressId == VenueOffererAddress.id),
                (VenueAddress, VenueOffererAddress.addressId == VenueAddress.id),
            ),
        )
        .with_entities(*with_entities)
        .distinct(Booking.id)
    )

    return bookings_query


def _get_filtered_booking_pro(
    pro_user: User,
    *,
    period: tuple[date, date] | None = None,
    status_filter: BookingStatusFilter | None = None,
    event_date: date | None = None,
    venue_id: int | None = None,
    offer_id: int | None = None,
    offerer_address_id: int | None = None,
) -> BaseQuery:
    VenueOffererAddress = aliased(OffererAddress)
    VenueAddress = aliased(Address)

    with_entities: tuple[typing.Any, ...] = (
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
        Offerer.postalCode.label("offererPostalCode"),
    )

    if FeatureToggle.WIP_USE_OFFERER_ADDRESS_AS_DATA_SOURCE.is_active():
        with_entities += (
            Address.departmentCode.label("offerDepartmentCode"),
            VenueAddress.departmentCode.label("venueDepartmentCode"),
        )
    else:
        with_entities += (Venue.departementCode.label("venueDepartmentCode"),)

    bookings_query = (
        _get_filtered_bookings_query(
            pro_user,
            period=period,
            status_filter=status_filter,
            event_date=event_date,
            venue_id=venue_id,
            offer_id=offer_id,
            offerer_address_id=offerer_address_id,
            extra_joins=(
                (Stock.offer,),
                (Booking.user,),
                (Offer.offererAddress,),
                (OffererAddress.address,),
                (VenueOffererAddress, Venue.offererAddressId == VenueOffererAddress.id),
                (VenueAddress, VenueOffererAddress.addressId == VenueAddress.id),
            ),
        )
        .with_entities(*with_entities)
        .distinct(Booking.id)
    )

    return bookings_query


def _duplicate_booking_when_quantity_is_two(bookings_recap_query: BaseQuery) -> BaseQuery:
    return bookings_recap_query.union_all(bookings_recap_query.filter(Booking.quantity == DUO_QUANTITY))


def _get_booking_status(status: BookingStatus, is_confirmed: bool) -> str:
    cancellation_limit_date_exists_and_past = is_confirmed
    if cancellation_limit_date_exists_and_past and status == BookingStatus.CONFIRMED:
        return BOOKING_STATUS_LABELS["confirmed"]
    return BOOKING_STATUS_LABELS[status]


def _write_bookings_to_csv(query: BaseQuery) -> str:
    output = StringIO()
    writer = csv.writer(output, dialect=csv.excel, delimiter=";", quoting=csv.QUOTE_NONNUMERIC)
    writer.writerow(booking_export_header())
    for booking in query.yield_per(1000):
        if booking.quantity == DUO_QUANTITY:
            _write_csv_row(writer, booking, "DUO 1")
            _write_csv_row(writer, booking, "DUO 2")
        else:
            _write_csv_row(writer, booking, "Non")

    return output.getvalue()


def _write_csv_row(csv_writer: typing.Any, booking: Booking, booking_duo_column: str) -> None:
    row: tuple[typing.Any, ...] = (
        booking.venueName,
        booking.offerName,
    )
    if FeatureToggle.WIP_ENABLE_OFFER_ADDRESS.is_active():
        location = (
            f"{booking.locationName} - {booking.locationStreet} {booking.locationPostalCode} {booking.locationCity}"
        )
        row += (location,)
    row += (
        convert_booking_dates_utc_to_venue_timezone(booking.stockBeginningDatetime, booking),
        booking.ean,
        booking.beneficiaryFirstName,
        booking.beneficiaryLastName,
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
    csv_writer.writerow(row)


def _write_bookings_to_excel(query: BaseQuery) -> bytes:
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)

    bold = workbook.add_format({"bold": 1})
    currency_format = workbook.add_format({"num_format": "###0.00[$€-fr-FR]"})
    col_width = 18

    worksheet = workbook.add_worksheet()
    row = 0

    for col_num, title in enumerate(booking_export_header()):
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
    worksheet.write(row, 4, booking.beneficiaryFirstName)
    worksheet.write(row, 5, booking.beneficiaryLastName)
    worksheet.write(row, 6, booking.beneficiaryEmail)
    worksheet.write(row, 7, booking.beneficiaryPhoneNumber)
    worksheet.write(row, 8, str(convert_booking_dates_utc_to_venue_timezone(booking.bookedAt, booking)))
    worksheet.write(row, 9, str(convert_booking_dates_utc_to_venue_timezone(booking.usedAt, booking)))
    worksheet.write(
        row,
        10,
        booking_recap_utils.get_booking_token(
            booking.token,
            booking.status,
            booking.isExternal,
            booking.stockBeginningDatetime,
        ),
    )
    worksheet.write(row, 11, booking.priceCategoryLabel)
    worksheet.write(row, 12, booking.amount, currency_format)
    worksheet.write(row, 13, _get_booking_status(booking.status, booking.isConfirmed))
    worksheet.write(row, 14, str(convert_booking_dates_utc_to_venue_timezone(booking.reimbursedAt, booking)))
    worksheet.write(row, 15, serialize_offer_type_educational_or_individual(offer_is_educational=False))
    worksheet.write(row, 16, booking.beneficiaryPostalCode)
    worksheet.write(
        row,
        17,
        duo_column,
    )


def _serialize_csv_report(query: BaseQuery) -> str:
    output = StringIO()
    writer = csv.writer(output, dialect=csv.excel, delimiter=";", quoting=csv.QUOTE_NONNUMERIC)
    writer.writerow(booking_export_header())
    for booking in query.yield_per(1000):
        row: tuple[typing.Any, ...] = (booking.venueName, booking.offerName)
        if FeatureToggle.WIP_ENABLE_OFFER_ADDRESS.is_active():
            location = (
                f"{booking.locationName} - {booking.locationStreet} {booking.locationPostalCode} {booking.locationCity}"
            )
            row += (location,)
        row += (
            convert_booking_dates_utc_to_venue_timezone(booking.stockBeginningDatetime, booking),
            booking.ean,
            booking.beneficiaryFirstName,
            booking.beneficiaryLastName,
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
        writer.writerow(row)

    return output.getvalue()


def _serialize_excel_report(query: BaseQuery) -> bytes:
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)

    bold = workbook.add_format({"bold": 1})
    currency_format = workbook.add_format({"num_format": "###0.00[$€-fr-FR]"})
    col_width = 18
    should_add_location = FeatureToggle.WIP_ENABLE_OFFER_ADDRESS.is_active()

    worksheet = workbook.add_worksheet()
    row = 0

    for col_num, title in enumerate(booking_export_header()):
        worksheet.write(row, col_num, title, bold)
        worksheet.set_column(col_num, col_num, col_width)
    row = 1
    data: tuple[typing.Any, ...]
    for booking in query.yield_per(1000):
        data = (booking.venueName, booking.offerName)
        if should_add_location:
            data += (
                f"{booking.locationName} - {booking.locationStreet} {booking.locationPostalCode} {booking.locationCity}",
            )
        data += (
            str(convert_booking_dates_utc_to_venue_timezone(booking.stockBeginningDatetime, booking)),
            booking.ean,
            booking.beneficiaryFirstName,
            booking.beneficiaryLastName,
            booking.beneficiaryEmail,
            booking.beneficiaryPhoneNumber,
            str(convert_booking_dates_utc_to_venue_timezone(booking.bookedAt, booking)),
            str(convert_booking_dates_utc_to_venue_timezone(booking.usedAt, booking)),
            booking_recap_utils.get_booking_token(
                booking.token, booking.status, booking.isExternal, booking.stockBeginningDatetime
            ),
            booking.priceCategoryLabel,
            booking.amount,
            _get_booking_status(booking.status, booking.isConfirmed),
            str(convert_booking_dates_utc_to_venue_timezone(booking.reimbursedAt, booking)),
            serialize_offer_type_educational_or_individual(offer_is_educational=False),
            booking.beneficiaryPostalCode,
            "Oui" if booking.quantity == DUO_QUANTITY else "Non",
        )
        worksheet.write_row(row, 0, data)
        worksheet.set_column(13, 13, cell_format=currency_format)
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
                joinedload(Offer.offererAddress).load_only(OffererAddress.label).joinedload(OffererAddress.address),
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

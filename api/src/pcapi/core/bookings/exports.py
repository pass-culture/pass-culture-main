import csv
import typing
from datetime import date
from datetime import datetime
from decimal import Decimal
from io import BytesIO
from io import StringIO

import sqlalchemy.orm as sa_orm
import xlsxwriter
from xlsxwriter.format import Format
from xlsxwriter.worksheet import Worksheet

from pcapi.core.bookings import models
from pcapi.core.bookings import repository
from pcapi.core.bookings import schemas
from pcapi.core.bookings import utils
from pcapi.utils import export as utils_export


DUO_QUANTITY = 2


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


BOOKING_STATUS_LABELS = {
    models.BookingStatus.CONFIRMED: "réservé",
    models.BookingStatus.CANCELLED: "annulé",
    models.BookingStatus.USED: "validé",
    models.BookingStatus.PENDING_REIMBURSEMENT: "en cours de remboursement",
    models.BookingStatus.REIMBURSED: "remboursé",
    "confirmed": "confirmé",
}


def get_booking_token(
    booking_token: str,
    booking_status: models.BookingStatus,
    booking_is_external: bool,
    event_beginning_datetime: datetime | None,
) -> str | None:
    if (
        not event_beginning_datetime
        and booking_status
        not in [
            models.BookingStatus.PENDING_REIMBURSEMENT,
            models.BookingStatus.REIMBURSED,
            models.BookingStatus.CANCELLED,
            models.BookingStatus.USED,
        ]
        or booking_is_external
    ):
        return None
    return booking_token


def booking_export_header() -> list[str]:
    return BOOKING_EXPORT_HEADER


def get_booking_price(booking: schemas.ExportBookingsQueryResult) -> Decimal:
    """
    Retourne le prix de la réservation, converti en CFP si le bénéficiaire est calédonien.
    """
    if hasattr(booking, "is_caledonian") and booking.is_caledonian:
        return utils.convert_euro_to_pacific_franc(booking.amount)
    return booking.amount


def serialize_offer_type_educational_or_individual(offer_is_educational: bool) -> str:
    return "offre collective" if offer_is_educational else "offre grand public"


def _get_booking_status(status: models.BookingStatus, is_confirmed: bool) -> str:
    cancellation_limit_date_exists_and_past = is_confirmed
    if cancellation_limit_date_exists_and_past and status == models.BookingStatus.CONFIRMED:
        return BOOKING_STATUS_LABELS["confirmed"]
    return BOOKING_STATUS_LABELS[status]


def _write_bookings_to_csv(query: sa_orm.Query) -> str:
    output = StringIO()
    writer = csv.writer(output, dialect=csv.excel, delimiter=";", quoting=csv.QUOTE_NONNUMERIC)
    writer.writerow(booking_export_header())
    for booking in query.yield_per(1000):
        booking = typing.cast(schemas.ExportBookingsQueryResult, booking)

        if booking.quantity == DUO_QUANTITY:
            _write_csv_row(writer, booking, "DUO 1")
            _write_csv_row(writer, booking, "DUO 2")
        else:
            _write_csv_row(writer, booking, "Non")

    return output.getvalue()


def _write_csv_row(csv_writer: typing.Any, booking: schemas.ExportBookingsQueryResult, booking_duo_column: str) -> None:
    booking_price = get_booking_price(booking)
    row: tuple[typing.Any, ...] = (
        booking.venueName,
        booking.offerName,
        f"{booking.locationName} - {booking.locationStreet} {booking.locationPostalCode} {booking.locationCity}",
        utils.convert_booking_dates_utc_to_venue_timezone(booking.stockBeginningDatetime, booking),
        booking.ean,
        booking.beneficiaryFirstName,
        booking.beneficiaryLastName,
        booking.beneficiaryEmail,
        booking.beneficiaryPhoneNumber,
        utils.convert_booking_dates_utc_to_venue_timezone(booking.bookedAt, booking),
        utils.convert_booking_dates_utc_to_venue_timezone(booking.usedAt, booking),
        get_booking_token(
            booking.token,
            booking.status,
            booking.isExternal,
            booking.stockBeginningDatetime,
        ),
        booking.priceCategoryLabel or "",
        booking_price,
        _get_booking_status(booking.status, booking.isConfirmed),
        utils.convert_booking_dates_utc_to_venue_timezone(booking.reimbursedAt, booking),
        serialize_offer_type_educational_or_individual(offer_is_educational=False),
        booking.beneficiaryPostalCode or "",
        booking_duo_column,
    )
    csv_writer.writerow(row)


def _write_bookings_to_excel(query: sa_orm.Query) -> bytes:
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)

    bold = workbook.add_format(utils_export.EXCEL_BOLD_FORMAT)
    currency_format_eur = workbook.add_format(utils_export.EXCEL_CURRENCY_FORMAT)
    currency_format_cfp = workbook.add_format(utils_export.EXCEL_CFP_FORMAT)
    col_width = utils_export.EXCEL_COL_WIDTH

    worksheet = workbook.add_worksheet()
    row = 0

    for col_num, title in enumerate(booking_export_header()):
        worksheet.write(row, col_num, title, bold)
        worksheet.set_column(col_num, col_num, col_width)

    row = 1
    for booking in query.yield_per(1000):
        booking = typing.cast(schemas.ExportBookingsQueryResult, booking)

        if booking.quantity == DUO_QUANTITY:
            _write_excel_row(
                worksheet,
                row,
                booking,
                currency_format_cfp if getattr(booking, "is_caledonian", False) else currency_format_eur,
                "DUO 1",
            )
            row += 1
            _write_excel_row(
                worksheet,
                row,
                booking,
                currency_format_cfp if getattr(booking, "is_caledonian", False) else currency_format_eur,
                "DUO 2",
            )
        else:
            _write_excel_row(
                worksheet,
                row,
                booking,
                currency_format_cfp if getattr(booking, "is_caledonian", False) else currency_format_eur,
                "Non",
            )
        row += 1
    workbook.close()
    return output.getvalue()


def _write_excel_row(
    worksheet: Worksheet, row: int, booking: schemas.ExportBookingsQueryResult, currency_format: Format, duo_column: str
) -> None:
    booking_price = get_booking_price(booking)
    worksheet.write(row, 0, booking.venueName)
    worksheet.write(row, 1, booking.offerName)
    worksheet.write(
        row, 2, str(utils.convert_booking_dates_utc_to_venue_timezone(booking.stockBeginningDatetime, booking))
    )
    worksheet.write(row, 3, booking.ean)
    worksheet.write(row, 4, booking.beneficiaryFirstName)
    worksheet.write(row, 5, booking.beneficiaryLastName)
    worksheet.write(row, 6, booking.beneficiaryEmail)
    worksheet.write(row, 7, booking.beneficiaryPhoneNumber)
    worksheet.write(row, 8, str(utils.convert_booking_dates_utc_to_venue_timezone(booking.bookedAt, booking)))
    worksheet.write(row, 9, str(utils.convert_booking_dates_utc_to_venue_timezone(booking.usedAt, booking)))
    worksheet.write(
        row,
        10,
        get_booking_token(
            booking.token,
            booking.status,
            booking.isExternal,
            booking.stockBeginningDatetime,
        ),
    )
    worksheet.write(row, 11, booking.priceCategoryLabel)
    worksheet.write(row, 12, booking_price, currency_format)
    worksheet.write(row, 13, _get_booking_status(booking.status, booking.isConfirmed))
    worksheet.write(row, 14, str(utils.convert_booking_dates_utc_to_venue_timezone(booking.reimbursedAt, booking)))
    worksheet.write(row, 15, serialize_offer_type_educational_or_individual(offer_is_educational=False))
    worksheet.write(row, 16, booking.beneficiaryPostalCode)
    worksheet.write(
        row,
        17,
        duo_column,
    )


def _serialize_csv_report(query: sa_orm.Query) -> str:
    output = StringIO()
    writer = csv.writer(output, dialect=csv.excel, delimiter=";", quoting=csv.QUOTE_NONNUMERIC)
    writer.writerow(booking_export_header())
    for booking in query.yield_per(1000):
        booking = typing.cast(schemas.ExportBookingsQueryResult, booking)

        booking_price = get_booking_price(booking)
        row: tuple[typing.Any, ...] = (
            booking.venueName,
            booking.offerName,
            f"{booking.locationName} - {booking.locationStreet} {booking.locationPostalCode} {booking.locationCity}",
            utils.convert_booking_dates_utc_to_venue_timezone(booking.stockBeginningDatetime, booking),
            booking.ean,
            booking.beneficiaryFirstName,
            booking.beneficiaryLastName,
            booking.beneficiaryEmail,
            booking.beneficiaryPhoneNumber,
            utils.convert_booking_dates_utc_to_venue_timezone(booking.bookedAt, booking),
            utils.convert_booking_dates_utc_to_venue_timezone(booking.usedAt, booking),
            get_booking_token(
                booking.token,
                booking.status,
                booking.isExternal,
                booking.stockBeginningDatetime,
            ),
            booking.priceCategoryLabel or "",
            booking_price,
            _get_booking_status(booking.status, booking.isConfirmed),
            utils.convert_booking_dates_utc_to_venue_timezone(booking.reimbursedAt, booking),
            # This method is still used in the old Payment model
            serialize_offer_type_educational_or_individual(offer_is_educational=False),
            booking.beneficiaryPostalCode or "",
            "Oui" if booking.quantity == DUO_QUANTITY else "Non",
        )
        writer.writerow(row)

    return output.getvalue()


def _serialize_excel_report(query: sa_orm.Query) -> bytes:
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)

    bold = workbook.add_format(utils_export.EXCEL_BOLD_FORMAT)
    currency_format_eur = workbook.add_format(utils_export.EXCEL_CURRENCY_FORMAT)
    currency_format_cfp = workbook.add_format(utils_export.EXCEL_CFP_FORMAT)
    col_width = utils_export.EXCEL_COL_WIDTH

    worksheet = workbook.add_worksheet()
    row = 0

    for col_num, title in enumerate(booking_export_header()):
        worksheet.write(row, col_num, title, bold)
        worksheet.set_column(col_num, col_num, col_width)
    row = 1
    data: tuple[typing.Any, ...]
    for booking in query.yield_per(1000):
        booking = typing.cast(schemas.ExportBookingsQueryResult, booking)

        booking_price = get_booking_price(booking)
        if hasattr(booking, "is_caledonian") and booking.is_caledonian:
            currency_format = currency_format_cfp
        else:
            currency_format = currency_format_eur
        data = (
            booking.venueName,
            booking.offerName,
            f"{booking.locationName} - {booking.locationStreet} {booking.locationPostalCode} {booking.locationCity}",
            str(utils.convert_booking_dates_utc_to_venue_timezone(booking.stockBeginningDatetime, booking)),
            booking.ean,
            booking.beneficiaryFirstName,
            booking.beneficiaryLastName,
            booking.beneficiaryEmail,
            booking.beneficiaryPhoneNumber,
            str(utils.convert_booking_dates_utc_to_venue_timezone(booking.bookedAt, booking)),
            str(utils.convert_booking_dates_utc_to_venue_timezone(booking.usedAt, booking)),
            get_booking_token(booking.token, booking.status, booking.isExternal, booking.stockBeginningDatetime),
            booking.priceCategoryLabel,
            booking_price,
            _get_booking_status(booking.status, booking.isConfirmed),
            str(utils.convert_booking_dates_utc_to_venue_timezone(booking.reimbursedAt, booking)),
            serialize_offer_type_educational_or_individual(offer_is_educational=False),
            booking.beneficiaryPostalCode,
            "Oui" if booking.quantity == DUO_QUANTITY else "Non",
        )
        worksheet.write_row(row, 0, data)
        worksheet.set_column(13, 13, cell_format=currency_format)
        row += 1

    workbook.close()
    return output.getvalue()


def export_bookings_by_offer_id(
    offer_id: int, event_beginning_date: date, export_type: models.BookingExportType
) -> str | bytes:
    offer_bookings_query = repository.export_query(offer_id, event_beginning_date)
    if export_type == models.BookingExportType.EXCEL:
        return _write_bookings_to_excel(offer_bookings_query)
    return _write_bookings_to_csv(offer_bookings_query)


def get_export(
    *,
    pro_user_id: int,
    venue_ids: list[int],
    booking_period: tuple[date, date] | None = None,
    status_filter: models.BookingStatusFilter | None = models.BookingStatusFilter.BOOKED,
    event_date: date | None = None,
    offer_id: int | None = None,
    offerer_address_id: int | None = None,
    export_type: models.BookingExportType | None = models.BookingExportType.CSV,
) -> str | bytes:
    bookings_query = repository.get_filtered_booking_report(
        pro_user_id=pro_user_id,
        venue_ids=venue_ids,
        period=booking_period,
        status_filter=status_filter,
        event_date=event_date,
        offer_id=offer_id,
        offerer_address_id=offerer_address_id,
    )
    bookings_query = repository.duplicate_booking_when_quantity_is_two(bookings_query)
    if export_type == models.BookingExportType.EXCEL:
        return _serialize_excel_report(bookings_query)
    return _serialize_csv_report(bookings_query)


def export_validated_bookings_by_offer_id(
    offer_id: int, event_beginning_date: date, export_type: models.BookingExportType
) -> str | bytes:
    offer_validated_bookings_query = repository.validated_bookings_by_offer_id_query(offer_id, event_beginning_date)
    if export_type == models.BookingExportType.EXCEL:
        return _write_bookings_to_excel(offer_validated_bookings_query)
    return _write_bookings_to_csv(offer_validated_bookings_query)

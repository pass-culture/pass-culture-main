import csv
from io import BytesIO
from io import StringIO

import sqlalchemy.orm as sa_orm
import xlsxwriter

from pcapi.core.bookings.utils import convert_collective_booking_dates_utc_to_venue_timezone
from pcapi.core.educational import models
from pcapi.core.educational import repository
from pcapi.utils import export as utils_export


def _get_booking_status(status: models.CollectiveBookingStatus, is_confirmed: bool) -> str:
    cancellation_limit_date_exists_and_past = is_confirmed
    if cancellation_limit_date_exists_and_past and status == models.CollectiveBookingStatus.CONFIRMED:
        return repository.COLLECTIVE_BOOKING_STATUS_LABELS["confirmed"]
    return repository.COLLECTIVE_BOOKING_STATUS_LABELS[status]


COLLECTIVE_BOOKING_EXPORT_HEADER = [
    "Lieu",
    "Nom de l'offre",
    "Date de l'évènement",
    "Prénom du bénéficiaire",
    "Nom du bénéficiaire",
    "Email du bénéficiaire",
    "Date et heure de réservation",
    "Date et heure de validation",
    "Prix de la réservation",
    "Statut de la réservation",
    "Date et heure de remboursement",
    "uai de l'institution",
    "nom de l'institution",
]


def serialize_collective_booking_csv_report(query: sa_orm.Query) -> str:
    output = StringIO()
    writer = csv.writer(output, dialect=csv.excel, delimiter=";", quoting=csv.QUOTE_NONNUMERIC)
    writer.writerow(COLLECTIVE_BOOKING_EXPORT_HEADER)
    for collective_booking in query.yield_per(1000):
        writer.writerow(
            (
                collective_booking.venueName,
                collective_booking.offerName,
                convert_collective_booking_dates_utc_to_venue_timezone(
                    collective_booking.stockStartDatetime, collective_booking
                ),
                collective_booking.firstName,
                collective_booking.lastName,
                collective_booking.email,
                convert_collective_booking_dates_utc_to_venue_timezone(collective_booking.bookedAt, collective_booking),
                convert_collective_booking_dates_utc_to_venue_timezone(collective_booking.usedAt, collective_booking),
                collective_booking.price,
                _get_booking_status(collective_booking.status, collective_booking.isConfirmed),
                convert_collective_booking_dates_utc_to_venue_timezone(
                    collective_booking.reimbursedAt, collective_booking
                ),
                collective_booking.institutionId,
                f"{collective_booking.institutionType} {collective_booking.institutionName}",
            )
        )

    return output.getvalue()


def serialize_collective_booking_excel_report(query: sa_orm.Query) -> bytes:
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)

    bold = workbook.add_format(utils_export.EXCEL_BOLD_FORMAT)
    currency_format = workbook.add_format(utils_export.EXCEL_CURRENCY_FORMAT)
    col_width = utils_export.EXCEL_COL_WIDTH

    worksheet = workbook.add_worksheet()
    row = 0

    for col_num, title in enumerate(COLLECTIVE_BOOKING_EXPORT_HEADER):
        worksheet.write(row, col_num, title, bold)
        worksheet.set_column(col_num, col_num, col_width)
    row = 1
    for collective_booking in query.yield_per(1000):
        worksheet.write(row, 0, collective_booking.venueName)
        worksheet.write(row, 1, collective_booking.offerName)
        worksheet.write(
            row,
            2,
            str(
                convert_collective_booking_dates_utc_to_venue_timezone(
                    collective_booking.stockStartDatetime, collective_booking
                )
            ),
        )
        worksheet.write(row, 3, collective_booking.firstName)
        worksheet.write(row, 4, collective_booking.lastName)
        worksheet.write(row, 5, collective_booking.email)
        worksheet.write(
            row,
            6,
            str(
                convert_collective_booking_dates_utc_to_venue_timezone(collective_booking.bookedAt, collective_booking)
            ),
        )
        worksheet.write(
            row,
            7,
            str(convert_collective_booking_dates_utc_to_venue_timezone(collective_booking.usedAt, collective_booking)),
        )
        worksheet.write(row, 8, collective_booking.price, currency_format)
        worksheet.write(row, 9, _get_booking_status(collective_booking.status, collective_booking.isConfirmed))
        worksheet.write(
            row,
            10,
            str(
                convert_collective_booking_dates_utc_to_venue_timezone(
                    collective_booking.reimbursedAt, collective_booking
                )
            ),
        )
        worksheet.write(row, 11, collective_booking.institutionId, currency_format)
        worksheet.write(row, 12, f"{collective_booking.institutionType} {collective_booking.institutionName}")

        row += 1

    workbook.close()
    return output.getvalue()

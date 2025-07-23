import csv
import dataclasses
import datetime
import decimal
import enum
import io

import sqlalchemy.orm as sa_orm
import xlsxwriter

from pcapi.core.educational import models
from pcapi.core.offerers import models as offerers_models
from pcapi.utils import date as date_utils
from pcapi.utils import export as utils_export


class CollectiveOfferExportHeader(enum.Enum):
    offer_name = "Nom de l'offre"
    offer_id = "Numéro de l'offre"
    offer_status = "Statut de l'offre"
    offer_location_type = "Type de localisation de l'offre"
    offer_location = "Localisation de l'offre"
    venue_common_name = "Structure"
    institution_name = "Etablissement"
    institution_postal_code = "Code postal de l'établissement"
    institution_uai = "UAI de l'établissement"
    teacher_email = "Email de l'enseignant"
    teacher_first_name = "Prénom de l'enseignant"
    teacher_last_name = "Nom de l'enseignant"
    start_datetime = "Date de début de l'évènement"
    end_datetime = "Date de fin de l'évènement"
    price = "Prix"
    number_of_tickets = "Nombre de participants"
    prebooking_datetime = "Date de préréservation de l'offre"
    booking_datetime = "Date de réservation de l'offre"
    reimbursement_datetime = "Date de remboursement"


COLLECTIVE_OFFERS_EXPORT_HEADER = [header.value for header in CollectiveOfferExportHeader]


def _format_export_datetime(date_time: datetime.datetime, timezone: str | None) -> str:
    if timezone is not None:
        date_time = date_utils.default_timezone_to_local_datetime(date_time, timezone)

    return date_time.isoformat()


FORMAT_LOCATION_TYPE = {
    None: "",  # TODO: remove this when locationType is not nullable
    models.CollectiveLocationType.SCHOOL: "En établissement scolaire",
    models.CollectiveLocationType.ADDRESS: "À une adresse précise",
    models.CollectiveLocationType.TO_BE_DEFINED: "À déterminer avec l'enseignant",
}


def _format_location(offer: models.CollectiveOffer) -> str:
    match offer.locationType:
        case models.CollectiveLocationType.ADDRESS:
            if offer.offererAddress is None:
                return ""

            return offer.offererAddress.address.fullAddress

        case models.CollectiveLocationType.TO_BE_DEFINED:
            return offer.locationComment or ""

        case _:
            return ""


@dataclasses.dataclass(kw_only=True, slots=True)
class CollectiveOfferExportData:
    offer_name: str
    offer_id: int
    offer_status: str
    offer_location_type: str
    offer_location: str
    venue_common_name: str
    institution_name: str | None = None
    institution_postal_code: str | None = None
    institution_uai: str | None = None
    teacher_email: str | None = None
    teacher_first_name: str | None = None
    teacher_last_name: str | None = None
    start_datetime: str | None = None
    end_datetime: str | None = None
    price: decimal.Decimal | None = None
    number_of_tickets: int | None = None
    prebooking_datetime: str | None = None
    booking_datetime: str | None = None
    reimbursement_datetime: str | None = None


def _get_collective_offer_export_data(
    collective_offer: models.CollectiveOffer,
) -> CollectiveOfferExportData:
    venue = collective_offer.venue
    collective_stock = collective_offer.collectiveStock
    collective_booking = collective_offer.lastBooking
    institution = collective_offer.institution

    result = CollectiveOfferExportData(
        offer_name=collective_offer.name,
        offer_id=collective_offer.id,
        offer_status=collective_offer.displayedStatus.value,
        offer_location_type=FORMAT_LOCATION_TYPE[collective_offer.locationType],
        offer_location=_format_location(collective_offer),
        venue_common_name=venue.common_name,
    )

    if collective_offer.offererAddress is not None:
        timezone = collective_offer.offererAddress.address.timezone
    elif venue.offererAddress is not None:
        timezone = venue.offererAddress.address.timezone
    else:
        timezone = None

    if institution is not None:
        result.institution_name = institution.full_name
        result.institution_postal_code = institution.postalCode
        result.institution_uai = institution.institutionId

    if collective_stock is not None:
        result.start_datetime = _format_export_datetime(collective_stock.startDatetime, timezone)
        result.end_datetime = _format_export_datetime(collective_stock.endDatetime, timezone)
        result.price = collective_stock.price
        result.number_of_tickets = collective_stock.numberOfTickets

    if collective_booking is not None:
        result.teacher_email = collective_booking.educationalRedactor.email
        result.teacher_first_name = collective_booking.educationalRedactor.firstName
        result.teacher_last_name = collective_booking.educationalRedactor.lastName

        result.prebooking_datetime = _format_export_datetime(collective_booking.dateCreated, timezone)

        if collective_booking.confirmationDate is not None:
            result.booking_datetime = _format_export_datetime(collective_booking.confirmationDate, timezone)

        if collective_booking.reimbursementDate is not None:
            result.reimbursement_datetime = _format_export_datetime(collective_booking.reimbursementDate, timezone)
    elif collective_offer.teacher:
        result.teacher_email = collective_offer.teacher.email
        result.teacher_first_name = collective_offer.teacher.firstName
        result.teacher_last_name = collective_offer.teacher.lastName

    return result


def _get_query_with_loading_for_export(
    collective_offers_query: "sa_orm.Query[models.CollectiveOffer]",
) -> "sa_orm.Query[models.CollectiveOffer]":
    return collective_offers_query.options(
        sa_orm.joinedload(models.CollectiveOffer.venue)
        .joinedload(offerers_models.Venue.offererAddress)
        .joinedload(offerers_models.OffererAddress.address),
        sa_orm.joinedload(models.CollectiveOffer.collectiveStock)
        .selectinload(models.CollectiveStock.collectiveBookings)
        .joinedload(models.CollectiveBooking.educationalRedactor),
        sa_orm.joinedload(models.CollectiveOffer.institution),
        sa_orm.joinedload(models.CollectiveOffer.offererAddress).joinedload(offerers_models.OffererAddress.address),
    )


def generate_csv_for_collective_offers(
    collective_offers_query: "sa_orm.Query[models.CollectiveOffer]",
) -> bytes:
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=COLLECTIVE_OFFERS_EXPORT_HEADER,
        dialect=csv.excel,
        delimiter=";",
        quoting=csv.QUOTE_NONNUMERIC,
    )
    writer.writeheader()

    collective_offers_query = _get_query_with_loading_for_export(collective_offers_query)

    for collective_offer in collective_offers_query.yield_per(1000):
        offer_data = _get_collective_offer_export_data(collective_offer)

        writer.writerow({header.value: getattr(offer_data, header.name) for header in CollectiveOfferExportHeader})

    return output.getvalue().encode("utf-8-sig")


def generate_excel_for_collective_offers(
    collective_offers_query: "sa_orm.Query[models.CollectiveOffer]",
) -> bytes:
    output = io.BytesIO()
    # from the xlsxwriter doc on "constant_memory" option:
    # The optimization works by flushing each row after a subsequent row is written
    options = {"constant_memory": True}
    workbook = xlsxwriter.Workbook(output, options=options)

    bold = workbook.add_format(utils_export.EXCEL_BOLD_FORMAT)
    currency_format = workbook.add_format(utils_export.EXCEL_CURRENCY_FORMAT)
    col_width = utils_export.EXCEL_COL_WIDTH

    worksheet = workbook.add_worksheet()

    # set header and columns width
    worksheet.write_row(row=0, col=0, data=COLLECTIVE_OFFERS_EXPORT_HEADER, cell_format=bold)
    worksheet.set_column(first_col=0, last_col=len(COLLECTIVE_OFFERS_EXPORT_HEADER) - 1, width=col_width)

    # set price column format
    price_index = COLLECTIVE_OFFERS_EXPORT_HEADER.index(CollectiveOfferExportHeader.price.value)
    worksheet.set_column(first_col=price_index, last_col=price_index, cell_format=currency_format)

    collective_offers_query = _get_query_with_loading_for_export(collective_offers_query)

    row = 1
    for collective_offer in collective_offers_query.yield_per(1000):
        offer_data = _get_collective_offer_export_data(collective_offer)

        worksheet.write_row(
            row=row, col=0, data=[getattr(offer_data, header.name) for header in CollectiveOfferExportHeader]
        )

        row += 1

    workbook.close()
    return output.getvalue()

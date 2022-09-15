import csv
from datetime import datetime
from enum import Enum
from io import BytesIO
from io import StringIO

from flask_sqlalchemy import BaseQuery
from pydantic import root_validator
import xlsxwriter

from pcapi.core.bookings.utils import convert_booking_dates_utc_to_venue_timezone
from pcapi.core.educational import models
from pcapi.core.educational.repository import COLLECTIVE_BOOKING_STATUS_LABELS
from pcapi.core.educational.repository import CollectiveBookingNamedTuple
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization.collective_offers_serialize import CollectiveOfferOfferVenueResponseModel
from pcapi.routes.serialization.educational_institutions import EducationalInstitutionResponseModel
from pcapi.serialization.utils import dehumanize_field
from pcapi.serialization.utils import to_camel
from pcapi.utils.date import format_into_timezoned_date
from pcapi.utils.date import format_into_utc_date
from pcapi.utils.human_ids import humanize


class CollectiveBookingRecapStatus(Enum):
    booked = "booked"
    validated = "validated"
    cancelled = "cancelled"
    reimbursed = "reimbursed"
    confirmed = "confirmed"
    pending = "pending"


class ListCollectiveBookingsQueryModel(BaseModel):
    page: int = 1
    venue_id: int | None
    event_date: str | None
    booking_status_filter: models.CollectiveBookingStatusFilter | None
    booking_period_beginning_date: str | None
    booking_period_ending_date: str | None

    _dehumanize_venue_id = dehumanize_field("venue_id")

    class Config:
        alias_generator = to_camel

    extra = "forbid"

    @root_validator(pre=True)
    def booking_period_or_event_date_required(cls, values):  # type: ignore [no-untyped-def] # pylint: disable=no-self-argument
        event_date = values.get("eventDate")
        booking_period_beginning_date = values.get("bookingPeriodBeginningDate")
        booking_period_ending_date = values.get("bookingPeriodEndingDate")
        if not event_date and not (booking_period_beginning_date and booking_period_ending_date):
            raise ApiErrors(
                errors={
                    "eventDate": ["Ce champ est obligatoire si aucune période n'est renseignée."],
                    "bookingPeriodEndingDate": ["Ce champ est obligatoire si la date d'évènement n'est renseignée"],
                    "bookingPeriodBeginningDate": ["Ce champ est obligatoire si la date d'évènement n'est renseignée"],
                }
            )
        return values


class BookingStatusHistoryResponseModel(BaseModel):
    status: str
    date: str


class CollectiveBookingCollectiveStockResponseModel(BaseModel):
    offer_name: str
    offer_identifier: str
    event_beginning_datetime: str
    offer_isbn: str | None
    offer_is_educational: bool
    number_of_tickets: int


class EducationalRedactorResponseModel(BaseModel):
    lastname: str
    firstname: str
    email: str
    phonenumber: str | None


class CollectiveBookingResponseModel(BaseModel):
    stock: CollectiveBookingCollectiveStockResponseModel
    institution: EducationalInstitutionResponseModel
    booking_token: str | None
    booking_date: str
    booking_status: str
    booking_is_duo = False
    booking_amount: float
    booking_status_history: list[BookingStatusHistoryResponseModel]
    booking_identifier: str


class ListCollectiveBookingsResponseModel(BaseModel):
    bookingsRecap: list[CollectiveBookingResponseModel]
    page: int
    pages: int
    total: int

    class Config:
        json_encoders = {datetime: format_into_utc_date}
        alias_generator = to_camel


def _get_booking_status(status: models.CollectiveBookingStatus, is_confirmed: bool) -> str:
    cancellation_limit_date_exists_and_past = is_confirmed
    if cancellation_limit_date_exists_and_past and status == models.CollectiveBookingStatus.CONFIRMED:
        return COLLECTIVE_BOOKING_STATUS_LABELS["confirmed"]
    return COLLECTIVE_BOOKING_STATUS_LABELS[status]


def build_status_history(
    booking_status: models.CollectiveBookingStatus,
    booking_date: datetime,
    cancellation_date: datetime | None,
    cancellation_limit_date: datetime | None,
    payment_date: datetime | None,
    date_used: datetime | None,
    confirmation_date: datetime | None,
    is_confirmed: bool | None,
) -> list[BookingStatusHistoryResponseModel]:

    if booking_status == models.CollectiveBookingStatus.PENDING:
        serialized_booking_status_history = [
            _serialize_collective_booking_status_info(CollectiveBookingRecapStatus.pending, booking_date)
        ]
        return serialized_booking_status_history

    if booking_status == models.CollectiveBookingStatus.CANCELLED and not (confirmation_date or booking_date):
        serialized_booking_status_history = [
            _serialize_collective_booking_status_info(CollectiveBookingRecapStatus.cancelled, cancellation_date)
        ]
        return serialized_booking_status_history

    serialized_booking_status_history = [
        _serialize_collective_booking_status_info(
            CollectiveBookingRecapStatus.booked, confirmation_date or booking_date
        )
    ]
    if is_confirmed and confirmation_date is not None:
        serialized_booking_status_history.append(
            _serialize_collective_booking_status_info(CollectiveBookingRecapStatus.confirmed, cancellation_limit_date)
        )
    if date_used:
        serialized_booking_status_history.append(
            _serialize_collective_booking_status_info(CollectiveBookingRecapStatus.validated, date_used)
        )

    if cancellation_date:
        serialized_booking_status_history.append(
            _serialize_collective_booking_status_info(CollectiveBookingRecapStatus.cancelled, cancellation_date)
        )
    if payment_date:
        serialized_booking_status_history.append(
            _serialize_collective_booking_status_info(CollectiveBookingRecapStatus.reimbursed, payment_date)
        )
    return serialized_booking_status_history


def _serialize_collective_booking_status_info(
    collective_booking_status: CollectiveBookingRecapStatus, collective_booking_status_date: datetime | None
) -> BookingStatusHistoryResponseModel:

    serialized_collective_booking_status_date = (
        format_into_timezoned_date(collective_booking_status_date) if collective_booking_status_date else None
    )

    return BookingStatusHistoryResponseModel(
        status=collective_booking_status.value,
        date=serialized_collective_booking_status_date,
    )


def serialize_collective_booking_stock(
    collective_booking: CollectiveBookingNamedTuple,
) -> CollectiveBookingCollectiveStockResponseModel:
    return CollectiveBookingCollectiveStockResponseModel(
        offer_name=collective_booking.offerName,
        offer_identifier=humanize(collective_booking.offerId),
        event_beginning_datetime=collective_booking.stockBeginningDatetime.isoformat(),
        offer_is_educational=True,
        number_of_tickets=collective_booking.numberOfTickets,
    )


def serialize_collective_booking_institution(
    collective_booking: CollectiveBookingNamedTuple,
) -> EducationalInstitutionResponseModel:
    return EducationalInstitutionResponseModel(
        id=collective_booking.institutionId,
        institutionType=collective_booking.institutionType,
        name=collective_booking.institutionName,
        postalCode=collective_booking.institutionPostalCode,
        city=collective_booking.institutionCity,
        phoneNumber=collective_booking.institutionPhoneNumber,
    )


def _serialize_collective_booking_recap_status(
    collective_booking: CollectiveBookingNamedTuple,
) -> CollectiveBookingRecapStatus:
    if collective_booking.status == models.CollectiveBookingStatus.PENDING:
        return CollectiveBookingRecapStatus.pending
    if collective_booking.status == models.CollectiveBookingStatus.REIMBURSED:
        return CollectiveBookingRecapStatus.reimbursed
    if collective_booking.status == models.CollectiveBookingStatus.CANCELLED:
        return CollectiveBookingRecapStatus.cancelled
    if collective_booking.status == models.CollectiveBookingStatus.USED:
        return CollectiveBookingRecapStatus.validated
    if collective_booking.isConfirmed:
        return CollectiveBookingRecapStatus.confirmed
    return CollectiveBookingRecapStatus.booked


def serialize_collective_booking(collective_booking: CollectiveBookingNamedTuple) -> CollectiveBookingResponseModel:
    return CollectiveBookingResponseModel(
        stock=serialize_collective_booking_stock(collective_booking),
        institution=serialize_collective_booking_institution(collective_booking),
        booking_date=collective_booking.bookedAt.isoformat(),
        booking_status=_serialize_collective_booking_recap_status(collective_booking).value,
        booking_amount=collective_booking.bookingAmount,
        booking_status_history=build_status_history(
            booking_status=collective_booking.status,
            booking_date=collective_booking.bookedAt,
            cancellation_date=collective_booking.cancelledAt,
            cancellation_limit_date=collective_booking.cancellationLimitDate,
            payment_date=collective_booking.reimbursedAt,
            date_used=collective_booking.usedAt,
            confirmation_date=collective_booking.confirmationDate,
            is_confirmed=collective_booking.isConfirmed,
        ),
        booking_identifier=humanize(collective_booking.collectiveBookingId),
    )


COLLECTIVE_BOOKING_EXPORT_HEADER = [
    "Lieu",
    "Nom de l'offre",
    "Date de l'évènement",
    "Nom et prénom du bénéficiaire",
    "Email du bénéficiaire",
    "Date et heure de réservation",
    "Date et heure de validation",
    "Prix de la réservation",
    "Statut de la réservation",
    "Date et heure de remboursement",
]


def serialize_collective_booking_csv_report(query: BaseQuery) -> str:
    output = StringIO()
    writer = csv.writer(output, dialect=csv.excel, delimiter=";", quoting=csv.QUOTE_NONNUMERIC)
    writer.writerow(COLLECTIVE_BOOKING_EXPORT_HEADER)
    for collective_booking in query.yield_per(1000):
        writer.writerow(
            (
                collective_booking.venueName,
                collective_booking.offerName,
                convert_booking_dates_utc_to_venue_timezone(
                    collective_booking.stockBeginningDatetime, collective_booking
                ),
                f"{collective_booking.lastName} {collective_booking.firstName}",
                collective_booking.email,
                convert_booking_dates_utc_to_venue_timezone(collective_booking.bookedAt, collective_booking),
                convert_booking_dates_utc_to_venue_timezone(collective_booking.usedAt, collective_booking),
                collective_booking.price,
                _get_booking_status(collective_booking.status, collective_booking.isConfirmed),
                convert_booking_dates_utc_to_venue_timezone(collective_booking.reimbursedAt, collective_booking),
            )
        )

    return output.getvalue()


def serialize_collective_booking_excel_report(query: BaseQuery) -> bytes:
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)

    bold = workbook.add_format({"bold": 1})
    currency_format = workbook.add_format({"num_format": "###0.00[$€-fr-FR]"})
    col_width = 18

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
                convert_booking_dates_utc_to_venue_timezone(
                    collective_booking.stockBeginningDatetime, collective_booking
                )
            ),
        )
        worksheet.write(row, 3, f"{collective_booking.lastName} {collective_booking.firstName}")
        worksheet.write(row, 4, collective_booking.email)
        worksheet.write(
            row, 5, str(convert_booking_dates_utc_to_venue_timezone(collective_booking.bookedAt, collective_booking))
        )
        worksheet.write(
            row, 6, str(convert_booking_dates_utc_to_venue_timezone(collective_booking.usedAt, collective_booking))
        )
        worksheet.write(row, 7, collective_booking.price, currency_format)
        worksheet.write(row, 8, _get_booking_status(collective_booking.status, collective_booking.isConfirmed))
        worksheet.write(
            row,
            9,
            str(convert_booking_dates_utc_to_venue_timezone(collective_booking.reimbursedAt, collective_booking)),
        )
        row += 1

    workbook.close()
    return output.getvalue()


class CollectiveBookingEducationalRedactorResponseModel(BaseModel):
    id: int
    email: str
    civility: str | None
    firstName: str | None
    lastName: str | None

    class Config:
        orm_mode = True


class CollectiveBookingByIdResponseModel(BaseModel):
    id: int
    offerVenue: CollectiveOfferOfferVenueResponseModel
    beginningDatetime: datetime
    students: list[models.StudentLevels]
    price: int
    educationalInstitution: EducationalInstitutionResponseModel
    educationalRedactor: CollectiveBookingEducationalRedactorResponseModel
    numberOfTickets: int
    venuePostalCode: str | None

    class Config:
        orm_mode = True

    @classmethod
    def from_orm(cls, booking: models.CollectiveBooking) -> "CollectiveBookingByIdResponseModel":
        return cls(
            id=booking.id,
            offerVenue=booking.collectiveStock.collectiveOffer.offerVenue,
            beginningDatetime=booking.collectiveStock.beginningDatetime,
            students=booking.collectiveStock.collectiveOffer.students,
            price=booking.collectiveStock.price,
            educationalInstitution=booking.educationalInstitution,
            educationalRedactor=booking.educationalRedactor,
            numberOfTickets=booking.collectiveStock.numberOfTickets,
            venuePostalCode=booking.venue.postalCode,
        )

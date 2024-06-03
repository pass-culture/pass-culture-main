import csv
from datetime import datetime
import decimal
from enum import Enum
from io import BytesIO
from io import StringIO
import typing

from flask_sqlalchemy import BaseQuery
from pydantic.v1 import root_validator
import xlsxwriter

from pcapi.core.bookings.utils import convert_booking_dates_utc_to_venue_timezone
from pcapi.core.bookings.utils import convert_real_booking_dates_utc_to_venue_timezone
from pcapi.core.educational import models
from pcapi.core.educational import repository
from pcapi.core.finance.models import BankAccountApplicationStatus
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization.collective_offers_serialize import CollectiveOfferOfferVenueResponseModel
from pcapi.routes.serialization.educational_institutions import EducationalInstitutionResponseModel
from pcapi.serialization.utils import to_camel
from pcapi.utils.date import format_into_utc_date
from pcapi.utils.date import isoformat


class CollectiveBookingRecapStatus(Enum):
    booked = "booked"
    validated = "validated"
    cancelled = "cancelled"
    reimbursed = "reimbursed"
    confirmed = "confirmed"
    pending = "pending"


class CollectiveBookingBankAccountStatus(Enum):
    ACCEPTED = "ACCEPTED"
    DRAFT = "DRAFT"
    MISSING = "MISSING"
    REJECTED = "REJECTED"


class ListCollectiveBookingsQueryModel(BaseModel):
    page: int = 1
    venue_id: int | None
    event_date: str | None
    booking_status_filter: models.CollectiveBookingStatusFilter | None
    booking_period_beginning_date: str | None
    booking_period_ending_date: str | None

    class Config:
        alias_generator = to_camel
        extra = "forbid"

    @root_validator(pre=True)
    def booking_period_or_event_date_required(cls, values: dict) -> dict:
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
    offer_id: int
    event_beginning_datetime: str
    event_start_datetime: str
    event_end_datetime: str | None
    offer_isbn: str | None
    offer_is_educational: bool
    number_of_tickets: int
    booking_limit_datetime: str | None

    class Config:
        alias_generator = to_camel


class EducationalRedactorResponseModel(BaseModel):
    lastname: str
    firstname: str
    email: str
    phonenumber: str | None


class CollectiveBookingResponseModel(BaseModel):
    stock: CollectiveBookingCollectiveStockResponseModel
    institution: EducationalInstitutionResponseModel
    booking_id: str
    booking_token: str | None
    booking_date: str
    booking_cancellation_limit_date: str
    booking_confirmation_date: str | None
    booking_confirmation_limit_date: str
    booking_status: str
    booking_is_duo = False
    booking_amount: float
    booking_status_history: list[BookingStatusHistoryResponseModel]
    booking_cancellation_reason: models.CollectiveBookingCancellationReasons | None

    class Config:
        alias_generator = to_camel


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
        return repository.COLLECTIVE_BOOKING_STATUS_LABELS["confirmed"]
    return repository.COLLECTIVE_BOOKING_STATUS_LABELS[status]


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
    serialized_booking_status_history = []
    if booking_status == models.CollectiveBookingStatus.PENDING:
        serialized_booking_status_history = [
            _serialize_collective_booking_status_info(CollectiveBookingRecapStatus.pending, booking_date),
        ]

    elif booking_status == models.CollectiveBookingStatus.CONFIRMED:
        serialized_booking_status_history = [
            _serialize_collective_booking_status_info(CollectiveBookingRecapStatus.pending, booking_date),
            _serialize_collective_booking_status_info(CollectiveBookingRecapStatus.booked, confirmation_date),
        ]
        if is_confirmed:
            serialized_booking_status_history.append(
                _serialize_collective_booking_status_info(
                    CollectiveBookingRecapStatus.confirmed, cancellation_limit_date
                )
            )
    elif booking_status == models.CollectiveBookingStatus.USED:
        serialized_booking_status_history = [
            _serialize_collective_booking_status_info(CollectiveBookingRecapStatus.pending, booking_date),
            _serialize_collective_booking_status_info(CollectiveBookingRecapStatus.booked, confirmation_date),
            _serialize_collective_booking_status_info(CollectiveBookingRecapStatus.confirmed, cancellation_limit_date),
            _serialize_collective_booking_status_info(CollectiveBookingRecapStatus.validated, date_used),
        ]
    elif booking_status == models.CollectiveBookingStatus.REIMBURSED:
        serialized_booking_status_history = [
            _serialize_collective_booking_status_info(CollectiveBookingRecapStatus.pending, booking_date),
            _serialize_collective_booking_status_info(CollectiveBookingRecapStatus.booked, confirmation_date),
            _serialize_collective_booking_status_info(CollectiveBookingRecapStatus.confirmed, cancellation_limit_date),
            _serialize_collective_booking_status_info(CollectiveBookingRecapStatus.validated, date_used),
            _serialize_collective_booking_status_info(CollectiveBookingRecapStatus.reimbursed, payment_date),
        ]
    elif booking_status == models.CollectiveBookingStatus.CANCELLED:
        serialized_booking_status_history = [
            _serialize_collective_booking_status_info(CollectiveBookingRecapStatus.pending, booking_date),
        ]
        if confirmation_date:
            serialized_booking_status_history.append(
                _serialize_collective_booking_status_info(CollectiveBookingRecapStatus.booked, confirmation_date),
            )
            if is_confirmed:
                serialized_booking_status_history.append(
                    _serialize_collective_booking_status_info(
                        CollectiveBookingRecapStatus.confirmed, cancellation_limit_date
                    ),
                )
                if date_used:
                    serialized_booking_status_history.append(
                        _serialize_collective_booking_status_info(CollectiveBookingRecapStatus.validated, date_used),
                    )
        serialized_booking_status_history.append(
            _serialize_collective_booking_status_info(CollectiveBookingRecapStatus.cancelled, cancellation_date),
        )
    return serialized_booking_status_history


def _serialize_collective_booking_status_info(
    collective_booking_status: CollectiveBookingRecapStatus, collective_booking_status_date: datetime | None
) -> BookingStatusHistoryResponseModel:
    serialized_collective_booking_status_date = (
        isoformat(collective_booking_status_date) if collective_booking_status_date else None
    )

    return BookingStatusHistoryResponseModel(
        status=collective_booking_status.value,
        date=serialized_collective_booking_status_date,  # type: ignore[arg-type]
    )


def serialize_collective_booking_stock(
    collective_booking: models.CollectiveBooking,
) -> CollectiveBookingCollectiveStockResponseModel:
    return CollectiveBookingCollectiveStockResponseModel(  # type: ignore[call-arg]
        offerName=collective_booking.collectiveStock.collectiveOffer.name,
        offerId=collective_booking.collectiveStock.collectiveOfferId,
        eventBeginningDatetime=typing.cast(
            datetime,
            convert_real_booking_dates_utc_to_venue_timezone(
                collective_booking.collectiveStock.beginningDatetime, collective_booking
            ),
        ).isoformat(),
        eventStartDatetime=typing.cast(
            datetime,
            convert_real_booking_dates_utc_to_venue_timezone(
                collective_booking.collectiveStock.startDatetime, collective_booking
            ),
        ).isoformat(),
        eventEndDatetime=typing.cast(
            datetime,
            convert_real_booking_dates_utc_to_venue_timezone(
                collective_booking.collectiveStock.endDatetime, collective_booking
            ),
        ).isoformat(),
        offerIsEducational=True,
        numberOfTickets=collective_booking.collectiveStock.numberOfTickets,
        bookingLimitDatetime=typing.cast(
            datetime,
            convert_real_booking_dates_utc_to_venue_timezone(
                collective_booking.collectiveStock.bookingLimitDatetime, collective_booking
            ),
        ).isoformat(),
    )


def serialize_collective_booking_institution(
    collective_booking: models.CollectiveBooking,
) -> EducationalInstitutionResponseModel:
    return EducationalInstitutionResponseModel(
        id=collective_booking.educationalInstitution.id,
        institutionType=collective_booking.educationalInstitution.institutionType,
        name=collective_booking.educationalInstitution.name,
        postalCode=collective_booking.educationalInstitution.postalCode,
        city=collective_booking.educationalInstitution.city,
        phoneNumber=collective_booking.educationalInstitution.phoneNumber,
        institutionId=collective_booking.educationalInstitution.institutionId,
    )


def _serialize_collective_booking_recap_status(
    collective_booking: models.CollectiveBooking,
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


def serialize_collective_booking(collective_booking: models.CollectiveBooking) -> CollectiveBookingResponseModel:
    return CollectiveBookingResponseModel(  # type: ignore[call-arg]
        stock=serialize_collective_booking_stock(collective_booking),
        institution=serialize_collective_booking_institution(collective_booking),
        bookingId=collective_booking.id,
        bookingDate=typing.cast(
            datetime,
            convert_real_booking_dates_utc_to_venue_timezone(collective_booking.dateCreated, collective_booking),
        ).isoformat(),
        bookingCancellationLimitDate=typing.cast(
            datetime,
            convert_real_booking_dates_utc_to_venue_timezone(
                collective_booking.cancellationLimitDate, collective_booking
            ),
        ).isoformat(),
        bookingConfirmationDate=(
            typing.cast(
                datetime,
                convert_real_booking_dates_utc_to_venue_timezone(
                    collective_booking.confirmationDate, collective_booking
                ),
            ).isoformat()
            if collective_booking.confirmationDate
            else ""
        ),
        bookingConfirmationLimitDate=typing.cast(
            datetime,
            convert_real_booking_dates_utc_to_venue_timezone(
                collective_booking.confirmationLimitDate, collective_booking
            ),
        ).isoformat(),
        bookingStatus=_serialize_collective_booking_recap_status(collective_booking).value,
        bookingAmount=collective_booking.collectiveStock.price,
        bookingStatusHistory=build_status_history(
            booking_status=collective_booking.status,
            booking_date=typing.cast(
                datetime,
                convert_real_booking_dates_utc_to_venue_timezone(collective_booking.dateCreated, collective_booking),
            ),
            cancellation_date=convert_real_booking_dates_utc_to_venue_timezone(
                collective_booking.cancellationDate, collective_booking
            ),
            cancellation_limit_date=convert_real_booking_dates_utc_to_venue_timezone(
                collective_booking.cancellationLimitDate, collective_booking
            ),
            payment_date=convert_real_booking_dates_utc_to_venue_timezone(
                collective_booking.reimbursementDate, collective_booking
            ),
            date_used=convert_real_booking_dates_utc_to_venue_timezone(collective_booking.dateUsed, collective_booking),
            confirmation_date=convert_real_booking_dates_utc_to_venue_timezone(
                collective_booking.confirmationDate, collective_booking
            ),
            is_confirmed=collective_booking.isConfirmed,
        ),
        bookingCancellationReason=collective_booking.cancellationReason,
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
    "uai de l'institution",
    "nom de l'institution",
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
                collective_booking.institutionId,
                f"{collective_booking.institutionType} {collective_booking.institutionName}",
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
        worksheet.write(row, 10, collective_booking.institutionId, currency_format)
        worksheet.write(row, 11, f"{collective_booking.institutionType} {collective_booking.institutionName}")

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
    startDatetime: datetime
    endDatetime: datetime
    students: list[models.StudentLevels]
    price: decimal.Decimal
    educationalInstitution: EducationalInstitutionResponseModel
    educationalRedactor: CollectiveBookingEducationalRedactorResponseModel
    numberOfTickets: int
    venuePostalCode: str | None
    isCancellable: bool
    bankAccountStatus: CollectiveBookingBankAccountStatus
    venueDMSApplicationId: int | None
    venueId: int
    offererId: int

    class Config:
        orm_mode = True

    @classmethod
    def from_orm(cls, booking: models.CollectiveBooking) -> "CollectiveBookingByIdResponseModel":
        ds_application_id = None

        bank_account = repository.get_booking_related_bank_account(booking.id)
        bank_account_status = CollectiveBookingBankAccountStatus.MISSING
        if bank_account:
            ds_application_id = bank_account.dsApplicationId
            match bank_account.status:
                case BankAccountApplicationStatus.ACCEPTED:
                    bank_account_status = CollectiveBookingBankAccountStatus.ACCEPTED
                case (BankAccountApplicationStatus.WITHOUT_CONTINUATION, BankAccountApplicationStatus.REFUSED):
                    bank_account_status = CollectiveBookingBankAccountStatus.REJECTED
                case _:
                    bank_account_status = CollectiveBookingBankAccountStatus.DRAFT

        return cls(
            id=booking.id,
            offerVenue=booking.collectiveStock.collectiveOffer.offerVenue,  # type: ignore[arg-type]
            beginningDatetime=booking.collectiveStock.beginningDatetime,
            startDatetime=booking.collectiveStock.startDatetime,
            endDatetime=booking.collectiveStock.endDatetime,
            students=booking.collectiveStock.collectiveOffer.students,
            price=booking.collectiveStock.price,
            educationalInstitution=booking.educationalInstitution,
            educationalRedactor=booking.educationalRedactor,
            numberOfTickets=booking.collectiveStock.numberOfTickets,
            venuePostalCode=booking.venue.postalCode,
            isCancellable=booking.is_cancellable_from_offerer,
            bankAccountStatus=bank_account_status,
            venueDMSApplicationId=ds_application_id,
            venueId=booking.venueId,
            offererId=booking.venue.managingOffererId,
        )

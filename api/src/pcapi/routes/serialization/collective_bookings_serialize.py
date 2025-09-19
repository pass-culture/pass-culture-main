import decimal
import typing
from datetime import datetime
from enum import Enum

from pydantic.v1 import root_validator

from pcapi.core.bookings.utils import convert_real_booking_dates_utc_to_venue_timezone
from pcapi.core.educational import models
from pcapi.core.educational import repository
from pcapi.core.finance.models import BankAccountApplicationStatus
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization import to_camel
from pcapi.routes.serialization.collective_offers_serialize import CollectiveOfferOfferVenueResponseModel
from pcapi.routes.serialization.educational_institutions import EducationalInstitutionResponseModel
from pcapi.utils.date import format_into_utc_date


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
    event_start_datetime: str
    event_end_datetime: str
    offer_ean: str | None
    offer_is_educational: bool
    number_of_tickets: int
    booking_limit_datetime: str

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


def build_status_history(
    *,
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
        collective_booking_status_date.isoformat() if collective_booking_status_date else None
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

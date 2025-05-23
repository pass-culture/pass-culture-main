import typing
from datetime import date
from datetime import datetime
from enum import Enum

from pydantic.v1 import root_validator

from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingExportType
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.bookings.models import BookingStatusFilter
from pcapi.core.bookings.utils import _apply_departement_timezone
from pcapi.core.bookings.utils import convert_collective_booking_dates_utc_to_venue_timezone
from pcapi.domain.booking_recap.utils import get_booking_token
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import to_camel


class BookingRecapResponseBeneficiaryModel(BaseModel):
    email: str | None
    firstname: str | None
    lastname: str | None
    phonenumber: str | None


class BookingRecapResponseStockModel(BaseModel):
    event_beginning_datetime: datetime | None
    offer_id: int
    offer_is_educational: bool
    offer_ean: str | None
    offer_name: str

    class Config:
        alias_generator = to_camel


class BookingRecapStatus(Enum):
    booked = "booked"
    validated = "validated"
    cancelled = "cancelled"
    reimbursed = "reimbursed"
    confirmed = "confirmed"
    pending = "pending"


class BookingRecapResponseBookingStatusHistoryModel(BaseModel):
    status: BookingRecapStatus
    date: datetime | None


class BookingRecapResponseModel(BaseModel):
    beneficiary: BookingRecapResponseBeneficiaryModel
    booking_amount: float
    booking_date: datetime
    booking_is_duo: bool
    booking_status: BookingRecapStatus
    booking_status_history: list[BookingRecapResponseBookingStatusHistoryModel]
    booking_price_category_label: str | None
    booking_token: str | None
    stock: BookingRecapResponseStockModel

    class Config:
        alias_generator = to_camel


class UserHasBookingResponse(BaseModel):
    hasBookings: bool


class ListBookingsResponseModel(BaseModel):
    bookingsRecap: list[BookingRecapResponseModel]
    page: int
    pages: int
    total: int


def _serialize_booking_status_info(
    booking_status: BookingRecapStatus, booking_status_date: datetime
) -> BookingRecapResponseBookingStatusHistoryModel:
    serialized_booking_status_date = booking_status_date.isoformat() if booking_status_date else None

    return BookingRecapResponseBookingStatusHistoryModel(
        status=booking_status,
        date=serialized_booking_status_date,  # type: ignore[arg-type]
    )


def serialize_booking_status_history(
    booking: Booking,
) -> list[BookingRecapResponseBookingStatusHistoryModel]:
    serialized_booking_status_history = [
        _serialize_booking_status_info(
            BookingRecapStatus.booked,
            typing.cast(datetime, convert_collective_booking_dates_utc_to_venue_timezone(booking.bookedAt, booking)),
        )
    ]

    if booking.usedAt:
        serialized_booking_status_history.append(
            _serialize_booking_status_info(
                BookingRecapStatus.validated,
                typing.cast(datetime, convert_collective_booking_dates_utc_to_venue_timezone(booking.usedAt, booking)),
            )
        )

    if booking.cancelledAt:
        serialized_booking_status_history.append(
            _serialize_booking_status_info(
                BookingRecapStatus.cancelled,
                typing.cast(
                    datetime,
                    convert_collective_booking_dates_utc_to_venue_timezone(booking.cancelledAt, booking=booking),
                ),
            )
        )
    if booking.reimbursedAt:
        serialized_booking_status_history.append(
            _serialize_booking_status_info(
                BookingRecapStatus.reimbursed,
                typing.cast(
                    datetime, convert_collective_booking_dates_utc_to_venue_timezone(booking.reimbursedAt, booking)
                ),
            )
        )
    return serialized_booking_status_history


def serialize_bookings(booking: Booking) -> BookingRecapResponseModel:
    stock_beginning_datetime = _apply_departement_timezone(booking.stockBeginningDatetime, booking.venueDepartmentCode)
    booking_date = convert_collective_booking_dates_utc_to_venue_timezone(booking.bookedAt, booking)
    serialized_booking_recap = BookingRecapResponseModel(  # type: ignore[call-arg]
        stock={  # type: ignore[arg-type]
            "offerName": booking.offerName,
            "offerId": booking.offerId,
            "eventBeginningDatetime": stock_beginning_datetime.isoformat() if stock_beginning_datetime else None,
            "offerEan": booking.offerEan,
            "offerIsEducational": False,
        },
        beneficiary={  # type: ignore[arg-type]
            "lastname": booking.beneficiaryLastname,
            "firstname": booking.beneficiaryFirstname,
            "email": booking.beneficiaryEmail,
            "phonenumber": booking.beneficiaryPhoneNumber,
        },
        bookingToken=get_booking_token(
            booking.bookingToken,
            booking.status,
            bool(booking.isExternal),
            _apply_departement_timezone(booking.stockBeginningDatetime, booking.venueDepartmentCode),
        ),
        bookingDate=booking_date.isoformat() if booking_date else None,
        bookingStatus=build_booking_status(booking),
        bookingIsDuo=booking.quantity == 2,
        bookingAmount=booking.bookingAmount,
        bookingPriceCategoryLabel=booking.priceCategoryLabel,
        bookingStatusHistory=serialize_booking_status_history(booking),
    )

    return serialized_booking_recap


class BookingsExportStatusFilter(Enum):
    VALIDATED = "validated"
    ALL = "all"


class BookingsExportQueryModel(BaseModel):
    status: BookingsExportStatusFilter
    event_date: date

    class config:
        alias_generator = to_camel
        extra = "forbid"


class ListBookingsQueryModel(BaseModel):
    page: int = 1
    offerer_id: int | None
    venue_id: int | None
    offer_id: int | None
    event_date: date | None
    booking_status_filter: BookingStatusFilter | None
    booking_period_beginning_date: date | None
    booking_period_ending_date: date | None
    offerer_address_id: int | None
    export_type: BookingExportType | None

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


def build_booking_status(booking: Booking) -> BookingRecapStatus:
    if booking.status == BookingStatus.REIMBURSED:
        return BookingRecapStatus.reimbursed
    if booking.status == BookingStatus.CANCELLED:
        return BookingRecapStatus.cancelled
    if booking.status == BookingStatus.USED:
        return BookingRecapStatus.validated
    if booking.isConfirmed:
        return BookingRecapStatus.confirmed
    return BookingRecapStatus.booked


class EventDateScheduleAndPriceCategoriesCountModel(BaseModel):
    event_date: date
    schedule_count: int
    price_categories_count: int

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True


class EventDatesInfos(BaseModel):
    __root__: list[EventDateScheduleAndPriceCategoriesCountModel]

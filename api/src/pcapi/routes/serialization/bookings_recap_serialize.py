import typing
from datetime import date
from datetime import datetime
from enum import Enum

import pydantic as pydantic_v2

from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingExportType
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.bookings.models import BookingStatusFilter
from pcapi.core.bookings.repository import get_booking_token
from pcapi.core.bookings.utils import _apply_departement_timezone
from pcapi.core.bookings.utils import convert_booking_dates_utc_to_venue_timezone
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.serialization import HttpBodyModel
from pcapi.routes.serialization import HttpQueryParamsModel
from pcapi.serialization.exceptions import PydanticError


class BookingRecapStatus(Enum):
    booked = "booked"
    validated = "validated"
    cancelled = "cancelled"
    reimbursed = "reimbursed"
    confirmed = "confirmed"
    pending = "pending"


class BookingsExportStatusFilter(Enum):
    VALIDATED = "validated"
    ALL = "all"


# Body models
class BookingRecapResponseBeneficiaryModel(HttpBodyModel):
    email: pydantic_v2.EmailStr | None = None
    firstname: str | None = None
    lastname: str | None = None
    phonenumber: str | None = None


class BookingRecapResponseStockModel(HttpBodyModel):
    event_beginning_datetime: datetime | None = None
    offer_id: int
    offer_is_educational: bool
    offer_ean: str | None = None
    offer_name: str


class BookingRecapResponseBookingStatusHistoryModel(HttpBodyModel):
    status: BookingRecapStatus
    date: datetime | None = None

    # TODO: (tcoudray-pass, 16/12/25) Remove when tz are handled in front
    model_config = pydantic_v2.ConfigDict(json_encoders={datetime: datetime.isoformat})


class BookingRecapResponseModel(HttpBodyModel):
    beneficiary: BookingRecapResponseBeneficiaryModel
    booking_amount: float
    booking_date: datetime
    booking_is_duo: bool
    booking_status: BookingRecapStatus
    booking_status_history: list[BookingRecapResponseBookingStatusHistoryModel]
    booking_price_category_label: str | None = None
    booking_token: str | None = None
    stock: BookingRecapResponseStockModel

    # TODO: (tcoudray-pass, 16/12/25) Remove when tz are handled in front
    model_config = pydantic_v2.ConfigDict(json_encoders={datetime: datetime.isoformat})


class UserHasBookingResponse(HttpBodyModel):
    has_bookings: bool


class ListBookingsResponseModel(HttpBodyModel):
    bookingsRecap: list[BookingRecapResponseModel]
    page: int
    pages: int
    total: int


class EventDateScheduleAndPriceCategoriesCountModel(HttpBodyModel):
    event_date: date
    schedule_count: int
    price_categories_count: int


class EventDatesInfos(pydantic_v2.RootModel):
    root: list[EventDateScheduleAndPriceCategoriesCountModel]


# Query models
class BookingsExportQueryModel(HttpQueryParamsModel):
    status: BookingsExportStatusFilter
    event_date: date


class ListBookingsQueryModel(HttpQueryParamsModel):
    page: int = 1
    offerer_id: int | None = None
    venue_id: int | None = None
    offer_id: int | None = None
    event_date: date | None = None
    booking_status_filter: BookingStatusFilter | None = None
    booking_period_beginning_date: date | None = None
    booking_period_ending_date: date | None = None
    offerer_address_id: int | None = None
    export_type: BookingExportType | None = None

    @pydantic_v2.model_validator(mode="before")
    @classmethod
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

    @pydantic_v2.field_validator("booking_period_beginning_date", "booking_period_ending_date")
    def validate_booking_period_date(cls, booking_period_date: date | None) -> date | None:
        # Conversion to local timezone may crash when it would shift before 0001-01-01
        if booking_period_date and booking_period_date < date(1, 1, 2):
            raise PydanticError("invalid date")
        return booking_period_date


# Serializers
def _serialize_booking_status_info(
    booking_status: BookingRecapStatus, booking_status_date: datetime
) -> BookingRecapResponseBookingStatusHistoryModel:
    return BookingRecapResponseBookingStatusHistoryModel(
        status=booking_status,
        date=booking_status_date,
    )


def serialize_booking_status_history(
    booking: Booking,
) -> list[BookingRecapResponseBookingStatusHistoryModel]:
    serialized_booking_status_history = [
        _serialize_booking_status_info(
            BookingRecapStatus.booked,
            typing.cast(datetime, convert_booking_dates_utc_to_venue_timezone(booking.bookedAt, booking)),
        )
    ]

    if booking.usedAt:
        serialized_booking_status_history.append(
            _serialize_booking_status_info(
                BookingRecapStatus.validated,
                typing.cast(datetime, convert_booking_dates_utc_to_venue_timezone(booking.usedAt, booking)),
            )
        )

    if booking.cancelledAt:
        serialized_booking_status_history.append(
            _serialize_booking_status_info(
                BookingRecapStatus.cancelled,
                typing.cast(
                    datetime,
                    convert_booking_dates_utc_to_venue_timezone(booking.cancelledAt, booking=booking),
                ),
            )
        )
    if booking.reimbursedAt:
        serialized_booking_status_history.append(
            _serialize_booking_status_info(
                BookingRecapStatus.reimbursed,
                typing.cast(datetime, convert_booking_dates_utc_to_venue_timezone(booking.reimbursedAt, booking)),
            )
        )
    return serialized_booking_status_history


def serialize_bookings(booking: Booking) -> BookingRecapResponseModel:
    stock_beginning_datetime = _apply_departement_timezone(booking.stockBeginningDatetime, booking.venueDepartmentCode)
    booking_date = convert_booking_dates_utc_to_venue_timezone(booking.bookedAt, booking)
    serialized_booking_recap = BookingRecapResponseModel(
        stock=BookingRecapResponseStockModel(
            offer_name=booking.offerName,
            offer_id=booking.offerId,
            event_beginning_datetime=stock_beginning_datetime,
            offer_ean=booking.offerEan,
            offer_is_educational=False,
        ),
        beneficiary=BookingRecapResponseBeneficiaryModel(
            lastname=booking.beneficiaryLastname,
            firstname=booking.beneficiaryFirstname,
            email=booking.beneficiaryEmail,
            phonenumber=booking.beneficiaryPhoneNumber,
        ),
        booking_token=get_booking_token(
            booking.bookingToken,
            booking.status,
            bool(booking.isExternal),
            _apply_departement_timezone(booking.stockBeginningDatetime, booking.venueDepartmentCode),
        ),
        booking_date=booking_date,
        booking_status=_build_booking_status(booking),
        booking_is_duo=booking.quantity == 2,
        booking_amount=booking.bookingAmount,
        booking_price_category_label=booking.priceCategoryLabel,
        booking_status_history=serialize_booking_status_history(booking),
    )

    return serialized_booking_recap


def _build_booking_status(booking: Booking) -> BookingRecapStatus:
    if booking.status == BookingStatus.REIMBURSED:
        return BookingRecapStatus.reimbursed
    if booking.status == BookingStatus.CANCELLED:
        return BookingRecapStatus.cancelled
    if booking.status == BookingStatus.USED:
        return BookingRecapStatus.validated
    if booking.isConfirmed:
        return BookingRecapStatus.confirmed
    return BookingRecapStatus.booked

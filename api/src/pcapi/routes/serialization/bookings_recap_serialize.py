from datetime import date
from datetime import datetime
from enum import Enum

from pydantic.v1 import root_validator

from pcapi.core.bookings.models import BookingExportType
from pcapi.core.bookings.models import BookingStatusFilter
from pcapi.domain.booking_recap.booking_recap import BookingRecap
from pcapi.domain.booking_recap.booking_recap import BookingRecapStatus
from pcapi.domain.booking_recap.booking_recap_history import BookingRecapCancelledHistory
from pcapi.domain.booking_recap.booking_recap_history import BookingRecapConfirmedHistory
from pcapi.domain.booking_recap.booking_recap_history import BookingRecapHistory
from pcapi.domain.booking_recap.booking_recap_history import BookingRecapPendingHistory
from pcapi.domain.booking_recap.booking_recap_history import BookingRecapReimbursedHistory
from pcapi.domain.booking_recap.booking_recap_history import BookingRecapValidatedHistory
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import to_camel
from pcapi.utils.date import isoformat


class OfferType(Enum):
    INDIVIDUAL_OR_DUO = "INDIVIDUAL_OR_DUO"
    EDUCATIONAL = "EDUCATIONAL"


class BookingRecapResponseBeneficiaryModel(BaseModel):
    email: str | None
    firstname: str | None
    lastname: str | None
    phonenumber: str | None


class BookingRecapResponseStockModel(BaseModel):
    event_beginning_datetime: datetime | None
    # FIXME (mageoffray, 2023-07-03): The stock_identifier field is unused by our front but used by pims.
    # Once our booking api is released and pims uses it we can remove it.
    stock_identifier: int
    offer_id: int
    offer_is_educational: bool
    # Field should be called offerEan but it is shared with
    # collective bookings. We have to adapt the pro front to change name
    offer_isbn: str | None
    offer_name: str

    class Config:
        alias_generator = to_camel


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
    serialized_booking_status_date = isoformat(booking_status_date) if booking_status_date else None

    return BookingRecapResponseBookingStatusHistoryModel(
        status=booking_status,
        date=serialized_booking_status_date,  # type: ignore [arg-type]
    )


def _serialize_booking_status_history(
    booking_status_history: BookingRecapHistory,
) -> list[BookingRecapResponseBookingStatusHistoryModel]:
    if isinstance(booking_status_history, BookingRecapPendingHistory):
        serialized_booking_status_history = [
            _serialize_booking_status_info(BookingRecapStatus.pending, booking_status_history.booking_date)
        ]
        return serialized_booking_status_history

    serialized_booking_status_history = [
        _serialize_booking_status_info(
            BookingRecapStatus.booked,
            booking_status_history.confirmation_date or booking_status_history.booking_date,
        )
    ]
    if (
        isinstance(booking_status_history, BookingRecapConfirmedHistory)
        and booking_status_history.date_confirmed is not None
    ):
        serialized_booking_status_history.append(
            _serialize_booking_status_info(BookingRecapStatus.confirmed, booking_status_history.date_confirmed)
        )
    if isinstance(booking_status_history, BookingRecapValidatedHistory):
        serialized_booking_status_history.append(
            _serialize_booking_status_info(BookingRecapStatus.validated, booking_status_history.date_used)
        )

    if isinstance(booking_status_history, BookingRecapCancelledHistory):
        serialized_booking_status_history.append(
            _serialize_booking_status_info(BookingRecapStatus.cancelled, booking_status_history.cancellation_date)
        )
    if isinstance(booking_status_history, BookingRecapReimbursedHistory):
        serialized_booking_status_history.append(
            _serialize_booking_status_info(BookingRecapStatus.reimbursed, booking_status_history.payment_date)
        )
    return serialized_booking_status_history


def serialize_booking_recap(booking_recap: BookingRecap) -> BookingRecapResponseModel:
    serialized_booking_recap = BookingRecapResponseModel(  # type: ignore [call-arg]
        stock={  # type: ignore [arg-type]
            "stockIdentifier": booking_recap.stock_identifier,
            "offerName": booking_recap.offer_name,
            "offerId": booking_recap.offer_identifier,
            "eventBeginningDatetime": (
                isoformat(booking_recap.event_beginning_datetime) if booking_recap.event_beginning_datetime else None
            ),
            "offerIsbn": booking_recap.offer_ean,
            "offerIsEducational": False,
        },
        beneficiary={  # type: ignore [arg-type]
            "lastname": booking_recap.beneficiary_lastname or booking_recap.redactor_lastname,
            "firstname": booking_recap.beneficiary_firstname or booking_recap.redactor_firstname,
            "email": booking_recap.beneficiary_email or booking_recap.redactor_email,
            "phonenumber": booking_recap.beneficiary_phonenumber,
        },
        bookingToken=booking_recap.booking_token,
        bookingDate=isoformat(booking_recap.booking_date),
        bookingStatus=booking_recap.booking_status.value,
        bookingIsDuo=booking_recap.booking_is_duo,
        bookingAmount=booking_recap.booking_amount,
        bookingPriceCategoryLabel=booking_recap.booking_price_category_label,
        bookingStatusHistory=_serialize_booking_status_history(booking_recap.booking_status_history),
    )

    return serialized_booking_recap


class BookingsExportStatusFilter(Enum):
    VALIDATED = "validated"
    ALL = "all"


class BookingsExportQueryModel(BaseModel):
    status: BookingsExportStatusFilter

    class config:
        alias_generator = to_camel
        extra = "forbid"


class ListBookingsQueryModel(BaseModel):
    page: int = 1
    venue_id: int | None
    offer_id: int | None
    event_date: date | None
    booking_status_filter: BookingStatusFilter | None
    booking_period_beginning_date: date | None
    booking_period_ending_date: date | None
    offer_type: OfferType | None
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

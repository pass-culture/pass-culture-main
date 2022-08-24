from datetime import datetime
from enum import Enum

from pydantic import root_validator

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
from pcapi.domain.booking_recap.bookings_recap_paginated import BookingsRecapPaginated
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import dehumanize_field
from pcapi.serialization.utils import to_camel
from pcapi.utils.date import format_into_timezoned_date
from pcapi.utils.human_ids import humanize


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
    offer_identifier: str
    stock_identifier: str
    offer_is_educational: bool
    offer_isbn: str | None
    offer_name: str


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
    booking_token: str | None
    stock: BookingRecapResponseStockModel


class ListBookingsResponseModel(BaseModel):
    bookingsRecap: list[BookingRecapResponseModel]
    page: int
    pages: int
    total: int


class PatchBookingByTokenQueryModel(BaseModel):
    email: str | None
    offer_id: str | None


def serialize_bookings_recap_paginated(bookings_recap_paginated: BookingsRecapPaginated) -> ListBookingsResponseModel:
    return ListBookingsResponseModel(
        bookingsRecap=[
            _serialize_booking_recap(booking_recap) for booking_recap in bookings_recap_paginated.bookings_recap
        ],
        page=bookings_recap_paginated.page,
        pages=bookings_recap_paginated.pages,
        total=bookings_recap_paginated.total,
    )


def _serialize_booking_status_info(
    booking_status: BookingRecapStatus, booking_status_date: datetime
) -> BookingRecapResponseBookingStatusHistoryModel:

    serialized_booking_status_date = format_into_timezoned_date(booking_status_date) if booking_status_date else None

    return BookingRecapResponseBookingStatusHistoryModel(
        status=booking_status.value,
        date=serialized_booking_status_date,
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


def _serialize_booking_recap(booking_recap: BookingRecap) -> BookingRecapResponseModel:
    serialized_booking_recap = BookingRecapResponseModel(
        stock={
            "offer_name": booking_recap.offer_name,
            "offer_identifier": humanize(booking_recap.offer_identifier),
            "stock_identifier": humanize(booking_recap.stock_identifier),
            "event_beginning_datetime": format_into_timezoned_date(booking_recap.event_beginning_datetime)
            if booking_recap.event_beginning_datetime
            else None,
            "offer_isbn": booking_recap.offer_isbn,
            "offer_is_educational": False,
        },
        beneficiary={
            "lastname": booking_recap.beneficiary_lastname or booking_recap.redactor_lastname,
            "firstname": booking_recap.beneficiary_firstname or booking_recap.redactor_firstname,
            "email": booking_recap.beneficiary_email or booking_recap.redactor_email,
            "phonenumber": booking_recap.beneficiary_phonenumber,
        },
        booking_token=booking_recap.booking_token,
        booking_date=format_into_timezoned_date(booking_recap.booking_date),
        booking_status=booking_recap.booking_status.value,
        booking_is_duo=booking_recap.booking_is_duo,
        booking_amount=booking_recap.booking_amount,
        booking_status_history=_serialize_booking_status_history(booking_recap.booking_status_history),
    )

    return serialized_booking_recap


class ListBookingsQueryModel(BaseModel):
    page: int = 1
    venue_id: int | None
    event_date: str | None
    booking_status_filter: BookingStatusFilter | None
    booking_period_beginning_date: str | None
    booking_period_ending_date: str | None
    offer_type: OfferType | None
    export_type: BookingExportType | None

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

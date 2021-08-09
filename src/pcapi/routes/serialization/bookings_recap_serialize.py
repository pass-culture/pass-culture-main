from datetime import date
from datetime import datetime
from typing import Any
from typing import Optional

from pydantic import BaseModel

from pcapi.domain.booking_recap.booking_recap import BookingRecap
from pcapi.domain.booking_recap.booking_recap import BookingRecapStatus
from pcapi.domain.booking_recap.booking_recap_history import BookingRecapCancelledHistory
from pcapi.domain.booking_recap.booking_recap_history import BookingRecapConfirmedHistory
from pcapi.domain.booking_recap.booking_recap_history import BookingRecapHistory
from pcapi.domain.booking_recap.booking_recap_history import BookingRecapReimbursedHistory
from pcapi.domain.booking_recap.booking_recap_history import BookingRecapValidatedHistory
from pcapi.domain.booking_recap.bookings_recap_paginated import BookingsRecapPaginated
from pcapi.serialization.utils import dehumanize_field
from pcapi.serialization.utils import to_camel
from pcapi.utils.date import format_into_timezoned_date
from pcapi.utils.human_ids import humanize


def serialize_bookings_recap_paginated(bookings_recap_paginated: BookingsRecapPaginated) -> dict[str, Any]:
    return {
        "bookings_recap": [
            _serialize_booking_recap(booking_recap) for booking_recap in bookings_recap_paginated.bookings_recap
        ],
        "page": bookings_recap_paginated.page,
        "pages": bookings_recap_paginated.pages,
        "total": bookings_recap_paginated.total,
    }


def _serialize_booking_status_info(booking_status: BookingRecapStatus, booking_status_date: datetime) -> dict[str, str]:

    serialized_booking_status_date = format_into_timezoned_date(booking_status_date) if booking_status_date else None

    return {
        "status": booking_status.value,
        "date": serialized_booking_status_date,
    }


def _serialize_booking_status_history(booking_status_history: BookingRecapHistory) -> list[dict[str, str]]:
    serialized_booking_status_history = [
        _serialize_booking_status_info(BookingRecapStatus.booked, booking_status_history.booking_date)
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


def _serialize_booking_recap(booking_recap: BookingRecap) -> dict[str, Any]:
    serialized_booking_recap = {
        "stock": {
            "offer_name": booking_recap.offer_name,
            "offer_identifier": humanize(booking_recap.offer_identifier),
            "event_beginning_datetime": format_into_timezoned_date(booking_recap.event_beginning_datetime)
            if booking_recap.event_beginning_datetime
            else None,
            "offer_isbn": booking_recap.offer_isbn,
        },
        "beneficiary": {
            "lastname": booking_recap.beneficiary_lastname,
            "firstname": booking_recap.beneficiary_firstname,
            "email": booking_recap.beneficiary_email,
            "phonenumber": booking_recap.beneficiary_phonenumber,
        },
        "booking_token": booking_recap.booking_token,
        "booking_date": format_into_timezoned_date(booking_recap.booking_date),
        "booking_status": booking_recap.booking_status.value,
        "booking_is_duo": booking_recap.booking_is_duo,
        "booking_amount": booking_recap.booking_amount,
        "booking_status_history": _serialize_booking_status_history(booking_recap.booking_status_history),
        "offerer": {"name": booking_recap.offerer_name},
        "venue": {
            "identifier": humanize(booking_recap.venue_identifier),
            "is_virtual": booking_recap.venue_is_virtual,
            "name": booking_recap.venue_name,
        },
    }

    return serialized_booking_recap


class ListBookingsQueryModel(BaseModel):
    page: int = 1
    venue_id: Optional[int]
    event_date: Optional[datetime]
    booking_period_beginning_date: date
    booking_period_ending_date: date

    _dehumanize_venue_id = dehumanize_field("venue_id")

    class Config:
        alias_generator = to_camel

    extra = "forbid"


class ListBookingsResponseModel(BaseModel):
    bookings_recap: list[dict]
    page: int
    pages: int
    total: int

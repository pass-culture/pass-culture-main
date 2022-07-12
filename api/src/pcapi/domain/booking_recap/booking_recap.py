from datetime import datetime
from enum import Enum

from pcapi.core.bookings import models as bookings_models
from pcapi.domain.booking_recap import utils
from pcapi.domain.booking_recap.booking_recap_history import BookingRecapCancelledHistory
from pcapi.domain.booking_recap.booking_recap_history import BookingRecapConfirmedHistory
from pcapi.domain.booking_recap.booking_recap_history import BookingRecapHistory
from pcapi.domain.booking_recap.booking_recap_history import BookingRecapPendingHistory
from pcapi.domain.booking_recap.booking_recap_history import BookingRecapReimbursedHistory
from pcapi.domain.booking_recap.booking_recap_history import BookingRecapValidatedHistory


class BookingRecapStatus(Enum):
    booked = "booked"
    validated = "validated"
    cancelled = "cancelled"
    reimbursed = "reimbursed"
    confirmed = "confirmed"
    pending = "pending"


class BookingRecap:
    def __init__(
        self,
        beneficiary_lastname: str | None,
        beneficiary_firstname: str | None,
        beneficiary_email: str | None,
        beneficiary_phonenumber: str | None,
        booking_token: str,
        booking_date: datetime,
        booking_is_duo: bool,
        booking_is_used: bool,
        booking_is_cancelled: bool,
        booking_is_reimbursed: bool,
        booking_is_confirmed: bool,
        booking_raw_status: bookings_models.BookingStatus,
        booking_confirmation_date: datetime | None,
        booking_is_educational: bool,
        booking_is_external: bool,
        booking_amount: float,
        cancellation_date: datetime | None,
        cancellation_limit_date: datetime | None,
        payment_date: datetime | None,
        date_used: datetime | None,
        offer_identifier: int,
        offer_name: str,
        offer_isbn: str | None,
        redactor_lastname: str | None,
        redactor_firstname: str | None,
        redactor_email: str | None,
        event_beginning_datetime: datetime | None,
        stock_identifier: int,
    ):
        self.booking_amount = booking_amount
        self.beneficiary_lastname = beneficiary_lastname
        self.beneficiary_firstname = beneficiary_firstname
        self.beneficiary_email = beneficiary_email
        self.beneficiary_phonenumber = beneficiary_phonenumber
        self.booking_token = booking_token
        self.booking_date = booking_date
        self.booking_is_duo = booking_is_duo
        self.booking_is_used = booking_is_used
        self.booking_is_cancelled = booking_is_cancelled
        self.booking_is_reimbursed = booking_is_reimbursed
        self.booking_is_confirmed = booking_is_confirmed
        self.booking_raw_status = booking_raw_status
        self.booking_confirmation_date = booking_confirmation_date
        self.booking_is_educational = booking_is_educational
        self.booking_is_external = booking_is_external
        self.offer_identifier = offer_identifier
        self.offer_name = offer_name
        self.offer_isbn = offer_isbn
        self.redactor_lastname = redactor_lastname
        self.redactor_firstname = redactor_firstname
        self.redactor_email = redactor_email
        self.booking_status_history = self.build_status_history(
            booking_date=booking_date,
            cancellation_date=cancellation_date,
            cancellation_limit_date=cancellation_limit_date,
            payment_date=payment_date,
            date_used=date_used,
            confirmation_date=booking_confirmation_date,
        )
        self.event_beginning_datetime = event_beginning_datetime
        self.stock_identifier = stock_identifier

    def __new__(cls, *args, **kwargs):  # type: ignore [no-untyped-def]
        return object.__new__(cls)

    def _get_booking_token(self) -> str | None:
        return utils.get_booking_token(
            self._booking_token,
            self.booking_raw_status,
            self.booking_is_educational,
            self.booking_is_external,
            self.event_beginning_datetime,
        )

    def _set_booking_token(self, booking_token: str) -> None:
        self._booking_token = booking_token

    booking_token = property(
        lambda self: self._get_booking_token(),
        lambda self, booking_token: self._set_booking_token(booking_token),
    )

    @property
    def booking_status(self) -> BookingRecapStatus:
        if self.booking_raw_status == bookings_models.BookingStatus.PENDING:
            return BookingRecapStatus.pending
        if self.booking_is_reimbursed:
            return BookingRecapStatus.reimbursed
        if self.booking_is_cancelled:
            return BookingRecapStatus.cancelled
        if self.booking_is_used:
            return BookingRecapStatus.validated
        if self.booking_is_confirmed:
            return BookingRecapStatus.confirmed
        return BookingRecapStatus.booked

    def build_status_history(
        self,
        booking_date: datetime,
        cancellation_date: datetime | None,
        cancellation_limit_date: datetime | None,
        payment_date: datetime | None,
        date_used: datetime | None,
        confirmation_date: datetime | None,
    ) -> BookingRecapHistory:
        if self.booking_status == BookingRecapStatus.pending:
            return BookingRecapPendingHistory(booking_date=booking_date)

        if self.booking_is_reimbursed:
            return BookingRecapReimbursedHistory(
                booking_date=booking_date,
                cancellation_limit_date=cancellation_limit_date,
                payment_date=payment_date,  # type: ignore [arg-type]
                date_used=date_used,
                confirmation_date=confirmation_date,
            )
        if self.booking_is_cancelled:
            return BookingRecapCancelledHistory(
                booking_date=booking_date,
                cancellation_date=cancellation_date,  # type: ignore [arg-type]
                confirmation_date=confirmation_date,
            )
        if self.booking_is_used:
            return BookingRecapValidatedHistory(
                booking_date=booking_date,
                cancellation_limit_date=cancellation_limit_date,
                date_used=date_used,  # type: ignore [arg-type]
                confirmation_date=confirmation_date,
            )
        if self.booking_is_confirmed:
            return BookingRecapConfirmedHistory(
                booking_date=booking_date,
                cancellation_limit_date=cancellation_limit_date,
                confirmation_date=confirmation_date,
            )

        return BookingRecapHistory(booking_date, confirmation_date)

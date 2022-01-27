from datetime import datetime
from typing import Optional

from pcapi.core.bookings.api import compute_cancellation_limit_date
from pcapi.core.bookings.models import BookingStatus
from pcapi.domain.booking_recap.booking_recap import BookingRecap


def create_domain_booking_recap(
    offer_identifier: int = 1,
    offer_name: str = "Le livre de la jungle",
    offer_isbn: Optional[str] = None,
    beneficiary_lastname: str = "Sans Nom",
    beneficiary_firstname: str = "Mowgli",
    beneficiary_email: str = "mowgli@example.com",
    beneficiary_phonenumber: str = "0100000000",
    booking_amount: float = 0,
    booking_token: str = "JUNGLE",
    booking_date: datetime = datetime(2020, 3, 14, 19, 5, 3, 0),
    booking_is_duo: bool = False,
    booking_is_educational: bool = False,
    booking_is_used: bool = False,
    booking_is_cancelled: bool = False,
    booking_is_reimbursed: bool = False,
    booking_is_confirmed: bool = False,
    booking_status: BookingStatus = BookingStatus.CONFIRMED,
    booking_confirmation_date: Optional[datetime] = None,
    payment_date: Optional[datetime] = None,
    cancellation_date: Optional[datetime] = None,
    date_used: Optional[datetime] = None,
    redactor_lastname=None,
    redactor_firstname=None,
    redactor_email=None,
    event_beginning_datetime: Optional[datetime] = None,
) -> BookingRecap:
    return BookingRecap(
        offer_identifier=offer_identifier,
        offer_name=offer_name,
        offer_isbn=offer_isbn,
        beneficiary_lastname=beneficiary_lastname,
        beneficiary_firstname=beneficiary_firstname,
        beneficiary_email=beneficiary_email,
        beneficiary_phonenumber=beneficiary_phonenumber,
        booking_amount=booking_amount,
        booking_token=booking_token,
        booking_date=booking_date,
        booking_is_duo=booking_is_duo,
        booking_is_educational=booking_is_educational,
        booking_is_used=booking_is_used,
        booking_is_cancelled=booking_is_cancelled,
        booking_is_reimbursed=booking_is_reimbursed,
        booking_is_confirmed=booking_is_confirmed,
        booking_raw_status=booking_status,
        booking_confirmation_date=booking_confirmation_date,
        payment_date=payment_date,
        cancellation_date=cancellation_date,
        cancellation_limit_date=compute_cancellation_limit_date(event_beginning_datetime, booking_date),
        date_used=date_used,
        redactor_lastname=redactor_lastname,
        redactor_firstname=redactor_firstname,
        redactor_email=redactor_email,
        event_beginning_datetime=event_beginning_datetime,
    )

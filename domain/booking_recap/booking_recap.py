import datetime
from enum import Enum
from typing import Optional

from models.offer_type import ProductType
from models.payment_status import TransactionStatus


class BookingRecapStatus(Enum):
    booked = 'booked'
    validated = 'validated'
    cancelled = 'cancelled'
    reimbursed = 'reimbursed'


class BookingRecap:
    def __init__(self,
                 offer_name: str,
                 offer_type: str,
                 beneficiary_lastname: str,
                 beneficiary_firstname: str,
                 beneficiary_email: str,
                 booking_token: str,
                 booking_date: datetime,
                 booking_status: BookingRecapStatus,
                 booking_is_duo: bool,
                 ):
        self.offer_name: str = offer_name
        self.offer_type = offer_type
        self.beneficiary_lastname: str = beneficiary_lastname
        self.beneficiary_firstname: str = beneficiary_firstname
        self.beneficiary_email: str = beneficiary_email
        self.booking_token: str = booking_token
        self.booking_date: datetime = booking_date
        self.booking_status = booking_status
        self.booking_is_duo = booking_is_duo


class EventBookingRecap(BookingRecap):
    def __init__(self, event_beginning_datetime: datetime, **kwargs):
        super().__init__(**kwargs)
        self.event_beginning_datetime = event_beginning_datetime


def compute_booking_recap_status(booking: object) -> BookingRecapStatus:
    if booking.paymentStatus == TransactionStatus.SENT:
        return BookingRecapStatus.reimbursed
    if booking.isCancelled:
        return BookingRecapStatus.cancelled
    if booking.isUsed:
        return BookingRecapStatus.validated
    return BookingRecapStatus.booked


def compute_booking_recap_token(booking: object) -> Optional[str]:
    if not booking.isUsed \
            and not booking.isCancelled \
            and ProductType.is_thing(booking.offerType):
        return None
    return booking.bookingToken

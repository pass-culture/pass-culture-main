import datetime
from enum import Enum
from typing import Optional

from models.offer_type import ProductType


class BookingRecapStatus(Enum):
    booked = 'booked'
    validated = 'validated'
    cancelled = 'cancelled'
    reimbursed = 'reimbursed'


class BookingRecap:
    def __init__(self,
                 offer_name: str,
                 beneficiary_lastname: str,
                 beneficiary_firstname: str,
                 beneficiary_email: str,
                 booking_token: str,
                 booking_date: datetime,
                 booking_is_duo: bool,
                 booking_is_used: bool,
                 booking_is_cancelled: bool,
                 booking_is_reimbursed: bool,
                 ):
        self.offer_name: str = offer_name
        self.beneficiary_lastname: str = beneficiary_lastname
        self.beneficiary_firstname: str = beneficiary_firstname
        self.beneficiary_email: str = beneficiary_email
        self.booking_token: str = booking_token
        self.booking_date: datetime = booking_date
        self.booking_is_duo = booking_is_duo
        self.booking_is_used = booking_is_used
        self.booking_is_cancelled = booking_is_cancelled
        self.booking_is_reimbursed = booking_is_reimbursed

    @property
    def booking_status(self):
        if self.booking_is_reimbursed:
            return BookingRecapStatus.reimbursed
        if self.booking_is_cancelled:
            return BookingRecapStatus.cancelled
        if self.booking_is_used:
            return BookingRecapStatus.validated
        else:
            return BookingRecapStatus.booked


class EventBookingRecap(BookingRecap):
    def __init__(self, event_beginning_datetime: datetime, **kwargs):
        super().__init__(**kwargs)
        self.event_beginning_datetime = event_beginning_datetime


def compute_booking_recap_token(booking: object) -> Optional[str]:
    if not booking.isUsed \
            and not booking.isCancelled \
            and ProductType.is_thing(booking.offerType):
        return None
    return booking.bookingToken

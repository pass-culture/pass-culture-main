import datetime
from enum import Enum


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
        self.offer_name = offer_name
        self.beneficiary_lastname = beneficiary_lastname
        self.beneficiary_firstname = beneficiary_firstname
        self.beneficiary_email = beneficiary_email
        self.booking_token = booking_token
        self.booking_date = booking_date
        self.booking_is_duo = booking_is_duo
        self.booking_is_used = booking_is_used
        self.booking_is_cancelled = booking_is_cancelled
        self.booking_is_reimbursed = booking_is_reimbursed

    def __new__(cls, *args, **kwargs):
        if cls is BookingRecap:
            raise TypeError("BookingRecap may not be instantiated")
        return object.__new__(cls)

    @property
    def booking_token(self):
        return self._booking_token

    @booking_token.setter
    def booking_token(self, booking_token):
        self._booking_token = booking_token

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


class ThingBookingRecap(BookingRecap):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @BookingRecap.booking_token.getter
    def booking_token(self):
        if not self.booking_is_used and not self.booking_is_cancelled:
            return None
        else:
            return self._booking_token


class EventBookingRecap(BookingRecap):
    def __init__(self, event_beginning_datetime: datetime, **kwargs):
        super().__init__(**kwargs)
        self.event_beginning_datetime = event_beginning_datetime

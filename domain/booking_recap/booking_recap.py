import datetime
from enum import Enum

from models.payment_status import TransactionStatus


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
                 booking_status: BookingRecapStatus
                 ):
        self.offer_name: str = offer_name
        self.beneficiary_lastname: str = beneficiary_lastname
        self.beneficiary_firstname: str = beneficiary_firstname
        self.beneficiary_email: str = beneficiary_email
        self.booking_token: str = booking_token
        self.booking_date: datetime = booking_date
        self.booking_status = booking_status


def compute_booking_recap_status(booking: object) -> BookingRecapStatus:
    if booking.paymentStatus == TransactionStatus.SENT:
        return BookingRecapStatus.reimbursed
    if booking.isCancelled:
        return BookingRecapStatus.cancelled
    if booking.isUsed:
        return BookingRecapStatus.validated
    return BookingRecapStatus.booked

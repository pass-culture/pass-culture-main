from datetime import datetime
from typing import List

from domain.reimbursement import BookingReimbursement
from models.payment import Payment
from models.payment_status import PaymentStatus, TransactionStatus


def create_payment_for_booking(booking_reimbursement: BookingReimbursement) -> Payment:
    payment = Payment()
    payment.booking = booking_reimbursement.booking
    payment.amount = booking_reimbursement.reimbursed_amount
    payment.reimbursementRule = booking_reimbursement.reimbursement.value.description
    payment.author = 'batch'
    payment.recipient = booking_reimbursement.booking.stock.resolvedOffer.venue.managingOfferer.name
    payment.iban = booking_reimbursement.booking.stock.resolvedOffer.venue.managingOfferer.iban
    payment.statuses = [_create_status_for_payment(payment)]
    return payment


def filter_out_already_paid_for_bookings(booking_reimbursements: List[BookingReimbursement]) -> List[
    BookingReimbursement]:
    return list(filter(lambda x: not x.booking.payments, booking_reimbursements))


def _create_status_for_payment(payment):
    payment_status = PaymentStatus()
    payment_status.date = datetime.utcnow()
    if payment.iban:
        payment_status.status = TransactionStatus.PENDING
    else:
        payment_status.status = TransactionStatus.NOT_PROCESSABLE
        payment_status.detail = 'IBAN manquant sur l\'offreur'
    return payment_status

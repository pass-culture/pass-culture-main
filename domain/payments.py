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
    venue = booking_reimbursement.booking.stock.resolvedOffer.venue
    if venue.iban:
        payment.recipient = venue.name
        payment.iban = venue.iban
        payment.bic = venue.bic
    else:
        offerer = venue.managingOfferer
        payment.recipient = offerer.name
        payment.iban = offerer.iban
        payment.bic = offerer.bic
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
        payment_status.detail = 'IBAN et BIC manquants sur l\'offreur'
    return payment_status

from datetime import datetime

from domain.reimbursement import BookingReimbursement
from models.payment import Payment
from models.payment_status import PaymentStatus, TransactionStatus


def create_payment_for_booking(booking_reimbursement: BookingReimbursement) -> Payment:
    payment = Payment()
    payment.booking = booking_reimbursement.booking
    payment.amount = booking_reimbursement.reimbursed_amount
    payment.reimbursementRule = booking_reimbursement.reimbursement.description
    payment.author = 'batch'
    payment.iban = booking_reimbursement.booking.stock.resolvedOffer.venue.offerer.iban
    payment.recipient = booking_reimbursement.booking.stock.resolvedOffer.venue.offerer.name

    payment_status = PaymentStatus()
    payment_status.date = datetime.utcnow()
    payment_status.status = TransactionStatus.PENDING
    payment.statuses = [payment_status]

    return payment

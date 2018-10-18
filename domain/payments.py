import itertools
import operator
import uuid
from datetime import datetime, timedelta
from io import BytesIO
from typing import List

from flask import render_template
from lxml import etree

from domain.reimbursement import BookingReimbursement
from models.payment import Payment
from models.payment_status import TransactionStatus


class InvalidTransactionXML(Exception):
    pass


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

    if payment.iban:
        payment.setStatus(TransactionStatus.PENDING)
    else:
        payment.setStatus(TransactionStatus.NOT_PROCESSABLE, detail='IBAN et BIC manquants sur l\'offreur')

    return payment


def filter_out_already_paid_for_bookings(booking_reimbursements: List[BookingReimbursement]) -> List[
    BookingReimbursement]:
    return list(filter(lambda x: not x.booking.payments, booking_reimbursements))


def generate_transaction_file(payments: List[Payment], pass_culture_iban: str, pass_culture_bic: str,
                              message_id: str) -> str:
    payments_with_iban = sorted(filter(lambda x: x.iban, payments), key=lambda x: (x.iban, x.bic))
    total_amount = sum([payment.amount for payment in payments_with_iban])

    payments_info_by_iban = []
    payments_by_iban = itertools.groupby(payments_with_iban, lambda x: (x.iban, x.bic))
    for (iban, bic), grouped_payments in payments_by_iban:
        info = {
            'iban': iban,
            'bic': bic,
            'unique_id': uuid.uuid4().hex,
            'amount': sum([payment.amount for payment in grouped_payments])
        }
        payments_info_by_iban.append(info)

    now = datetime.utcnow()

    return render_template(
        'transactions/transaction_banque_de_france.xml',
        message_id=message_id,
        creation_datetime=now.isoformat(),
        requested_execution_datetime=datetime.strftime(now + timedelta(days=7), "%Y-%m-%d"),
        payments_info_by_iban=payments_info_by_iban,
        number_of_transactions=len(payments_info_by_iban),
        total_amount=total_amount,
        pass_culture_iban=pass_culture_iban,
        pass_culture_bic=pass_culture_bic
    )


def validate_transaction_file(transaction_file: str):
    xsd = render_template('transactions/transaction_banque_de_france.xsd')
    xsd_doc = etree.parse(BytesIO(xsd.encode()))
    xsd_schema = etree.XMLSchema(xsd_doc)

    xml = BytesIO(transaction_file.encode())
    xml_doc = etree.parse(xml)

    xsd_schema.assertValid(xml_doc)

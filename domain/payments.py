import itertools
import operator
from datetime import datetime, timedelta
from io import BytesIO
from typing import List

from flask import render_template
from lxml import etree

from domain.reimbursement import BookingReimbursement
from models.payment import Payment
from models.payment_status import TransactionStatus
from utils.human_ids import humanize


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
    payments_with_iban = sorted(filter(lambda x: x.iban, payments), key=operator.attrgetter('iban'))
    total_amount = sum([payment.amount for payment in payments_with_iban])
    payment_information = [_extract_payment_information(list(grouped_payments)) for iban, grouped_payments in
                           itertools.groupby(payments_with_iban, lambda x: x.iban)]
    now = datetime.utcnow()

    return render_template(
        'transactions/transaction_banque_de_france.xml',
        message_id=message_id,
        creation_datetime=now.isoformat(),
        requested_execution_datetime=datetime.strftime(now + timedelta(days=7), "%Y-%m-%d"),
        payments_by_iban=payment_information,
        number_of_transactions=len(payment_information),
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


def _extract_payment_information(payments: List[Payment]):
    amount = sum([payment.amount for payment in payments])
    first_payment = next(iter(payments))
    payment_id = first_payment.id
    venue_id = first_payment.booking.stock.resolvedOffer.venue.id
    offerer_id = first_payment.booking.stock.resolvedOffer.venue.managingOfferer.id
    unique_id = '{}_{}_{}'.format(humanize(offerer_id), humanize(venue_id), humanize(payment_id))

    return {'iban': first_payment.iban, 'bic': first_payment.bic, 'unique_id': unique_id, 'amount': amount}

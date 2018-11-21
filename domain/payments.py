import itertools
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from io import BytesIO
from typing import List
from uuid import UUID

from flask import render_template
from lxml import etree

from domain.reimbursement import BookingReimbursement
from models.payment import Payment
from models.payment_status import TransactionStatus


class InvalidTransactionXML(Exception):
    pass


class Transaction:
    def __init__(self, creditor_iban: str, creditor_bic: str, creditor_name: str, creditor_siren: str,
                 end_to_end_id: UUID, amount: Decimal):
        self.creditor_iban = creditor_iban
        self.creditor_bic = creditor_bic
        self.creditor_name = creditor_name
        self.creditor_siren = creditor_siren
        self.end_to_end_id = end_to_end_id
        self.amount = amount


def create_payment_for_booking(booking_reimbursement: BookingReimbursement) -> Payment:
    payment = Payment()
    payment.booking = booking_reimbursement.booking
    payment.amount = booking_reimbursement.reimbursed_amount
    payment.reimbursementRule = booking_reimbursement.reimbursement.value.description
    payment.author = 'batch'
    venue = booking_reimbursement.booking.stock.resolvedOffer.venue

    if venue.iban:
        payment.iban = venue.iban
        payment.bic = venue.bic
    else:
        offerer = venue.managingOfferer
        payment.iban = offerer.iban
        payment.bic = offerer.bic

    payment.recipientName = venue.managingOfferer.name
    payment.recipientSiren = venue.managingOfferer.siren

    if payment.iban:
        payment.setStatus(TransactionStatus.PENDING)
    else:
        payment.setStatus(TransactionStatus.NOT_PROCESSABLE, detail='IBAN et BIC manquants sur l\'offreur')

    return payment


def filter_out_already_paid_for_bookings(booking_reimbursements: List[BookingReimbursement]) -> List[
    BookingReimbursement]:
    return list(filter(lambda x: not x.booking.payments, booking_reimbursements))


def generate_transaction_file(payments: List[Payment], pass_culture_iban: str, pass_culture_bic: str, message_id: str,
                              remittance_code: str) -> str:
    transactions = _group_payments_into_transactions(payments, message_id)
    total_amount = sum([transaction.amount for transaction in transactions])
    now = datetime.utcnow()

    return render_template(
        'transactions/transaction_banque_de_france.xml',
        message_id=message_id,
        creation_datetime=now.isoformat(),
        requested_execution_datetime=datetime.strftime(now + timedelta(days=7), "%Y-%m-%d"),
        transactions=transactions,
        number_of_transactions=len(transactions),
        total_amount=total_amount,
        pass_culture_iban=pass_culture_iban,
        pass_culture_bic=pass_culture_bic,
        initiating_party_id=remittance_code
    )


def validate_transaction_file(transaction_file: str):
    xsd = render_template('transactions/transaction_banque_de_france.xsd')
    xsd_doc = etree.parse(BytesIO(xsd.encode()))
    xsd_schema = etree.XMLSchema(xsd_doc)

    xml = BytesIO(transaction_file.encode())
    xml_doc = etree.parse(xml)

    xsd_schema.assertValid(xml_doc)


def _group_payments_into_transactions(payments: List[Payment], message_id: str) -> List[Transaction]:
    payments_with_iban = sorted(filter(lambda x: x.iban, payments), key=lambda x: (x.iban, x.bic))
    payments_by_iban = itertools.groupby(payments_with_iban, lambda x: (x.iban, x.bic))

    transactions = []
    for (iban, bic), grouped_payments in payments_by_iban:
        payments_of_iban = list(grouped_payments)
        amount = sum([payment.amount for payment in payments_of_iban])
        end_to_end_id = uuid.uuid4()

        for payment in payments_of_iban:
            payment.setTransactionIds(message_id, end_to_end_id)

        transactions.append(Transaction(iban, bic, payments_of_iban[0].recipientName, payments_of_iban[0].recipientSiren, end_to_end_id, amount))
    return transactions

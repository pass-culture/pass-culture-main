import csv
import itertools
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from hashlib import sha256
from io import BytesIO, StringIO
from typing import List, Dict, Tuple, Set
from uuid import UUID

from flask import render_template
from lxml import etree

from domain.bank_account import format_raw_iban_or_bic
from domain.reimbursement import BookingReimbursement
from models import PaymentMessage
from models.payment import Payment
from models.payment_status import TransactionStatus
from models.user_sql_entity import WalletBalance
from repository import booking_queries
from utils.human_ids import humanize

XML_NAMESPACE = {'ns': 'urn:iso:std:iso:20022:tech:xsd:pain.001.001.03'}


class InvalidTransactionXML(Exception):
    pass


class UnmatchedPayments(Exception):
    def __init__(self, payment_ids: Set[int]):
        self.payment_ids = payment_ids


class Transaction:
    def __init__(self, creditor_iban: str, creditor_bic: str, creditor_name: str, creditor_siren: str,
                 end_to_end_id: UUID, amount: Decimal, custom_message: str):
        self.creditor_iban = creditor_iban
        self.creditor_bic = creditor_bic
        self.creditor_name = creditor_name
        self.creditor_siren = creditor_siren
        self.end_to_end_id = end_to_end_id
        self.amount = amount
        self.custom_message = custom_message


class PaymentDetails:
    CSV_HEADER = [
        "ID de l'utilisateur",
        "Email de l'utilisateur",
        "Raison sociale de la structure",
        "SIREN",
        "Raison sociale du lieu",
        "SIRET",
        "ID du lieu",
        "Nom de l'offre",
        "Type de l'offre",
        "Date de la réservation",
        "Prix de la réservation",
        "Date de validation",
        "IBAN",
        "Payment Message Name",
        "Transaction ID",
        "Paiement ID",
        "Taux de remboursement",
        "Montant remboursé à l'offreur",
    ]

    def __init__(self, payment: Payment = None, booking_used_date: datetime = None):
        if payment is not None:
            self.booking_user_id = payment.booking.user.id
            self.booking_user_email = payment.booking.user.email
            self.offerer_name = payment.booking.stock.offer.venue.managingOfferer.name
            self.offerer_siren = payment.booking.stock.offer.venue.managingOfferer.siren
            self.venue_name = payment.booking.stock.offer.venue.name
            self.venue_siret = payment.booking.stock.offer.venue.siret
            self.venue_humanized_id = humanize(payment.booking.stock.offer.venue.id)
            self.offer_name = payment.booking.stock.offer.product.name
            self.offer_type = payment.booking.stock.offer.product.offerType['proLabel']
            self.booking_date = payment.booking.dateCreated
            self.booking_amount = payment.booking.value
            self.booking_used_date = booking_used_date
            self.payment_iban = payment.iban
            self.payment_message_name = payment.paymentMessageName
            self.transaction_end_to_end_id = payment.transactionEndToEndId
            self.payment_id = payment.id
            self.reimbursement_rate = payment.reimbursementRate
            self.reimbursed_amount = payment.amount

    def as_csv_row(self):
        return [
            str(self.booking_user_id),
            self.booking_user_email,
            self.offerer_name,
            self.offerer_siren,
            self.venue_name,
            self.venue_siret,
            self.venue_humanized_id,
            self.offer_name,
            self.offer_type,
            str(self.booking_date),
            str(self.booking_amount),
            str(self.booking_used_date),
            self.payment_iban,
            self.payment_message_name,
            str(self.transaction_end_to_end_id),
            str(self.payment_id),
            str(self.reimbursement_rate),
            str(self.reimbursed_amount)
        ]


def create_payment_for_booking(booking_reimbursement: BookingReimbursement) -> Payment:
    venue = booking_reimbursement.booking.stock.offer.venue

    payment = Payment()
    payment.booking = booking_reimbursement.booking
    payment.amount = booking_reimbursement.reimbursed_amount
    payment.reimbursementRule = booking_reimbursement.reimbursement.value.description
    payment.reimbursementRate = booking_reimbursement.reimbursement.value.rate
    payment.author = 'batch'
    payment.transactionLabel = make_transaction_label(datetime.utcnow())

    if venue.iban:
        payment.iban = format_raw_iban_or_bic(venue.iban)
        payment.bic = format_raw_iban_or_bic(venue.bic)
    else:
        offerer = venue.managingOfferer
        payment.iban = format_raw_iban_or_bic(offerer.iban)
        payment.bic = format_raw_iban_or_bic(offerer.bic)

    payment.recipientName = venue.managingOfferer.name
    payment.recipientSiren = venue.managingOfferer.siren

    if payment.iban:
        payment.setStatus(TransactionStatus.PENDING)
    else:
        payment.setStatus(TransactionStatus.NOT_PROCESSABLE,
                          detail='IBAN et BIC manquants sur l\'offreur')

    return payment


def filter_out_already_paid_for_bookings(booking_reimbursements: List[BookingReimbursement]) -> \
        List[BookingReimbursement]:
    return list(filter(lambda x: not x.booking.payments, booking_reimbursements))


def filter_out_bookings_without_cost(
        booking_reimbursements: List[BookingReimbursement]
) -> List[BookingReimbursement]:
    return list(filter(lambda x: x.reimbursed_amount > Decimal(0), booking_reimbursements))


def keep_only_pending_payments(payments: List[Payment]) -> List[Payment]:
    return list(filter(lambda x: x.currentStatus.status == TransactionStatus.PENDING, payments))


def keep_only_not_processable_payments(payments: List[Payment]) -> List[Payment]:
    return list(filter(lambda x: x.currentStatus.status == TransactionStatus.NOT_PROCESSABLE, payments))


def generate_message_file(payments: List[Payment], pass_culture_iban: str, pass_culture_bic: str, message_name: str,
                          remittance_code: str) -> str:
    transactions = _group_payments_into_transactions(payments)
    total_amount = sum([transaction.amount for transaction in transactions])
    now = datetime.utcnow()

    return render_template(
        'transactions/transaction_banque_de_france.xml',
        message_name=message_name,
        creation_datetime=now.isoformat(),
        requested_execution_datetime=datetime.strftime(
            now + timedelta(days=7), "%Y-%m-%d"),
        transactions=transactions,
        number_of_transactions=len(transactions),
        total_amount=total_amount,
        pass_culture_iban=pass_culture_iban,
        pass_culture_bic=pass_culture_bic,
        initiating_party_id=remittance_code,
    )


def validate_message_file_structure(transaction_file: str):
    xsd = render_template('transactions/transaction_banque_de_france.xsd')
    xsd_doc = etree.parse(BytesIO(xsd.encode()))
    xsd_schema = etree.XMLSchema(xsd_doc)

    encoded_file = transaction_file.encode('utf-8')
    xml = BytesIO(encoded_file)
    xml_doc = etree.parse(xml)

    xsd_schema.assertValid(xml_doc)


def generate_file_checksum(file: str):
    encoded_file = file.encode('utf-8')
    return sha256(encoded_file).digest()


def create_all_payments_details(payments: List[Payment], find_booking_date_used=booking_queries.find_date_used) -> \
        List[PaymentDetails]:
    return list(map(lambda p: create_payment_details(p, find_booking_date_used), payments))


def create_payment_details(payment: Payment, find_booking_date_used=booking_queries.find_date_used) -> PaymentDetails:
    return PaymentDetails(payment, find_booking_date_used(payment.booking))


def generate_payment_details_csv(payments_details: List[PaymentDetails]) -> str:
    output = StringIO()
    csv_lines = [details.as_csv_row() for details in payments_details]
    writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)
    writer.writerow(PaymentDetails.CSV_HEADER)
    writer.writerows(csv_lines)
    return output.getvalue()


def generate_wallet_balances_csv(wallet_balances: List[WalletBalance]) -> str:
    output = StringIO()
    csv_lines = [balance.as_csv_row() for balance in wallet_balances]
    writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)
    writer.writerow(WalletBalance.CSV_HEADER)
    writer.writerows(csv_lines)
    return output.getvalue()


def make_transaction_label(date: datetime.date) -> str:
    month_and_year = date.strftime('%m-%Y')
    period = '1ère' if date.day < 15 else '2nde'
    return 'pass Culture Pro - remboursement %s quinzaine %s' % (period, month_and_year)


def generate_payment_message(name: str, checksum: str, payments: List[Payment]) -> PaymentMessage:
    payment_message = PaymentMessage()
    payment_message.name = name
    payment_message.checksum = checksum
    payment_message.payments = payments
    return payment_message


def read_message_name_in_message_file(xml_file: str) -> str:
    xml = BytesIO(xml_file.encode())
    tree = etree.parse(xml, etree.XMLParser())
    node = tree.find('//ns:GrpHdr/ns:MsgId', namespaces=XML_NAMESPACE)
    return node.text


def group_payments_by_status(payments: List[Payment]) -> Dict:
    groups = {}
    for p in payments:
        status_name = p.currentStatus.status.name

        if status_name in groups:
            groups[status_name].append(p)
        else:
            groups[status_name] = [p]
    return groups


def apply_banishment(payments: List[Payment], ids_to_ban: List[int]) -> Tuple[List[Payment], List[Payment]]:
    if not ids_to_ban:
        return [], []

    unmatched_ids = set(ids_to_ban) - {p.id for p in payments}
    if unmatched_ids:
        raise UnmatchedPayments(unmatched_ids)

    banned_payments = [p for p in payments if p.id in ids_to_ban]
    for p in banned_payments:
        p.setStatus(TransactionStatus.BANNED)

    retry_payments = [p for p in payments if p.id not in ids_to_ban]
    for p in retry_payments:
        p.setStatus(TransactionStatus.RETRY)

    return banned_payments, retry_payments


def _group_payments_into_transactions(payments: List[Payment]) -> List[Transaction]:
    payments_with_iban = sorted(
        filter(lambda x: x.iban, payments), key=lambda x: (x.iban, x.bic))
    payments_by_iban = itertools.groupby(
        payments_with_iban, lambda x: (x.iban, x.bic))

    transactions = []
    for (iban, bic), grouped_payments in payments_by_iban:
        payments_of_iban = list(grouped_payments)
        amount = sum([payment.amount for payment in payments_of_iban])
        end_to_end_id = uuid.uuid4()

        for payment in payments_of_iban:
            payment.transactionEndToEndId = end_to_end_id

        transactions.append(
            Transaction(iban, bic, payments_of_iban[0].recipientName, payments_of_iban[0].recipientSiren, end_to_end_id,
                        amount, payments_of_iban[0].transactionLabel))
    return transactions

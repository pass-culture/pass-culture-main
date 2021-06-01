import csv
from datetime import datetime
from datetime import timedelta
from decimal import Decimal
from io import BytesIO
from io import StringIO
import uuid
from uuid import UUID

from flask import render_template
from lxml import etree

from pcapi import settings
from pcapi.domain.bank_account import format_raw_iban_and_bic
from pcapi.domain.reimbursement import BookingReimbursement
from pcapi.models import db
from pcapi.models.payment import Payment
from pcapi.models.payment_status import TransactionStatus
from pcapi.models.wallet_balance import WalletBalance
import pcapi.utils.db as db_utils
from pcapi.utils.human_ids import humanize


class UnmatchedPayments(Exception):
    def __init__(self, payment_ids: set[int]):
        super().__init__()
        self.payment_ids = payment_ids


class Transaction:
    def __init__(
        self,
        creditor_iban: str,
        creditor_bic: str,
        creditor_name: str,
        creditor_siren: str,
        end_to_end_id: UUID,
        amount: Decimal,
        custom_message: str,
    ):
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
            self.offer_type = payment.booking.stock.offer.product.offerType["proLabel"]
            self.booking_date = payment.booking.dateCreated
            self.booking_amount = payment.booking.total_amount
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
            str(self.reimbursed_amount),
        ]


def create_payment_for_booking(booking_reimbursement: BookingReimbursement, batch_date: datetime) -> Payment:
    venue = booking_reimbursement.booking.stock.offer.venue
    offerer = venue.managingOfferer

    payment = Payment()
    payment.bookingId = booking_reimbursement.booking.id
    payment.amount = booking_reimbursement.reimbursed_amount
    payment.reimbursementRule = booking_reimbursement.reimbursement.value.description
    payment.reimbursementRate = booking_reimbursement.reimbursement.value.rate
    payment.author = "batch"
    payment.transactionLabel = make_transaction_label(datetime.utcnow())
    payment.batchDate = batch_date

    if venue.iban:
        payment.iban = format_raw_iban_and_bic(venue.iban)
        payment.bic = format_raw_iban_and_bic(venue.bic)
    else:
        payment.iban = format_raw_iban_and_bic(offerer.iban)
        payment.bic = format_raw_iban_and_bic(offerer.bic)

    payment.recipientName = offerer.name
    payment.recipientSiren = offerer.siren

    return payment


def filter_out_already_paid_for_bookings(
    booking_reimbursements: list[BookingReimbursement],
) -> list[BookingReimbursement]:
    return list(filter(lambda x: not x.booking.payments, booking_reimbursements))


def filter_out_bookings_without_cost(booking_reimbursements: list[BookingReimbursement]) -> list[BookingReimbursement]:
    return list(filter(lambda x: x.reimbursed_amount > Decimal(0), booking_reimbursements))


def keep_only_not_processable_payments(payments: list[Payment]) -> list[Payment]:
    return list(filter(lambda x: x.currentStatus.status == TransactionStatus.NOT_PROCESSABLE, payments))


def generate_message_file(
    payment_query, pass_culture_iban: str, pass_culture_bic: str, message_name: str, remittance_code: str
) -> str:
    transactions = _set_end_to_end_id_and_group_into_transactions(payment_query)
    total_amount = sum(transaction.amount for transaction in transactions)
    now = datetime.utcnow()

    return render_template(
        "transactions/transaction_banque_de_france.xml",
        message_name=message_name,
        creation_datetime=now.isoformat(),
        requested_execution_datetime=datetime.strftime(now + timedelta(days=7), "%Y-%m-%d"),
        transactions=transactions,
        number_of_transactions=len(transactions),
        total_amount=total_amount,
        pass_culture_iban=pass_culture_iban,
        pass_culture_bic=pass_culture_bic,
        initiating_party_id=remittance_code,
    )


def validate_message_file_structure(transaction_file: str):
    xsd = render_template("transactions/transaction_banque_de_france.xsd")
    xsd_doc = etree.parse(BytesIO(xsd.encode()))
    xsd_schema = etree.XMLSchema(xsd_doc)

    encoded_file = transaction_file.encode("utf-8")
    xml = BytesIO(encoded_file)
    xml_doc = etree.parse(xml)

    xsd_schema.assertValid(xml_doc)


def create_payment_details(payment: Payment) -> PaymentDetails:
    return PaymentDetails(payment, payment.booking.dateUsed)


def generate_payment_details_csv(payment_query) -> str:
    # FIXME (dbaty, 2021-05-31): remove this inner import once we have
    # moved functions to core.payments.api and
    # core.payments.repository.
    from pcapi.repository import payment_queries  # avoid import loop

    output = StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)
    writer.writerow(PaymentDetails.CSV_HEADER)
    for batch in db_utils.get_batches(payment_query, Payment.id, settings.PAYMENTS_CSV_DETAILS_BATCH_SIZE):
        payments = payment_queries.join_for_payment_details(batch)
        rows = [create_payment_details(payment).as_csv_row() for payment in payments]
        writer.writerows(rows)
    return output.getvalue()


def generate_wallet_balances_csv(wallet_balances: list[WalletBalance]) -> str:
    output = StringIO()
    csv_lines = [balance.as_csv_row() for balance in wallet_balances]
    writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)
    writer.writerow(WalletBalance.CSV_HEADER)
    writer.writerows(csv_lines)
    return output.getvalue()


def make_transaction_label(date: datetime.date) -> str:
    month_and_year = date.strftime("%m-%Y")
    period = "1ère" if date.day < 15 else "2nde"
    return "pass Culture Pro - remboursement %s quinzaine %s" % (period, month_and_year)


def apply_banishment(payments: list[Payment], ids_to_ban: list[int]) -> tuple[list[Payment], list[Payment]]:
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


def _set_end_to_end_id_and_group_into_transactions(payment_query) -> list[Transaction]:
    # FIXME (dbaty, 2021-05-31): remove this inner import once we have
    # moved functions to core.payments.api and
    # core.payments.repository.
    from pcapi.repository import payment_queries  # avoid import loop

    # FIXME (dbaty, 2021-05-31): this function still makes a lot of
    # SQL queries. It may be possible to UPDATE all payments in a
    # single query, with a different PostgreSQL-generated
    # `transactionEndToEndId` for each pair of `(iban, bic)`.
    transactions = []
    # Sort for reproducibility and tests
    groups = sorted(payment_queries.group_by_iban_and_bic(payment_query))
    for group in groups:
        end_to_end_id = uuid.uuid4()
        # We cannot directly call "update()" when "join()" has been called.
        batch = (
            db.session.query(Payment)
            .filter(Payment.id.in_(payment_query.with_entities(Payment.id)))
            .filter_by(iban=group.iban, bic=group.bic)
        )
        batch.update({"transactionEndToEndId": end_to_end_id}, synchronize_session=False)
        transactions.append(
            Transaction(
                group.iban,
                group.bic,
                group.recipient_name,
                group.recipient_siren,
                end_to_end_id,
                group.total_amount,
                group.transaction_label,
            )
        )
    db.session.commit()
    return transactions

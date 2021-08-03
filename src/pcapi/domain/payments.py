import csv
from dataclasses import dataclass
from datetime import datetime
from datetime import timedelta
from decimal import Decimal
from io import BytesIO
from io import StringIO
import logging
from uuid import UUID

from flask import render_template
from lxml import etree

from pcapi import settings
import pcapi.core.payments.models as payments_models
from pcapi.domain.bank_account import format_raw_iban_and_bic
from pcapi.domain.reimbursement import BookingReimbursement
from pcapi.models import db
from pcapi.models.payment import Payment
from pcapi.models.payment_status import TransactionStatus
from pcapi.models.wallet_balance import WalletBalance
import pcapi.utils.db as db_utils
from pcapi.utils.human_ids import humanize


logger = logging.getLogger(__name__)


class UnmatchedPayments(Exception):
    def __init__(self, payment_ids: set[int]):
        super().__init__()
        self.payment_ids = payment_ids


@dataclass
class Transaction:
    creditor_iban: str
    creditor_bic: str
    creditor_name: str
    creditor_siren: str
    end_to_end_id: UUID
    amount: Decimal
    custom_message: str


class PaymentDetails:
    CSV_HEADER = [
        "Libellé fournisseur",
        "Raison sociale de la structure",
        "SIREN",
        "Raison sociale du lieu",
        "SIRET",
        "ID du lieu",
        "ID de l'offre",
        "Nom de l'offre",
        "Type de l'offre",
        "Date de la réservation",
        "Prix de la réservation",
        "Date de validation",
        "IBAN",
        "Paiement ID",
        "Taux de remboursement",
        "Montant remboursé à l'offreur",
        "Marge",
    ]

    def __init__(self, payment: Payment = None, booking_used_date: datetime = None):
        if payment is not None:
            offer = payment.booking.stock.offer
            venue = offer.venue
            offerer = venue.managingOfferer
            self.offerer_and_venue_label = f"{offerer.name}-{venue.name}"
            self.offerer_name = offerer.name
            self.offerer_siren = offerer.siren
            self.venue_name = venue.name
            self.venue_siret = venue.siret
            self.venue_humanized_id = humanize(venue.id)
            self.offer_id = offer.id
            self.offer_name = offer.product.name
            self.offer_type = offer.product.offerType["proLabel"]
            self.booking_date = payment.booking.dateCreated
            self.booking_amount = payment.booking.total_amount
            self.booking_used_date = booking_used_date
            self.payment_iban = payment.iban
            self.payment_id = payment.id
            # `Payment.reimbursementRate` is None if a custom
            # reimbursement rule has been applied.
            self.reimbursement_rate = payment.reimbursementRate or (
                Decimal(payment.amount / payment.booking.total_amount).quantize(Decimal("0.01"))
            )
            self.reimbursed_amount = payment.amount
            self.margin = payment.booking.total_amount - payment.amount

    def as_csv_row(self):
        return [
            self.offerer_and_venue_label,
            self.offerer_name,
            self.offerer_siren,
            self.venue_name,
            self.venue_siret,
            self.venue_humanized_id,
            str(self.offer_id),
            self.offer_name,
            self.offer_type,
            str(self.booking_date),
            str(self.booking_amount),
            str(self.booking_used_date),
            self.payment_iban,
            str(self.payment_id),
            str(self.reimbursement_rate),
            str(self.reimbursed_amount),
            str(self.margin),
        ]


def create_payment_for_booking(reimbursement: BookingReimbursement, batch_date: datetime) -> Payment:
    venue = reimbursement.booking.stock.offer.venue
    offerer = venue.managingOfferer

    payment = Payment()
    payment.bookingId = reimbursement.booking.id
    payment.amount = reimbursement.reimbursed_amount
    if isinstance(reimbursement.rule, payments_models.CustomReimbursementRule):
        payment.customReimbursementRuleId = reimbursement.rule.id
    else:
        payment.reimbursementRule = reimbursement.rule.description
        payment.reimbursementRate = reimbursement.rule.rate
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


def generate_venues_csv(payment_query) -> str:
    # FIXME (dbaty, 2021-05-31): remove this inner import once we have
    # moved functions to core.payments.api and
    # core.payments.repository.
    from pcapi.repository import payment_queries  # avoid import loop

    output = StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)
    header = (
        "ID lieu",
        "SIREN",
        "Raison sociale de la structure",
        "SIRET",
        "Raison sociale du lieu",
        "Libellé fournisseur",
        "IBAN",
        "BIC",
        "Montant total",
    )
    writer.writerow(header)
    for group in payment_queries.group_by_venue(payment_query):
        row = (
            humanize(group.venue_id),
            group.siren,
            group.offerer_name,
            group.siret,
            group.venue_name,
            f"{group.offerer_name}-{group.venue_name}",
            group.iban,
            group.bic,
            group.total_amount,
        )
        writer.writerow(row)
    return output.getvalue()


def generate_message_file(
    payment_query,
    batch_date: datetime,
    pass_culture_iban: str,
    pass_culture_bic: str,
    message_name: str,
    remittance_code: str,
) -> str:
    logger.info("[BATCH][PAYMENTS] Setting transactionEndToEndId on all payments to send")
    transactions = _set_end_to_end_id_and_group_into_transactions(payment_query, batch_date)
    logger.info("[BATCH][PAYMENTS] Set transactionEndToEndId on all payments to send")
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


def _set_end_to_end_id_and_group_into_transactions(payment_query, batch_date) -> list[Transaction]:
    # FIXME (dbaty, 2021-05-31): remove this inner import once we have
    # moved functions to core.payments.api and
    # core.payments.repository.
    from pcapi.repository import payment_queries  # avoid import loop

    # FIXME (dbaty, 2021-06-15): we should use the ORM model and
    # `payment_query` as the base query, instead of this raw SQL. But
    # I need a very quick fix, so that will do, for now.
    # Let the database generate and set all transactionEndToEndId and
    # return the generated value for each IBAN.
    result = db.session.execute(
        """
        UPDATE payment
        SET "transactionEndToEndId" = sub.uuid
        FROM (
            SELECT distinct on (iban)
                   iban,
                   gen_random_uuid() as uuid
            FROM payment
            WHERE "batchDate" = :batch_date
        ) AS sub
        WHERE payment.iban = sub.iban
        AND id IN (
            SELECT payment.id
            FROM payment JOIN (
                SELECT DISTINCT ON (payment_status."paymentId")
                       payment.id AS payment_id,
                       payment_status.status AS status
                FROM payment
                JOIN payment_status
                ON payment.id = payment_status."paymentId"
                WHERE payment."batchDate" = :batch_date
                ORDER BY payment_status."paymentId", payment_status.date DESC)
            AS statuses ON statuses.payment_id = payment.id
            WHERE statuses.status IN ('PENDING', 'ERROR', 'RETRY')
        )
        RETURNING payment.iban AS iban, payment."transactionEndToEndId" AS transaction_id
    """,
        {"batch_date": batch_date},
    )
    rows = result.fetchall()
    db.session.commit()
    transaction_ids = {row.iban: row.transaction_id for row in rows}

    # Sort for reproducibility and tests
    groups = sorted(payment_queries.group_by_iban_and_bic(payment_query))
    return [
        Transaction(
            creditor_iban=group.iban,
            creditor_bic=group.bic,
            creditor_name=group.recipient_name,
            creditor_siren=group.recipient_siren,
            end_to_end_id=transaction_ids[group.iban],
            amount=group.total_amount,
            custom_message=group.transaction_label,
        )
        for group in groups
    ]

from typing import List

from flask import render_template
from sqlalchemy import text

from models import PaymentTransaction, Payment, PaymentStatus, Booking, Stock, Offer, Venue, BankInformation, Offerer
from models.db import db
from models.payment_status import TransactionStatus


def find_transaction_checksum(message_id: str) -> str:
    transaction = PaymentTransaction.query.filter_by(messageId=message_id).first()
    return transaction.checksum if transaction else None


def find_error_payments() -> List[Payment]:
    query = render_template('sql/find_payment_ids_with_last_status.sql', status='ERROR')
    error_payment_ids = db.session.query(PaymentStatus.paymentId).from_statement(text(query)).all()
    return Payment.query.filter(Payment.id.in_(error_payment_ids)).all()


def find_retry_payments() -> List[Payment]:
    query = render_template('sql/find_payment_ids_with_last_status.sql', status='RETRY')
    retry_payment_ids = db.session.query(PaymentStatus.paymentId).from_statement(text(query)).all()
    return Payment.query.filter(Payment.id.in_(retry_payment_ids)).all()


def find_payments_by_message(message_id: str) -> List[Payment]:
    return Payment.query \
        .join(PaymentTransaction) \
        .filter(PaymentTransaction.messageId == message_id) \
        .all()


def find_all_with_status_not_processable_for_bank_information(bank_information: BankInformation) -> List[Payment]:
    predicate_matches_venue_or_offerer = (Venue.id == BankInformation.venueId) | (
                Offerer.id == BankInformation.offererId)

    query = Payment.query \
        .join(Booking) \
        .join(Stock) \
        .join(Offer) \
        .join(Venue) \
        .join(Offerer) \
        .join(BankInformation, predicate_matches_venue_or_offerer) \
        .filter_by(id=bank_information.id) \
        .join(PaymentStatus, PaymentStatus.paymentId == Payment.id) \
        .filter_by(status=TransactionStatus.NOT_PROCESSABLE)

    if bank_information.offererId:
        query = _keep_only_venues_with_no_bank_information(query)

    return query.all()


def _keep_only_venues_with_no_bank_information(query):
    query = query.filter(Venue.bankInformation == None)
    return query

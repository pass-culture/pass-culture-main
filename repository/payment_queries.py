from typing import List

from flask import render_template
from sqlalchemy import text

from models import PaymentTransaction, Payment, PaymentStatus, Booking, Stock, Offer, Venue, BankInformation
from models.db import db


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


def find_all_for_bank_information(id: str) -> List[Payment]:
    return Payment.query\
        .join(Booking)\
        .join(Stock)\
        .join(Offer)\
        .join(Venue)\
        .join(BankInformation)\
        .filter_by(id=id)\
        .all()

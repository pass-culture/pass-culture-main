from typing import List

from flask import render_template
from sqlalchemy import text

from models import PaymentTransaction, Payment, PaymentStatus
from models.db import db


def find_transaction_checksum(message_id: str) -> str:
    transaction = PaymentTransaction.query.filter_by(messageId=message_id).first()
    return transaction.checksum if transaction else None


def find_error_payments() -> List[Payment]:
    query = render_template('sql/find_payment_ids_with_last_status_error.sql')
    error_payment_ids = db.session.query(PaymentStatus.paymentId).from_statement(text(query)).all()
    return Payment.query.filter(Payment.id.in_(error_payment_ids)).all()

from typing import List

from flask import render_template

from models import PaymentTransaction, Payment
from models.db import db


def find_transaction_checksum(message_id: str) -> str:
    transaction = PaymentTransaction.query.filter_by(messageId=message_id).first()
    return transaction.checksum if transaction else None


def find_error_payments() -> List[Payment]:
    query = render_template('sql/find_payment_ids_with_last_status_error.sql')
    result_set = db.engine.execute(query).fetchall()
    error_payment_ids = list(map(lambda x: x[0], result_set))
    return Payment.query.filter(Payment.id.in_(error_payment_ids)).all()

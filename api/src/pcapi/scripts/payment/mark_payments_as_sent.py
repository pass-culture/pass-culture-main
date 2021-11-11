import datetime
import logging

from sqlalchemy.sql.functions import func

from pcapi.core.bookings.api import mark_bookings_as_reimbursed_from_payment_ids
from pcapi.models import db
from pcapi.models.payment import Payment
from pcapi.models.payment_status import PaymentStatus
from pcapi.models.payment_status import TransactionStatus


logger = logging.getLogger(__name__)


def get_payments_ids_under_review(min_id: int, batch_size: int, transaction_label: str) -> list[int]:
    payments_ids_query = (
        Payment.query.filter(Payment.transactionLabel == transaction_label)
        .filter(Payment.id.between(min_id, min_id + batch_size - 1))
        .join(PaymentStatus)
        .filter(PaymentStatus.status == TransactionStatus.UNDER_REVIEW)
        .group_by(Payment.id)
        .having(func.count("*") > 0)
        .order_by(Payment.id)
        .with_entities(Payment.id)
    )

    return [payment_id for payment_id, in payments_ids_query.all()]


def mark_payments_as_sent(transaction_label: str, batch_size: int = 1000) -> None:
    modified_sum = 0
    min_id = db.session.query(func.min(Payment.id)).filter(Payment.transactionLabel == transaction_label).scalar()
    max_id = db.session.query(func.max(Payment.id)).filter(Payment.transactionLabel == transaction_label).scalar()

    if min_id is None or max_id is None:
        logger.info("No payments needed to be marked as sent")
        return

    now = datetime.datetime.utcnow()
    for batch_start in range(min_id, max_id + 1, batch_size):
        payments_ids = get_payments_ids_under_review(batch_start, batch_size, transaction_label)
        if len(payments_ids) == 0:
            continue

        payment_statuses_to_add: list[PaymentStatus] = []
        for payment_id in payments_ids:
            payment_statuses_to_add.append(PaymentStatus(paymentId=payment_id, status=TransactionStatus.SENT, date=now))

        db.session.bulk_save_objects(payment_statuses_to_add)
        mark_bookings_as_reimbursed_from_payment_ids(payments_ids, now)
        db.session.commit()

        modified_sum += len(payments_ids)

    logger.info("%d payments have been marked as sent for transaction %s", modified_sum, transaction_label)

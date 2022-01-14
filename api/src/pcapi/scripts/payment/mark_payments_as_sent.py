import datetime
import logging

from sqlalchemy.orm import joinedload
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


def mark_payments_batch_as_sent(payments_ids: list[int], now: datetime.datetime) -> None:
    payment_statuses_to_add: list[PaymentStatus] = []
    for payment_id in payments_ids:
        payment_statuses_to_add.append(PaymentStatus(paymentId=payment_id, status=TransactionStatus.SENT, date=now))

    db.session.bulk_save_objects(payment_statuses_to_add)
    mark_bookings_as_reimbursed_from_payment_ids(payments_ids, now)
    db.session.commit()


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

        mark_payments_batch_as_sent(payments_ids, now)
        modified_sum += len(payments_ids)

    logger.info("%d payments have been marked as sent for transaction %s", modified_sum, transaction_label)


def mark_payments_as_sent_from_file(ids_file: str, transaction_label: str, batch_size: int = 1000) -> None:
    """
    Allows to mark as SENT payments whose ids are read from a text file.
    The transaction label is used only to check the payments' ones.
    The file must be a text file with one id per line.

    ---usage---

    Copy the text file on the pod before running the function with `kubectl ps`:
        kubens staging  # choose the correct namespace
        kubectl get pods  # eventually list the pods to retrieve the wanted one (console)
        kubectl cp /local/path/to/reimbursement_ids.txt <the console pod name>:/usr/src

    Open a python interpreter on the pod:
        pc -e staging python

    Run the function:
        from pcapi.scripts.payment.mark_payments_as_sent import mark_payments_as_sent_from_file
        mark_payments_as_sent_from_file('/usr/src/reimbursement_ids.txt', '<the related transaction label>')

    """
    with open(ids_file, "r") as fp:
        ids = [int(_id.strip()) for _id in fp if _id]
    batches = [ids[index : index + batch_size] for index in range(0, len(ids), batch_size)]

    now = datetime.datetime.utcnow()
    for batch_nr, batch in enumerate(batches):
        errors = []
        print(f"processing batch#{batch_nr}", end=": ")
        payments = Payment.query.filter(Payment.id.in_(batch)).options(joinedload(Payment.statuses))
        for payment in payments:
            if payment.transactionLabel != transaction_label:
                errors.append(f"payment#{payment.id}: wrong transaction label '{payment.transactionLabel}'")
            if payment.currentStatus.status != TransactionStatus.UNDER_REVIEW:
                errors.append(f"payment#{payment.id}: wrong transaction status '{payment.currentStatus.status}'")

        if errors:
            print(f"{len(errors)} errors")
            print("\n".join(errors))
        else:
            mark_payments_batch_as_sent(batch, now)
            print(f"{len(batch)} payments marked as sent")

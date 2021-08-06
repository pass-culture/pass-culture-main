import datetime
import logging

from sqlalchemy.sql.functions import func

from pcapi.domain.payments import make_transaction_label
from pcapi.models.payment import Payment
from pcapi.models.payment_status import PaymentStatus
from pcapi.models.payment_status import TransactionStatus
from pcapi.repository import repository


logger = logging.getLogger(__name__)


def _get_execution_dates() -> list[datetime.datetime]:
    response = (
        Payment.query.join(PaymentStatus)
        .filter(PaymentStatus.status == TransactionStatus.PENDING)
        .with_entities(func.date_trunc("day", PaymentStatus.date).label("day"))
        .distinct("day")
        .order_by("day")
        .all()
    )
    return [execution_date for (execution_date,) in response]


def _get_retried_payments_by_execution_date(execution_date: datetime.datetime) -> list[Payment]:
    return (
        Payment.query.join(PaymentStatus)
        .filter(PaymentStatus.status == TransactionStatus.RETRY)
        .filter(func.date_trunc("day", PaymentStatus.date) == execution_date)
        .all()
    )


def _get_sent_date_by_execution_date(
    execution_date: datetime.datetime,
) -> datetime.datetime:
    transaction_label = make_transaction_label(execution_date.date())

    sent_payments_for_transaction_label = (
        PaymentStatus.query.join(Payment)
        .filter(Payment.transactionLabel == transaction_label)
        .filter(PaymentStatus.status == TransactionStatus.SENT)
        .with_entities(PaymentStatus.paymentId)
        .subquery()
    )

    first_adequate_payment = (
        Payment.query.join(PaymentStatus)
        .filter(Payment.transactionLabel == transaction_label)
        .filter(PaymentStatus.status == TransactionStatus.PENDING)
        .filter(func.date_trunc("day", PaymentStatus.date) == execution_date)
        .filter(Payment.id.in_(sent_payments_for_transaction_label))
        .first()
    )
    return first_adequate_payment.currentStatus.date if first_adequate_payment else None


def fix_retried_payments_status() -> None:
    logger.info("Begin script", extra={"script": "fix_retried_payments_status"})
    execution_dates = _get_execution_dates()
    logger.info(
        "Execution dates retrieved",
        extra={
            "executionDates": [execution_date.strftime("%Y-%m-%d") for execution_date in execution_dates],
            "script": "fix_retried_payments_status",
        },
    )
    updated_payments_count = 0
    for execution_date in execution_dates:
        updated_payments = []
        transaction_label = make_transaction_label(execution_date.date())
        retried_payments = _get_retried_payments_by_execution_date(execution_date)
        sent_date = _get_sent_date_by_execution_date(execution_date)
        logger.info(
            "Fix given execution date",
            extra={
                "executionDate": execution_date.strftime("%Y-%m-%d"),
                "transactionLabel": transaction_label,
                "sentDate": sent_date.strftime("%Y-%m-%d %H:%M:%S") if sent_date else None,
                "retriedPaymentsCount": len(retried_payments),
                "script": "fix_retried_payments_status",
            },
        )
        for retried_payment in retried_payments:
            retried_payment.transactionLabel = transaction_label
            if sent_date:
                if retried_payment.currentStatus.status == TransactionStatus.SENT:
                    if retried_payment.currentStatus.date.date() != sent_date.date():
                        sent_status = retried_payment.currentStatus
                        sent_status.date = sent_date
                else:
                    sent_status = PaymentStatus(payment=retried_payment, status=TransactionStatus.SENT, date=sent_date)
                    retried_payment.statuses.append(sent_status)

            updated_payments.append(retried_payment)

        repository.save(*updated_payments)
        updated_payments_count += len(updated_payments)

    logger.info(
        "End script", extra={"updatedPayments": updated_payments_count, "script": "fix_retried_payments_status"}
    )

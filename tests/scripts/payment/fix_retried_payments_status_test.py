import datetime

import pytest

from pcapi.core.payments import factories as payment_factories
from pcapi.models import Payment
from pcapi.models.payment_status import PaymentStatus
from pcapi.models.payment_status import TransactionStatus
from pcapi.scripts.payment.fix_retried_payments_status import fix_retried_payments_status


@pytest.mark.usefixtures("db_session")
def test_mark_retried_payment_as_sent_when_payment_of_same_execution_date_were_sent():
    # Given
    execution_date_1 = datetime.datetime(2021, 5, 10)
    transaction_label_1 = "pass Culture Pro - remboursement 1ère quinzaine 05-2021"
    retried_payment_1 = _build_retried_payment_under_review(
        execution_date_1, "pass Culture Pro - remboursement 1ère quinzaine 02-2020"
    )
    retried_payment_2 = _build_retried_payment_under_review(
        execution_date_1, "pass Culture Pro - remboursement 2nde quinzaine 06-2020"
    )
    payment_1 = _build_sent_payment(execution_date_1, transaction_label_1)

    execution_date_2 = datetime.datetime(2021, 7, 20)
    transaction_label_2 = "pass Culture Pro - remboursement 2nde quinzaine 07-2021"
    retried_payment_3 = _build_retried_payment_under_review(
        execution_date_2, "pass Culture Pro - remboursement 2nde quinzaine 02-2021"
    )
    retried_payment_4 = _build_retried_payment_under_review(
        execution_date_2, "pass Culture Pro - remboursement 2nde quinzaine 06-2021"
    )
    payment_2 = _build_sent_payment(execution_date_2, transaction_label_2)

    # When
    fix_retried_payments_status()

    # Then
    assert PaymentStatus.query.count() == 18 + 4
    payments_statuses_sent = PaymentStatus.query.filter(PaymentStatus.status == TransactionStatus.SENT).count()
    assert payments_statuses_sent == 6

    assert retried_payment_1.currentStatus.status == TransactionStatus.SENT
    assert retried_payment_1.currentStatus.date == payment_1.currentStatus.date
    assert retried_payment_2.currentStatus.status == TransactionStatus.SENT
    assert retried_payment_2.currentStatus.date == payment_1.currentStatus.date
    assert retried_payment_3.currentStatus.status == TransactionStatus.SENT
    assert retried_payment_3.currentStatus.date == payment_2.currentStatus.date
    assert retried_payment_4.currentStatus.status == TransactionStatus.SENT
    assert retried_payment_4.currentStatus.date == payment_2.currentStatus.date

    assert retried_payment_1.transactionLabel == transaction_label_1
    assert retried_payment_2.transactionLabel == transaction_label_1
    assert retried_payment_3.transactionLabel == transaction_label_2
    assert retried_payment_4.transactionLabel == transaction_label_2


@pytest.mark.usefixtures("db_session")
def test_update_retried_payment_sent_date_when_date_is_different_day_from_sent_date_of_payment_of_same_execution_date():
    # Given
    execution_date = datetime.datetime(2021, 5, 10)
    wrong_sent_date = datetime.datetime(2021, 7, 20)
    sent_date = execution_date + datetime.timedelta(days=10)
    transaction_label_1 = "pass Culture Pro - remboursement 1ère quinzaine 05-2021"
    retried_payment = _build_retried_payment_sent(
        execution_date, "pass Culture Pro - remboursement 1ère quinzaine 02-2020", wrong_sent_date
    )
    _build_sent_payment(execution_date, transaction_label_1, sent_date)

    # When
    fix_retried_payments_status()

    # Then
    assert PaymentStatus.query.count() == 7
    payments_statuses_sent = PaymentStatus.query.filter(PaymentStatus.status == TransactionStatus.SENT).count()
    assert payments_statuses_sent == 2

    assert retried_payment.currentStatus.status == TransactionStatus.SENT
    assert retried_payment.currentStatus.date == sent_date

    assert retried_payment.transactionLabel == transaction_label_1


@pytest.mark.usefixtures("db_session")
def test_does_not_update_retried_payment_sent_date_when_date_is_same_day_than_sent_date_of_payment_of_same_execution_date():
    # Given
    execution_date = datetime.datetime(2021, 5, 10)
    transaction_label = "pass Culture Pro - remboursement 1ère quinzaine 05-2021"
    retried_payment_sent_date = execution_date + datetime.timedelta(days=10, hours=5)
    other_payment_sent_date = execution_date + datetime.timedelta(days=10, hours=3)
    retried_payment = _build_retried_payment_sent(
        execution_date, "pass Culture Pro - remboursement 1ère quinzaine 02-2020", retried_payment_sent_date
    )
    _build_sent_payment(execution_date, transaction_label, other_payment_sent_date)

    # When
    fix_retried_payments_status()

    # Then
    assert PaymentStatus.query.count() == 7
    payments_statuses_sent = PaymentStatus.query.filter(PaymentStatus.status == TransactionStatus.SENT).count()
    assert payments_statuses_sent == 2

    assert retried_payment.currentStatus.status == TransactionStatus.SENT
    assert retried_payment.currentStatus.date != other_payment_sent_date
    assert retried_payment.currentStatus.date == retried_payment_sent_date

    assert retried_payment.transactionLabel == transaction_label


@pytest.mark.usefixtures("db_session")
def test_does_not_mark_retried_payment_as_sent_when_payment_of_same_execution_date_were_not_sent():
    # Given
    execution_date = datetime.datetime(2021, 5, 10)
    transaction_label = "pass Culture Pro - remboursement 1ère quinzaine 05-2021"
    retried_payment_1 = _build_retried_payment_under_review(
        execution_date, "pass Culture Pro - remboursement 1ère quinzaine 02-2020"
    )
    retried_payment_2 = _build_retried_payment_under_review(
        execution_date, "pass Culture Pro - remboursement 2nde quinzaine 06-2020"
    )
    _build_under_review_payment(execution_date, transaction_label)

    # When
    fix_retried_payments_status()

    # Then
    assert PaymentStatus.query.count() == 8
    payments_statuses_sent = PaymentStatus.query.filter(PaymentStatus.status == TransactionStatus.SENT).count()
    assert payments_statuses_sent == 0

    assert retried_payment_1.currentStatus.status == TransactionStatus.UNDER_REVIEW
    assert retried_payment_2.currentStatus.status == TransactionStatus.UNDER_REVIEW

    assert retried_payment_1.transactionLabel == transaction_label
    assert retried_payment_2.transactionLabel == transaction_label


@pytest.mark.usefixtures("db_session")
def test_update_transaction_label_of_retried_payment_before_under_review_status_was_implemented():
    # Given
    execution_date = datetime.datetime(2021, 5, 10)
    transaction_label = "pass Culture Pro - remboursement 1ère quinzaine 05-2021"
    retried_payment = _build_retried_payment_sent_before_under_review_status_existed(
        execution_date, "pass Culture Pro - remboursement 1ère quinzaine 02-2020"
    )
    _build_sent_payment_before_under_review_status_existed(execution_date, transaction_label)

    # When
    fix_retried_payments_status()

    # Then
    assert PaymentStatus.query.count() == 5
    payments_statuses_sent = PaymentStatus.query.filter(PaymentStatus.status == TransactionStatus.SENT).count()
    assert payments_statuses_sent == 2

    assert retried_payment.currentStatus.status == TransactionStatus.SENT
    assert retried_payment.transactionLabel == transaction_label


def _build_under_review_payment(execution_date: datetime.datetime, transaction_label: str) -> Payment:
    payment = payment_factories.PaymentFactory(statuses=[], transactionLabel=transaction_label)
    payment_factories.PaymentStatusFactory(payment=payment, status=TransactionStatus.PENDING, date=execution_date)
    payment_factories.PaymentStatusFactory(
        payment=payment, status=TransactionStatus.UNDER_REVIEW, date=execution_date + datetime.timedelta(minutes=10)
    )
    return payment


def _build_sent_payment(
    execution_date: datetime.datetime, transaction_label: str, sent_date: datetime.datetime = None
) -> Payment:
    sent_date = sent_date if sent_date else execution_date + datetime.timedelta(days=10)
    payment = payment_factories.PaymentFactory(statuses=[], transactionLabel=transaction_label)
    payment_factories.PaymentStatusFactory(payment=payment, status=TransactionStatus.PENDING, date=execution_date)
    payment_factories.PaymentStatusFactory(
        payment=payment, status=TransactionStatus.UNDER_REVIEW, date=execution_date + datetime.timedelta(minutes=10)
    )
    payment_factories.PaymentStatusFactory(payment=payment, status=TransactionStatus.SENT, date=sent_date)
    return payment


def _build_retried_payment_under_review(execution_date: datetime.datetime, transaction_label: str) -> Payment:
    retried_payment = payment_factories.PaymentFactory(statuses=[], transactionLabel=transaction_label)
    payment_factories.PaymentStatusFactory(
        payment=retried_payment,
        status=TransactionStatus.NOT_PROCESSABLE,
        date=execution_date - datetime.timedelta(days=30),
    )
    payment_factories.PaymentStatusFactory(payment=retried_payment, status=TransactionStatus.RETRY, date=execution_date)
    payment_factories.PaymentStatusFactory(
        payment=retried_payment,
        status=TransactionStatus.UNDER_REVIEW,
        date=execution_date + datetime.timedelta(minutes=10),
    )
    return retried_payment


def _build_retried_payment_sent(
    execution_date: datetime.datetime, transaction_label: str, sent_date: datetime.datetime
) -> Payment:
    retried_payment = payment_factories.PaymentFactory(statuses=[], transactionLabel=transaction_label)
    payment_factories.PaymentStatusFactory(
        payment=retried_payment,
        status=TransactionStatus.NOT_PROCESSABLE,
        date=execution_date - datetime.timedelta(days=30),
    )
    payment_factories.PaymentStatusFactory(payment=retried_payment, status=TransactionStatus.RETRY, date=execution_date)
    payment_factories.PaymentStatusFactory(
        payment=retried_payment,
        status=TransactionStatus.UNDER_REVIEW,
        date=execution_date + datetime.timedelta(minutes=10),
    )
    payment_factories.PaymentStatusFactory(payment=retried_payment, status=TransactionStatus.SENT, date=sent_date)
    return retried_payment


def _build_sent_payment_before_under_review_status_existed(
    execution_date: datetime.datetime, transaction_label: str
) -> Payment:
    payment = payment_factories.PaymentFactory(statuses=[], transactionLabel=transaction_label)
    payment_factories.PaymentStatusFactory(payment=payment, status=TransactionStatus.PENDING, date=execution_date)
    payment_factories.PaymentStatusFactory(
        payment=payment, status=TransactionStatus.SENT, date=execution_date + datetime.timedelta(minutes=10)
    )
    return payment


def _build_retried_payment_sent_before_under_review_status_existed(
    execution_date: datetime.datetime, transaction_label: str
) -> Payment:
    retried_payment = payment_factories.PaymentFactory(statuses=[], transactionLabel=transaction_label)
    payment_factories.PaymentStatusFactory(
        payment=retried_payment,
        status=TransactionStatus.NOT_PROCESSABLE,
        date=execution_date - datetime.timedelta(days=30),
    )
    payment_factories.PaymentStatusFactory(payment=retried_payment, status=TransactionStatus.RETRY, date=execution_date)
    payment_factories.PaymentStatusFactory(
        payment=retried_payment,
        status=TransactionStatus.SENT,
        date=execution_date + datetime.timedelta(minutes=10),
    )
    return retried_payment

from datetime import timedelta, datetime

import pytest

from models.payment import Payment
from models.payment_status import TransactionStatus, PaymentStatus


def test_set_status_appends_a_status_to_a_new_payment():
    # given
    one_second = timedelta(seconds=1)
    now = datetime.utcnow()
    payment = Payment()

    # when
    payment.setStatus(TransactionStatus.PENDING)

    # then
    assert len(payment.statuses) == 1
    assert payment.statuses[0].status == TransactionStatus.PENDING
    assert payment.statuses[0].detail is None
    assert now - one_second < payment.statuses[0].date < now + one_second


def test_set_status_appends_a_status_to_a_payment_with_existing_status():
    # given
    one_second = timedelta(seconds=1)
    now = datetime.utcnow()
    payment = Payment()
    payment_status = PaymentStatus()
    payment_status.status = TransactionStatus.PENDING
    payment_status.date = datetime.utcnow()
    payment.statuses = [payment_status]

    # when
    payment.setStatus(TransactionStatus.SENT)

    # then
    assert len(payment.statuses) == 2
    assert payment.statuses[1].status == TransactionStatus.SENT
    assert payment.statuses[1].detail is None
    assert now - one_second < payment.statuses[1].date < now + one_second

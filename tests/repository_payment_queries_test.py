import uuid
from datetime import datetime

import pytest

from models import PcObject
from models.payment_status import TransactionStatus, PaymentStatus
from repository.payment_queries import find_transaction_checksum, find_error_payments, find_retry_payments, \
    find_payments_by_transaction_and_message
from tests.conftest import clean_database
from tests.test_utils import create_payment_transaction, create_payment, create_booking, create_user, create_deposit


@pytest.mark.standalone
class FindTransactionChecksumTest:
    @clean_database
    def test_returns_a_checksum_if_message_id_is_known(self, app):
        pass
        # given
        message_id = 'ABCD1234'
        transaction = create_payment_transaction(transaction_message_id=message_id)
        PcObject.check_and_save(transaction)

        # when
        checksum = find_transaction_checksum(message_id)

        # then
        assert checksum == transaction.checksum

    @clean_database
    def test_returns_none_is_message_id_is_unknown(self, app):
        pass
        # given
        message_id = 'ABCD1234'
        transaction = create_payment_transaction(transaction_message_id=message_id)
        PcObject.check_and_save(transaction)

        # when
        checksum = find_transaction_checksum('EFGH5678')

        # then
        assert checksum is None


@pytest.mark.standalone
class FindErrorPaymentsTest:
    @clean_database
    def test_returns_payments_with_last_payment_status_error(self, app):
        # Given
        user = create_user()
        booking = create_booking(user)
        deposit = create_deposit(user, datetime.utcnow())
        error_payment1 = create_payment(booking, booking.stock.resolvedOffer.venue.managingOfferer, 10)
        error_payment2 = create_payment(booking, booking.stock.resolvedOffer.venue.managingOfferer, 10)
        pending_payment = create_payment(booking, booking.stock.resolvedOffer.venue.managingOfferer, 10)
        error_status1 = PaymentStatus()
        error_status1.status = TransactionStatus.ERROR
        error_payment1.statuses.append(error_status1)
        error_status2 = PaymentStatus()
        error_status2.status = TransactionStatus.ERROR
        error_payment2.statuses.append(error_status2)

        PcObject.check_and_save(error_payment1, error_payment2, pending_payment, deposit)

        # When
        payments = find_error_payments()

        # Then
        assert len(payments) == 2
        for p in payments:
            assert p.currentStatus.status == TransactionStatus.ERROR

    @clean_database
    def test_does_not_return_payment_if_has_status_error_but_not_last(self, app):
        # Given
        user = create_user()
        booking = create_booking(user)
        deposit = create_deposit(user, datetime.utcnow())
        error_payment = create_payment(booking, booking.stock.resolvedOffer.venue.managingOfferer, 10)
        pending_payment = create_payment(booking, booking.stock.resolvedOffer.venue.managingOfferer, 10)
        error_status = PaymentStatus()
        error_status.status = TransactionStatus.ERROR
        sent_status = PaymentStatus()
        sent_status.status = TransactionStatus.SENT
        error_payment.statuses.extend([error_status, sent_status])

        PcObject.check_and_save(error_payment, pending_payment, deposit)

        # When
        payments = find_error_payments()

        # Then
        assert payments == []


@pytest.mark.standalone
class FindRetryPaymentsTest:
    @clean_database
    def test_returns_payments_with_last_payment_status_retry(self, app):
        # Given
        user = create_user()
        booking = create_booking(user)
        deposit = create_deposit(user, datetime.utcnow())
        offerer = booking.stock.resolvedOffer.venue.managingOfferer
        retry_payment1 = create_payment(booking, offerer, 10)
        retry_payment2 = create_payment(booking, offerer, 10)
        pending_payment = create_payment(booking, offerer, 10, status=TransactionStatus.PENDING)
        retry_status1 = PaymentStatus()
        retry_status1.status = TransactionStatus.RETRY
        retry_payment1.statuses.append(retry_status1)
        retry_status2 = PaymentStatus()
        retry_status2.status = TransactionStatus.RETRY
        retry_payment2.statuses.append(retry_status2)

        PcObject.check_and_save(retry_payment1, retry_payment2, pending_payment, deposit)

        # When
        payments = find_retry_payments()

        # Then
        assert len(payments) == 2
        for p in payments:
            assert p.currentStatus.status == TransactionStatus.RETRY

    @clean_database
    def test_does_not_return_payment_if_has_status_retry_but_not_last(self, app):
        # Given
        user = create_user()
        booking = create_booking(user)
        deposit = create_deposit(user, datetime.utcnow())
        payment = create_payment(booking, booking.stock.resolvedOffer.venue.managingOfferer, 10)
        pending_payment = create_payment(booking, booking.stock.resolvedOffer.venue.managingOfferer, 10)
        retry_status = PaymentStatus()
        retry_status.status = TransactionStatus.RETRY
        sent_status = PaymentStatus()
        sent_status.status = TransactionStatus.SENT
        payment.statuses.extend([retry_status, sent_status])

        PcObject.check_and_save(payment, pending_payment, deposit)

        # When
        payments = find_retry_payments()

        # Then
        assert payments == []


@pytest.mark.standalone
class FindPaymentByTransactionAndMessageTest:
    @clean_database
    def test_returns_payments_matching_transaction_and_message(self, app):
        # given
        user = create_user()
        booking = create_booking(user)
        deposit = create_deposit(user, datetime.utcnow())
        offerer = booking.stock.resolvedOffer.venue.managingOfferer

        transaction1 = create_payment_transaction(transaction_message_id='XML1')
        transaction2 = create_payment_transaction(transaction_message_id='XML2')
        transaction3 = create_payment_transaction(transaction_message_id='XML3')

        uuid1, uuid2, uuid3 = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()

        payments = [
            create_payment(booking, offerer, 5, transaction_end_ot_end_id=uuid1, transaction=transaction1),
            create_payment(booking, offerer, 5, transaction_end_ot_end_id=uuid2, transaction=transaction2),
            create_payment(booking, offerer, 5, transaction_end_ot_end_id=uuid1, transaction=transaction3),
            create_payment(booking, offerer, 5, transaction_end_ot_end_id=uuid3, transaction=transaction1),
            create_payment(booking, offerer, 5, transaction_end_ot_end_id=uuid1, transaction=transaction1)
        ]

        PcObject.check_and_save(deposit, *payments)

        # when
        matching_payments = find_payments_by_transaction_and_message(uuid1.hex, 'XML1')

        # then
        assert len(matching_payments) == 2
        for p in matching_payments:
            assert p.transactionMessageId == 'XML1'
            assert p.transactionEndToEndId == uuid1

    @clean_database
    def test_returns_nothing_if_message_is_not_matched(self, app):
        # given
        user = create_user()
        booking = create_booking(user)
        deposit = create_deposit(user, datetime.utcnow())
        offerer = booking.stock.resolvedOffer.venue.managingOfferer

        transaction1 = create_payment_transaction(transaction_message_id='XML1')
        transaction2 = create_payment_transaction(transaction_message_id='XML2')
        transaction3 = create_payment_transaction(transaction_message_id='XML3')

        uuid1, uuid2, uuid3 = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()

        payments = [
            create_payment(booking, offerer, 5, transaction_end_ot_end_id=uuid1, transaction=transaction1),
            create_payment(booking, offerer, 5, transaction_end_ot_end_id=uuid2, transaction=transaction2),
            create_payment(booking, offerer, 5, transaction_end_ot_end_id=uuid3, transaction=transaction3)
        ]

        PcObject.check_and_save(deposit, *payments)

        # when
        matching_payments = find_payments_by_transaction_and_message(uuid1.hex, 'unknown message')

        # then
        assert matching_payments == []

    @clean_database
    def test_returns_nothing_if_transaction_is_not_matched(self, app):
        # given
        user = create_user()
        booking = create_booking(user)
        deposit = create_deposit(user, datetime.utcnow())
        offerer = booking.stock.resolvedOffer.venue.managingOfferer

        transaction1 = create_payment_transaction(transaction_message_id='XML1')
        transaction2 = create_payment_transaction(transaction_message_id='XML2')
        transaction3 = create_payment_transaction(transaction_message_id='XML3')

        uuid1, uuid2, uuid3 = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()

        payments = [
            create_payment(booking, offerer, 5, transaction_end_ot_end_id=uuid1, transaction=transaction1),
            create_payment(booking, offerer, 5, transaction_end_ot_end_id=uuid2, transaction=transaction2),
            create_payment(booking, offerer, 5, transaction_end_ot_end_id=uuid3, transaction=transaction3)
        ]

        PcObject.check_and_save(deposit, *payments)
        unknown_transaction = uuid.uuid4()

        # when
        matching_payments = find_payments_by_transaction_and_message(unknown_transaction.hex, 'XML1')

        # then
        assert matching_payments == []

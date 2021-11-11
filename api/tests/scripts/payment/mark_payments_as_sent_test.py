from pcapi.core.bookings.models import BookingStatus
from pcapi.core.payments import factories as payment_factories
from pcapi.models.payment_status import PaymentStatus
from pcapi.models.payment_status import TransactionStatus
from pcapi.scripts.payment.mark_payments_as_sent import mark_payments_as_sent


class MarkPaymentsAsSentTest:
    def test_mark_payments_as_sent(self, app, db_session):
        # Given
        payment1 = payment_factories.PaymentFactory(statuses=[], transactionLabel="transaction_label")
        payment2 = payment_factories.PaymentFactory(statuses=[], transactionLabel="transaction_label")
        payment3 = payment_factories.PaymentFactory(statuses=[], transactionLabel="transaction_label")
        payment4 = payment_factories.PaymentFactory(statuses=[], transactionLabel="transaction_label")
        no_status_under_review_payment = payment_factories.PaymentFactory(
            statuses=[], transactionLabel="transaction_label"
        )
        wrong_transaction_label_payment = payment_factories.PaymentFactory(
            statuses=[], transactionLabel="wrong_transaction_label"
        )
        expected_payments_to_be_marked_as_sent = [payment1, payment2, payment3, payment4]
        expected_payments_not_to_be_marked_as_sent = [no_status_under_review_payment, wrong_transaction_label_payment]
        payment_factories.PaymentStatusFactory(payment=payment1, status=TransactionStatus.UNDER_REVIEW)
        payment_factories.PaymentStatusFactory(payment=payment1, status=TransactionStatus.PENDING)
        payment_factories.PaymentStatusFactory(payment=payment2, status=TransactionStatus.UNDER_REVIEW)
        payment_factories.PaymentStatusFactory(payment=payment3, status=TransactionStatus.UNDER_REVIEW)
        payment_factories.PaymentStatusFactory(payment=payment4, status=TransactionStatus.UNDER_REVIEW)
        payment_factories.PaymentStatusFactory(payment=no_status_under_review_payment, status=TransactionStatus.PENDING)

        # When
        mark_payments_as_sent("transaction_label", 2)

        # Then
        assert PaymentStatus.query.count() == 6 + 4
        payments_statuses_sent = PaymentStatus.query.filter(PaymentStatus.status == TransactionStatus.SENT).all()
        assert len(payments_statuses_sent) == 4
        assert set(status.payment for status in payments_statuses_sent) == set(expected_payments_to_be_marked_as_sent)
        for payment in expected_payments_to_be_marked_as_sent:
            assert payment.booking.status == BookingStatus.REIMBURSED
            assert payment.booking.reimbursementDate == payment.currentStatus.date
        for payment in expected_payments_not_to_be_marked_as_sent:
            assert payment.booking.status != BookingStatus.REIMBURSED
            assert payment.booking.reimbursementDate is None

    def test_mark_payments_as_sent_does_not_fail_when_no_data(self, app, db_session):
        # Given
        mark_payments_as_sent("transaction_label", 2)

        # Then
        assert PaymentStatus.query.count() == 0

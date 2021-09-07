from datetime import datetime
from datetime import timedelta

import pytest

import pcapi.core.users.factories as users_factories
from pcapi.model_creators.generic_creators import create_booking
from pcapi.model_creators.generic_creators import create_payment
from pcapi.model_creators.generic_creators import create_payment_message
from pcapi.model_creators.generic_creators import create_payment_status
from pcapi.models.payment import Payment
from pcapi.models.payment_status import PaymentStatus
from pcapi.models.payment_status import TransactionStatus
from pcapi.repository import repository


class SetStatusTest:
    def test_appends_a_status_to_a_new_payment(self):
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

    def test_appends_a_status_to_a_payment_with_existing_status(self):
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


class PaymentDateTest:
    class InPythonContextTest:
        def test_payment_date_should_return_payment_date_for_status_sent(self):
            # Given
            payment_date = datetime.utcnow()
            payment = Payment()
            payment_status = PaymentStatus()
            payment_status.status = TransactionStatus.SENT
            payment_status.date = payment_date
            payment.statuses = [payment_status]

            # When/Then
            payment_sent_date = payment.lastProcessedDate
            assert payment_sent_date == payment_date  # pylint: disable=comparison-with-callable

        def test_payment_date_should_return_oldest_payment_date_for_status_sent_if_several(self, app):
            # Given
            payment_date = datetime.utcnow()
            payment = Payment()
            payment_status = PaymentStatus()
            payment_status.status = TransactionStatus.SENT
            payment_status.date = payment_date
            payment.statuses = [payment_status]
            older_payment_date = datetime.utcnow() - timedelta(days=1)
            payment_status.status = TransactionStatus.SENT
            payment_status.date = older_payment_date
            payment.statuses = [payment_status]

            # When/Then
            payment_sent_date = payment.lastProcessedDate
            assert payment_sent_date == older_payment_date  # pylint: disable=comparison-with-callable

        def test_payment_date_should_return_no_payment_date_for_status_pending(self):
            # Given
            payment_date = datetime.utcnow()
            payment = Payment()
            payment_status = PaymentStatus()
            payment_status.status = TransactionStatus.PENDING
            payment_status.date = payment_date
            payment.statuses = [payment_status]

            # When/Then
            payment_sent_date = payment.lastProcessedDate
            assert payment_sent_date is None

    class InSQLContextTest:
        @pytest.mark.usefixtures("db_session")
        def test_payment_date_should_return_payment_date_for_status_sent(self, app):
            # Given
            beneficiary = users_factories.BeneficiaryGrant18Factory()
            booking = create_booking(user=beneficiary)
            today = datetime.utcnow()
            offerer = booking.stock.offer.venue.managingOfferer
            payment_message = create_payment_message(name="mon message")
            payment = create_payment(booking, offerer, 5, payment_message=payment_message)
            payment_status = create_payment_status(payment, status=TransactionStatus.SENT, date=today)

            repository.save(payment_status)

            # When
            payment_from_query = Payment.query.with_entities(Payment.lastProcessedDate.label("payment_date")).first()

            # Then
            assert payment_from_query.payment_date == today

        @pytest.mark.usefixtures("db_session")
        def test_payment_date_should_return_oldest_payment_date_for_status_sent_if_several(self, app):
            # Given
            beneficiary = users_factories.BeneficiaryGrant18Factory()
            booking = create_booking(user=beneficiary)
            today = datetime.utcnow()
            yesterday = datetime.utcnow() - timedelta(days=1)
            offerer = booking.stock.offer.venue.managingOfferer
            payment_message = create_payment_message(name="mon message")
            payment = create_payment(booking, offerer, 5, payment_message=payment_message)
            payment_status = create_payment_status(payment, status=TransactionStatus.SENT, date=today)
            create_payment_status(payment, status=TransactionStatus.SENT, date=yesterday)

            repository.save(payment_status)

            # When
            payment_from_query = Payment.query.with_entities(Payment.lastProcessedDate.label("payment_date")).first()

            # Then
            assert payment_from_query.payment_date == yesterday

        @pytest.mark.usefixtures("db_session")
        def test_payment_date_should_return_no_payment_date_for_status_pending(self, app):
            # Given
            beneficiary = users_factories.BeneficiaryGrant18Factory()
            booking = create_booking(user=beneficiary)
            today = datetime.utcnow()
            offerer = booking.stock.offer.venue.managingOfferer
            payment_message = create_payment_message(name="mon message")
            payment = create_payment(booking, offerer, 5, payment_message=payment_message)
            payment_status = create_payment_status(payment, status=TransactionStatus.PENDING, date=today)

            repository.save(payment_status)

            # When
            payment_from_query = Payment.query.with_entities(Payment.lastProcessedDate.label("payment_date")).first()

            # Then
            assert payment_from_query.payment_date is None

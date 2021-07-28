from datetime import datetime

from freezegun import freeze_time
import pytest

from pcapi.core.payments import api
from pcapi.core.payments import factories
from pcapi.core.users.factories import BeneficiaryFactory
from pcapi.models.payment import Payment
from pcapi.models.payment_status import PaymentStatus
from pcapi.models.payment_status import TransactionStatus
from pcapi.repository import repository


class CreateDepositTest:
    @freeze_time("2021-02-05 09:00:00")
    @pytest.mark.usefixtures("db_session")
    def test_deposit_created_with_an_expiration_date(self, app):
        # Given
        beneficiary = BeneficiaryFactory(email="beneficiary@example.com")
        repository.delete(*beneficiary.deposits)

        # When
        deposit = api.create_deposit(beneficiary, "created by test")

        # Then
        assert deposit.expirationDate == datetime(2023, 2, 5, 9, 0, 0)


@pytest.mark.usefixtures("db_session")
class BulkCreatePaymentStatusesTest:
    def test_without_detail(self):
        p1 = factories.PaymentFactory(statuses=[])
        p2 = factories.PaymentFactory(statuses=[])
        _ignored = factories.PaymentFactory(statuses=[])

        query = Payment.query.filter(Payment.id.in_((p1.id, p2.id)))
        api.bulk_create_payment_statuses(query, TransactionStatus.PENDING)

        statuses = PaymentStatus.query.all()
        assert len(statuses) == 2
        assert {s.payment for s in statuses} == {p1, p2}
        assert {s.status for s in statuses} == {TransactionStatus.PENDING}
        assert {s.detail for s in statuses} == {None}

    def test_with_detail(self):
        p1 = factories.PaymentFactory(statuses=[])
        p2 = factories.PaymentFactory(statuses=[])
        _ignored = factories.PaymentFactory(statuses=[])

        query = Payment.query.filter(Payment.id.in_((p1.id, p2.id)))
        api.bulk_create_payment_statuses(query, TransactionStatus.PENDING, "something")

        statuses = PaymentStatus.query.all()
        assert len(statuses) == 2
        assert {s.payment for s in statuses} == {p1, p2}
        assert {s.status for s in statuses} == {TransactionStatus.PENDING}
        assert {s.detail for s in statuses} == {"something"}

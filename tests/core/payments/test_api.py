from datetime import datetime
from datetime import time
from decimal import Decimal

from dateutil.relativedelta import relativedelta
from freezegun import freeze_time
import pytest

from pcapi.core.payments import api
from pcapi.core.payments import exceptions
from pcapi.core.payments import factories as payments_factories
from pcapi.core.payments.models import Deposit
from pcapi.core.payments.models import DepositType
from pcapi.core.testing import override_settings
from pcapi.core.users import factories as users_factories
from pcapi.models.payment import Payment
from pcapi.models.payment_status import PaymentStatus
from pcapi.models.payment_status import TransactionStatus


pytestmark = pytest.mark.usefixtures("db_session")


@freeze_time("2021-02-05 09:00:00")
class CreateDepositTest:
    def test_deposit_created_with_version_1(self):
        beneficiary = users_factories.UserFactory(
            dateOfBirth=datetime.combine(datetime.utcnow(), time(0, 0)) - relativedelta(years=18, months=2)
        )

        deposit = api.create_deposit(beneficiary, "created by test", version=1)

        assert deposit.version == 1
        assert deposit.amount == Decimal(500)
        assert deposit.source == "created by test"

    @pytest.mark.parametrize("age,expected_amount", [(15, Decimal(20)), (16, Decimal(30)), (17, Decimal(30))])
    def test_create_underage_deposit(self, age, expected_amount):
        beneficiary = users_factories.UserFactory(
            dateOfBirth=datetime.combine(datetime.utcnow(), time(0, 0)) - relativedelta(years=age, months=2)
        )

        deposit = api.create_deposit(beneficiary, "created by test", beneficiary.eligibility)

        assert deposit.type == DepositType.GRANT_15_17
        assert deposit.version == 1
        assert deposit.amount == expected_amount
        assert deposit.user.id == beneficiary.id
        assert deposit.expirationDate == datetime(2021 - (age + 1) + 18, 12, 5, 0, 0, 0)

    def test_create_18_years_old_deposit(self):
        beneficiary = users_factories.UserFactory(
            dateOfBirth=datetime.combine(datetime.utcnow(), time(0, 0)) - relativedelta(years=18, months=4)
        )

        deposit = api.create_deposit(beneficiary, "created by test")

        assert deposit.type == DepositType.GRANT_18
        assert deposit.version == 2
        assert deposit.amount == Decimal(300)
        assert deposit.user.id == beneficiary.id
        assert deposit.expirationDate == datetime(2023, 2, 5, 9, 0, 0)

    @override_settings(IS_INTEGRATION=True)
    def test_deposit_on_integration(self):
        beneficiary = users_factories.UserFactory()

        # When
        deposit = api.create_deposit(beneficiary, "integration_signup")

        # Then
        assert deposit.type == DepositType.GRANT_18
        assert deposit.version == 2
        assert deposit.amount == Decimal(300)
        assert deposit.user.id == beneficiary.id
        assert deposit.expirationDate == datetime(2023, 2, 5, 9, 0, 0)

    def test_deposit_created_when_another_type_already_exist_for_user(self):
        birth_date = datetime.combine(datetime.utcnow(), time(0, 0)) - relativedelta(years=18, months=4)
        with freeze_time(datetime.utcnow() - relativedelta(years=3)):
            beneficiary = users_factories.UnderageBeneficiaryFactory(dateOfBirth=birth_date)

        api.create_deposit(beneficiary, "created by test")

        assert beneficiary.deposit.type == DepositType.GRANT_18
        assert len(beneficiary.deposits) == 2

    def test_cannot_create_twice_a_deposit_of_same_type(self):
        # Given
        eighteen_years_in_the_past = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - relativedelta(
            years=18, months=2
        )
        beneficiary = users_factories.BeneficiaryGrant18Factory(dateOfBirth=eighteen_years_in_the_past)

        # When
        with pytest.raises(exceptions.DepositTypeAlreadyGrantedException) as error:
            api.create_deposit(beneficiary, "created by test")

        # Then
        assert Deposit.query.filter(Deposit.userId == beneficiary.id).count() == 1
        assert error.value.errors["user"] == ['Cet utilisateur a déjà été crédité de la subvention "GRANT_18".']


class BulkCreatePaymentStatusesTest:
    def test_without_detail(self):
        p1 = payments_factories.PaymentFactory(statuses=[])
        p2 = payments_factories.PaymentFactory(statuses=[])
        _ignored = payments_factories.PaymentFactory(statuses=[])

        query = Payment.query.filter(Payment.id.in_((p1.id, p2.id)))
        api.bulk_create_payment_statuses(query, TransactionStatus.PENDING)

        statuses = PaymentStatus.query.all()
        assert len(statuses) == 2
        assert {s.payment for s in statuses} == {p1, p2}
        assert {s.status for s in statuses} == {TransactionStatus.PENDING}
        assert {s.detail for s in statuses} == {None}

    def test_with_detail(self):
        p1 = payments_factories.PaymentFactory(statuses=[])
        p2 = payments_factories.PaymentFactory(statuses=[])
        _ignored = payments_factories.PaymentFactory(statuses=[])

        query = Payment.query.filter(Payment.id.in_((p1.id, p2.id)))
        api.bulk_create_payment_statuses(query, TransactionStatus.PENDING, "something")

        statuses = PaymentStatus.query.all()
        assert len(statuses) == 2
        assert {s.payment for s in statuses} == {p1, p2}
        assert {s.status for s in statuses} == {TransactionStatus.PENDING}
        assert {s.detail for s in statuses} == {"something"}

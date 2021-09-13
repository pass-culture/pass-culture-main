from datetime import datetime

from dateutil.relativedelta import relativedelta
from freezegun import freeze_time
import pytest

from pcapi.core.bookings import conf
from pcapi.core.payments import api
from pcapi.core.payments import exceptions
from pcapi.core.payments import factories as payments_factories
from pcapi.core.testing import override_settings
from pcapi.core.users import factories as users_factories
from pcapi.models.deposit import Deposit
from pcapi.models.deposit import DepositType
from pcapi.models.payment import Payment
from pcapi.models.payment_status import PaymentStatus
from pcapi.models.payment_status import TransactionStatus


pytestmark = pytest.mark.usefixtures("db_session")


@freeze_time("2021-02-05 09:00:00")
class CreateDepositTest:
    def test_deposit_created_with_given_deposit_source_and_version(self):
        # Given
        eighteen_years_in_the_past = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - relativedelta(
            years=18, months=2
        )
        beneficiary = users_factories.UserFactory(dateOfBirth=eighteen_years_in_the_past)

        # When
        deposit = api.create_deposit(beneficiary, "created by test", version=1)

        # Then
        assert deposit.version == 1
        assert deposit.source == "created by test"

    def test_deposit_created_with_a_grant_15_which_expire_on_next_birthday_when_beneficiary_is_15_years_old(self):
        # Given
        fifteen_years_in_the_past = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - relativedelta(
            years=15, months=2
        )
        beneficiary = users_factories.UserFactory(dateOfBirth=fifteen_years_in_the_past)

        # When
        deposit = api.create_deposit(beneficiary, "created by test")

        # Then
        assert deposit.type == DepositType.GRANT_15
        assert deposit.version == conf.get_current_deposit_version_for_type(DepositType.GRANT_15)
        assert deposit.amount == conf.get_current_limit_configuration_for_type(DepositType.GRANT_15).TOTAL_CAP
        assert deposit.user.id == beneficiary.id
        assert deposit.expirationDate == datetime(2021, 12, 5, 0, 0, 0)

    def test_deposit_created_with_a_grant_16_which_expire_on_next_birthday_when_beneficiary_is_16_years_old(self):
        # Given
        sixteen_years_in_the_past = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - relativedelta(
            years=16, months=1
        )
        beneficiary = users_factories.UserFactory(dateOfBirth=sixteen_years_in_the_past)

        # When
        deposit = api.create_deposit(beneficiary, "created by test")

        # Then
        assert deposit.type == DepositType.GRANT_16
        assert deposit.version == conf.get_current_deposit_version_for_type(DepositType.GRANT_16)
        assert deposit.amount == conf.get_current_limit_configuration_for_type(DepositType.GRANT_16).TOTAL_CAP
        assert deposit.user.id == beneficiary.id
        assert deposit.expirationDate == datetime(2022, 1, 5, 0, 0, 0)

    def test_deposit_created_with_a_grant_17_which_expire_on_next_birthday_when_beneficiary_is_17_years_old(self):
        # Given
        seventeen_years_in_the_past = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - relativedelta(
            years=17, months=2
        )
        beneficiary = users_factories.UserFactory(dateOfBirth=seventeen_years_in_the_past)

        # When
        deposit = api.create_deposit(beneficiary, "created by test")

        # Then
        assert deposit.type == DepositType.GRANT_17
        assert deposit.version == conf.get_current_deposit_version_for_type(DepositType.GRANT_17)
        assert deposit.amount == conf.get_current_limit_configuration_for_type(DepositType.GRANT_17).TOTAL_CAP
        assert deposit.user.id == beneficiary.id
        assert deposit.expirationDate == datetime(2021, 12, 5, 0, 0, 0)

    def test_deposit_created_with_a_grant_18_which_expire_in_two_years_when_beneficiary_is_18_years_old(self):
        # Given
        eighteen_years_in_the_past = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - relativedelta(
            years=18, months=4
        )
        beneficiary = users_factories.UserFactory(dateOfBirth=eighteen_years_in_the_past)

        # When
        deposit = api.create_deposit(beneficiary, "created by test")

        # Then
        assert deposit.type == DepositType.GRANT_18
        assert deposit.version == conf.get_current_deposit_version_for_type(DepositType.GRANT_18)
        assert deposit.amount == conf.get_current_limit_configuration_for_type(DepositType.GRANT_18).TOTAL_CAP
        assert deposit.user.id == beneficiary.id
        assert deposit.expirationDate == datetime(2023, 2, 5, 9, 0, 0)

    def test_deposit_created_with_a_grant_18_which_expire_in_two_years_when_beneficiary_is_more_than_18_years_old(self):
        # Given
        nineteen_years_in_the_past = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - relativedelta(
            years=19, days=4
        )
        beneficiary = users_factories.UserFactory(dateOfBirth=nineteen_years_in_the_past)

        # When
        deposit = api.create_deposit(beneficiary, "created by test")

        # Then
        assert deposit.type == DepositType.GRANT_18
        assert deposit.version == conf.get_current_deposit_version_for_type(DepositType.GRANT_18)
        assert deposit.amount == conf.get_current_limit_configuration_for_type(DepositType.GRANT_18).TOTAL_CAP
        assert deposit.user.id == beneficiary.id
        assert deposit.expirationDate == datetime(2023, 2, 5, 9, 0, 0)

    @override_settings(IS_INTEGRATION=True)
    def test_deposit_created_with_a_grant_18_which_expire_in_two_years_when_on_integration(self):
        # Given
        beneficiary = users_factories.UserFactory()

        # When
        deposit = api.create_deposit(beneficiary, "created by test")

        # Then
        assert deposit.type == DepositType.GRANT_18
        assert deposit.version == conf.get_current_deposit_version_for_type(DepositType.GRANT_18)
        assert deposit.amount == conf.get_current_limit_configuration_for_type(DepositType.GRANT_18).TOTAL_CAP
        assert deposit.user.id == beneficiary.id
        assert deposit.expirationDate == datetime(2023, 2, 5, 9, 0, 0)

    def test_deposit_created_when_another_type_already_exist_for_user(self):
        # Given
        eighteen_years_in_the_past = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - relativedelta(
            years=18, months=4
        )
        beneficiary = users_factories.UserFactory(dateOfBirth=eighteen_years_in_the_past)
        payments_factories.DepositGrant17Factory(user=beneficiary)

        # When
        deposit = api.create_deposit(beneficiary, "created by test")

        # Then
        assert deposit.type == DepositType.GRANT_18
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

from datetime import datetime
from datetime import time
from decimal import Decimal

from dateutil.relativedelta import relativedelta
from freezegun import freeze_time
import pytest

from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.fraud import models as fraud_models
from pcapi.core.payments import api
from pcapi.core.payments import exceptions
from pcapi.core.payments.models import Deposit
from pcapi.core.payments.models import DepositType
from pcapi.core.testing import override_settings
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models


pytestmark = pytest.mark.usefixtures("db_session")


@freeze_time("2021-02-05 09:00:00")
class CreateDepositTest:
    @pytest.mark.parametrize("age,expected_amount", [(15, Decimal(20)), (16, Decimal(30)), (17, Decimal(30))])
    def test_create_underage_deposit(self, age, expected_amount):
        with freeze_time(datetime.combine(datetime.utcnow(), time(0, 0)) - relativedelta(years=age, months=2)):
            beneficiary = users_factories.UserFactory(dateOfBirth=datetime.utcnow())
        with freeze_time(datetime.utcnow() - relativedelta(month=1)):
            fraud_factories.BeneficiaryFraudCheckFactory(
                user=beneficiary,
                status=fraud_models.FraudCheckStatus.OK,
                type=fraud_models.FraudCheckType.EDUCONNECT,
                eligibilityType=users_models.EligibilityType.UNDERAGE,
                resultContent=fraud_factories.EduconnectContentFactory(registration_datetime=datetime.utcnow()),
            )

        deposit = api.create_deposit(beneficiary, "created by test", beneficiary.eligibility, age_at_registration=age)

        assert deposit.type == DepositType.GRANT_15_17
        assert deposit.version == 1
        assert deposit.amount == expected_amount
        assert deposit.user.id == beneficiary.id
        assert deposit.expirationDate == datetime(2021 - (age + 1) + 18, 12, 5, 0, 0, 0)

    def test_create_18_years_old_deposit(self):
        beneficiary = users_factories.UserFactory(
            dateOfBirth=datetime.combine(datetime.utcnow(), time(0, 0)) - relativedelta(years=18, months=4)
        )

        deposit = api.create_deposit(beneficiary, "created by test", users_models.EligibilityType.AGE18)

        assert deposit.type == DepositType.GRANT_18
        assert deposit.version == 2
        assert deposit.amount == Decimal(300)
        assert deposit.user.id == beneficiary.id
        assert deposit.expirationDate == datetime(2023, 2, 5, 9, 0, 0)

    @override_settings(IS_INTEGRATION=True)
    def test_deposit_on_integration(self):
        beneficiary = users_factories.UserFactory(
            dateOfBirth=datetime.combine(datetime.utcnow(), time(0, 0)) - relativedelta(years=18, months=4)
        )

        # When
        deposit = api.create_deposit(beneficiary, "integration_signup", users_models.EligibilityType.AGE18)

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

        api.create_deposit(beneficiary, "created by test", users_models.EligibilityType.AGE18)

        assert beneficiary.deposit.type == DepositType.GRANT_18
        assert len(beneficiary.deposits) == 2

    def test_cannot_create_twice_a_deposit_of_same_type(self):
        # Given
        AGE18_ELIGIBLE_BIRTH_DATE = datetime.utcnow().replace(
            hour=0, minute=0, second=0, microsecond=0
        ) - relativedelta(years=18, months=2)
        beneficiary = users_factories.BeneficiaryGrant18Factory(dateOfBirth=AGE18_ELIGIBLE_BIRTH_DATE)

        # When
        with pytest.raises(exceptions.DepositTypeAlreadyGrantedException) as error:
            api.create_deposit(beneficiary, "created by test", users_models.EligibilityType.AGE18)

        # Then
        assert Deposit.query.filter(Deposit.userId == beneficiary.id).count() == 1
        assert error.value.errors["user"] == ['Cet utilisateur a déjà été crédité de la subvention "GRANT_18".']

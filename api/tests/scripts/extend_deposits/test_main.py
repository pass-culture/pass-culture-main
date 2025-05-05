from datetime import date

from dateutil.relativedelta import relativedelta
import pytest
import time_machine

from pcapi.core.finance.models import DepositType
from pcapi.core.fraud.factories import BeneficiaryFraudCheckFactory
from pcapi.core.fraud.factories import HonorStatementFraudCheckFactory
from pcapi.core.fraud.factories import ProfileCompletionFraudCheckFactory
from pcapi.core.fraud.models import FraudCheckStatus
from pcapi.core.fraud.models import FraudCheckType
from pcapi.core.users.factories import BeneficiaryFactory
from pcapi.core.users.factories import DepositGrantFactory
from pcapi.core.users.factories import EmailValidatedUserFactory
from pcapi.scripts.extend_deposits.main import AUTHOR_ID
from pcapi.scripts.extend_deposits.main import extend_users_deposit


pytestmark = pytest.mark.usefixtures("db_session")


@pytest.mark.parametrize("deposit_type", [DepositType.GRANT_15_17, DepositType.GRANT_17_18])
def test_should_extend_deposit(deposit_type):
    today = date.today()
    seventeen_years_ago = today - relativedelta(years=17)
    user = BeneficiaryFactory(
        validatedBirthDate=seventeen_years_ago, deposit__type=deposit_type, deposit__expirationDate=today
    )
    EmailValidatedUserFactory(id=AUTHOR_ID)

    extend_users_deposit(not_dry=True)

    when_user_is_twenty_one = seventeen_years_ago + relativedelta(years=21, hours=11)
    assert user.deposit.expirationDate == when_user_is_twenty_one


def test_should_skip_grant_18_deposits():
    today = date.today()
    eighteen_years_ago = today - relativedelta(years=18)
    user = EmailValidatedUserFactory(validatedBirthDate=eighteen_years_ago)
    DepositGrantFactory(user=user, type=DepositType.GRANT_18, expirationDate=today)

    extend_users_deposit(not_dry=True)

    assert user.deposit.expirationDate.date() == today


def test_should_skip_older_users():
    today = date.today()
    twenty_one_years_ago = today - relativedelta(years=21)
    user = EmailValidatedUserFactory(validatedBirthDate=twenty_one_years_ago)
    DepositGrantFactory(user=user, type=DepositType.GRANT_15_17, expirationDate=today)

    extend_users_deposit(not_dry=True)

    assert user.deposit.expirationDate.date() == today


def test_should_skip_incomplete_registration():
    today = date.today()
    last_year = today - relativedelta(years=1)
    eighteen_years_ago = today - relativedelta(years=18)
    with time_machine.travel(last_year):
        user = BeneficiaryFactory(
            age=17,
            validatedBirthDate=eighteen_years_ago,
            phoneNumber="0123456789",
            beneficiaryFraudChecks__type=FraudCheckType.EDUCONNECT,
            deposit__type=DepositType.GRANT_15_17,
            deposit__expirationDate=today,
        )
    ProfileCompletionFraudCheckFactory(user=user)
    BeneficiaryFraudCheckFactory(user=user, type=FraudCheckType.UBBLE, status=FraudCheckStatus.KO)
    HonorStatementFraudCheckFactory(user=user)

    extend_users_deposit(not_dry=True)

    assert user.deposit.expirationDate.date() == today

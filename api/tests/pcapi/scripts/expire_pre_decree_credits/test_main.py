from datetime import datetime

from dateutil.relativedelta import relativedelta
import pytest

from pcapi.core.finance.models import DepositType
from pcapi.core.users.factories import BeneficiaryFactory
from pcapi.core.users.factories import UserFactory
from pcapi.scripts.expire_pre_decree_credits.main import expire_deposits
from pcapi.settings import CREDIT_V3_DECREE_DATETIME


@pytest.mark.usefixtures("db_session")
class ExpireDepositsTest:
    def test_deposit_that_should_have_expired_before_decree(self):
        two_years_before_decree = CREDIT_V3_DECREE_DATETIME - relativedelta(years=2, days=1)
        one_year_after_decree = two_years_before_decree + relativedelta(years=3)
        user = BeneficiaryFactory(
            age=18, dateCreated=two_years_before_decree, deposit__expirationDate=one_year_after_decree
        )
        UserFactory(email="dan.nguyen@passculture.app")

        expire_deposits(not_dry=True)

        assert user.deposit.expirationDate < datetime.today()

    def test_deposit_that_should_have_expired_after_decree(self):
        one_year_before_decree = CREDIT_V3_DECREE_DATETIME - relativedelta(years=1)
        two_years_after_decree = one_year_before_decree + relativedelta(years=3)
        user = BeneficiaryFactory(
            age=18, dateCreated=one_year_before_decree, deposit__expirationDate=two_years_after_decree
        )
        UserFactory(email="dan.nguyen@passculture.app")

        expire_deposits(not_dry=True)

        assert user.deposit.expirationDate == two_years_after_decree

    def test_underage_deposit_that_should_not_be_expired(self):
        two_years_before_decree = CREDIT_V3_DECREE_DATETIME - relativedelta(years=2)
        one_year_after_decree = two_years_before_decree + relativedelta(years=3)
        user = BeneficiaryFactory(
            age=17, dateCreated=two_years_before_decree, deposit__expirationDate=one_year_after_decree
        )
        UserFactory(email="dan.nguyen@passculture.app")

        expire_deposits(not_dry=True)

        assert user.deposit.expirationDate == one_year_after_decree

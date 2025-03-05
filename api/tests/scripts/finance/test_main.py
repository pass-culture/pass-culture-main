from decimal import Decimal

from dateutil.relativedelta import relativedelta
import pytest

from pcapi.core.finance.models import RecreditType
from pcapi.core.users.models import EligibilityType
from pcapi.core.users.factories import BeneficiaryFactory
from pcapi.core.fraud.factories import ProfileCompletionFraudCheckFactory
from pcapi.scripts.finance.main import fix_pre_decree_deposit_amount
from pcapi.settings import CREDIT_V3_DECREE_DATETIME


@pytest.mark.usefixtures("db_session")
class FixDepositAmountTest:
    def test_deposit_fix(self):
        before_decree = CREDIT_V3_DECREE_DATETIME - relativedelta(days=1)
        user = BeneficiaryFactory(age=18, beneficiaryFraudChecks__dateCreated=before_decree)

        fix_pre_decree_deposit_amount()

        deposit = user.deposit
        assert deposit.amount == Decimal("300")
        assert any(recredit.recreditType == RecreditType.MANUAL_MODIFICATION for recredit in deposit.recredits)

    def test_deposit_fix_only_if_eighteen_recredit_already_granted(self):
        before_decree = CREDIT_V3_DECREE_DATETIME - relativedelta(days=1)
        user = BeneficiaryFactory(age=17, dateCreated=before_decree)
        ProfileCompletionFraudCheckFactory(user=user, eligibilityType=EligibilityType.AGE18, dateCreated=before_decree)

        fix_pre_decree_deposit_amount()

        deposit = user.deposit
        assert deposit.amount != Decimal("300")
        assert not any(recredit.recreditType == RecreditType.MANUAL_MODIFICATION for recredit in deposit.recredits)

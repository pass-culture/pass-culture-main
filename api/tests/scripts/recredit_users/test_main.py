from decimal import Decimal

import pytest

from pcapi.core.finance.models import RecreditType
from pcapi.core.users.factories import BeneficiaryFactory
from pcapi.scripts.recredit_user.main import recredit_user_for_17_yo


@pytest.mark.usefixtures("db_session")
def test_recredit_user():
    user = BeneficiaryFactory(age=18)
    starting_credit = user.deposit.amount

    recredit_user_for_17_yo(user)

    assert user.deposit.amount == starting_credit + Decimal("50")
    assert RecreditType.RECREDIT_17 in [recredit.recreditType for recredit in user.deposit.recredits]

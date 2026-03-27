from datetime import datetime

import pytest
from dateutil.relativedelta import relativedelta

from pcapi.core.users.factories import BeneficiaryFactory
from pcapi.scripts.extend_deposit.main import extend_deposit


@pytest.mark.usefixtures("db_session")
def test_deposit_extension():
    user = BeneficiaryFactory.create()
    in_two_weeks = datetime.now(tz=None) + relativedelta(weeks=2)

    extend_deposit(user, in_two_weeks)

    assert user.deposit.expirationDate == in_two_weeks

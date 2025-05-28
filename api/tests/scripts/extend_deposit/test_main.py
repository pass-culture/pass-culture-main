from datetime import date
from datetime import datetime

import pytest
from dateutil.relativedelta import relativedelta

from pcapi.core.users.factories import BeneficiaryFactory
from pcapi.core.users.factories import UserFactory
from pcapi.scripts.extend_deposit.main import AUTHOR_ID
from pcapi.scripts.extend_deposit.main import extend_user_deposit


@pytest.mark.usefixtures("db_session")
def test_deposit_extension():
    _author = UserFactory(id=AUTHOR_ID)
    last_year = datetime.utcnow() - relativedelta(years=1)
    beneficiary = BeneficiaryFactory(age=18)
    beneficiary.deposit.expirationDate = last_year

    extend_user_deposit(beneficiary.id, not_dry=True)

    in_thirty_days = date.today() + relativedelta(days=30)
    assert beneficiary.deposit.expirationDate.date() == in_thirty_days

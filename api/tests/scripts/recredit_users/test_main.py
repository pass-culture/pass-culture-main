import pytest

from pcapi.core.finance.models import RecreditType
from pcapi.core.users.factories import BeneficiaryFactory
from pcapi.scripts.recredit_user.main import recredit_user
from pcapi.utils.transaction_manager import atomic


@pytest.mark.usefixtures("db_session")
def test_recredit_user():
    user = BeneficiaryFactory()

    with atomic():
        recredit_user(user.id)

    assert user.deposit.amount == 300
    assert RecreditType.MANUAL_MODIFICATION in [recredit.recreditType for recredit in user.deposit.recredits]

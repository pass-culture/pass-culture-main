import pytest

from pcapi.core.payments.models import Deposit
from pcapi.core.users.models import User
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_app_users import create_industrial_app_users


@pytest.mark.usefixtures("db_session")
class CreateIndustrialWebappUsersTest:
    def test_create_industrial_app_users(self):
        create_industrial_app_users()
        assert User.query.count() == 5 * 2 * 2 + 3 * 2 + 2 * 2 + 3 + 10
        assert Deposit.query.count() == 5 * 2 * 2 * 2 + 3 * 2 + 6

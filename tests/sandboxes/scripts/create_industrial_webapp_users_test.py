import pytest

from pcapi.core.users.models import User
from pcapi.models.deposit import Deposit
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_webapp_users import create_industrial_webapp_users


@pytest.mark.usefixtures("db_session")
class CreateIndustrialWebappUsersTest:
    def test_create_industrial_webapp_users(self):
        create_industrial_webapp_users()
        assert User.query.count() == 7 * 2 * 2 + 3
        assert Deposit.query.count() == (7 - 2) * 2 * 2

import pytest

from pcapi.core.users import factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


class UsersFactoriesTest:
    def test_user_suspension_factory(self):
        suspension = users_factories.UserSuspensionByFraudFactory()

        assert not suspension.user.isActive
        assert suspension.user.suspension_reason
        assert suspension.user.suspension_date
        assert suspension.actorUser.has_admin_role

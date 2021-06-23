import pytest

from pcapi.core.users import factories as user_factories
from pcapi.core.users.exceptions import InvalidUserRoleException
from pcapi.core.users.models import User
from pcapi.core.users.models import UserRole


@pytest.mark.usefixtures("db_session")
class UserTest:
    class UserRoleTest:
        def test_has_admin_role(self):
            user = user_factories.UserFactory(roles=[UserRole.ADMIN])

            assert user.has_admin_role
            assert User.query.filter(User.has_admin_role.is_(False)).all() == []
            assert User.query.filter(User.has_admin_role.is_(True)).all() == [user]

        def test_has_beneficiary_role(self):
            user = user_factories.UserFactory(roles=[UserRole.BENEFICIARY])

            assert user.has_beneficiary_role
            assert User.query.filter(User.has_beneficiary_role.is_(False)).all() == []
            assert User.query.filter(User.has_beneficiary_role.is_(True)).all() == [user]

        def test_has_pro_role(self):
            user = user_factories.UserFactory(roles=[UserRole.PRO])

            assert user.has_pro_role
            assert User.query.filter(User.has_pro_role.is_(False)).all() == []
            assert User.query.filter(User.has_pro_role.is_(True)).all() == [user]

        def test_add_admin_role(self):
            user = user_factories.UserFactory(roles=[UserRole.PRO])

            user.add_admin_role()

            assert user.has_admin_role

        def test_add_beneficiary_role(self):
            user = user_factories.UserFactory(roles=[UserRole.PRO])

            user.add_beneficiary_role()

            assert user.has_beneficiary_role

        def test_add_pro_role(self):
            user = user_factories.UserFactory(roles=[UserRole.ADMIN])

            user.add_pro_role()

            assert user.has_pro_role

        def test_cannot_add_beneficiary_role_to_an_admin(self):
            user = user_factories.UserFactory(roles=[UserRole.ADMIN])

            with pytest.raises(InvalidUserRoleException):
                user.add_beneficiary_role()

                assert not user.has_beneficiary_role
                assert user.has_admin_role

        def test_cannot_add_admin_role_to_a_beneficiary(self):
            user = user_factories.UserFactory(roles=[UserRole.BENEFICIARY])

            with pytest.raises(InvalidUserRoleException):
                user.add_admin_role()

                assert user.has_beneficiary_role
                assert not user.has_admin_role

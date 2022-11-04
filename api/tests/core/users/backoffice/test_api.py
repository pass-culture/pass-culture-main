import pytest

import pcapi.core.permissions.models as perm_models
from pcapi.core.testing import assert_num_queries
import pcapi.core.users.backoffice.api as backoffice_api
import pcapi.core.users.factories as users_factories
import pcapi.core.users.models as users_models

from tests.routes.backoffice_v3.conftest import ROLE_PERMISSIONS
from tests.routes.backoffice_v3.conftest import legit_user_fixture  # pylint: disable=unused-import
from tests.routes.backoffice_v3.conftest import roles_with_permissions_fixture  # pylint: disable=unused-import


pytestmark = pytest.mark.usefixtures("db_session")


def test_fetch_user_with_profile(legit_user) -> None:
    user_id = legit_user.id

    with assert_num_queries(1):
        user_with_profile = backoffice_api.fetch_user_with_profile(user_id)
        assert user_with_profile.backoffice_profile.permissions


class UpsertRolesTest:
    def test_add_one_role(self, roles_with_permissions) -> None:
        user = users_factories.BeneficiaryGrant18Factory()
        roles = [perm_models.Roles.SUPPORT_N1]

        backoffice_api.upsert_roles(user, roles)

        user = users_models.User.query.get(user.id)
        assert {role.name for role in user.backoffice_profile.roles} == {"support-N1"}

        user_permissions = user.backoffice_profile.permissions
        expected_permissions = ROLE_PERMISSIONS["support-N1"]
        assert set(user_permissions) == set(expected_permissions)

    def test_two_roles(self, roles_with_permissions) -> None:
        user = users_factories.BeneficiaryGrant18Factory()
        roles = [perm_models.Roles.SUPPORT_N1, perm_models.Roles.SUPPORT_PRO]

        backoffice_api.upsert_roles(user, roles)

        user = users_models.User.query.get(user.id)
        assert {role.name for role in user.backoffice_profile.roles} == {"support-N1", "support-pro"}

        user_permissions = user.backoffice_profile.permissions
        expected_permissions = ROLE_PERMISSIONS["support-N1"] + ROLE_PERMISSIONS["support-pro"]
        assert set(user_permissions) == set(expected_permissions)

    def test_add_role_to_existing_ones(self, roles_with_permissions) -> None:
        user = users_factories.BeneficiaryGrant18Factory()

        backoffice_api.upsert_roles(user, [perm_models.Roles.SUPPORT_N1])
        backoffice_api.upsert_roles(user, [perm_models.Roles.SUPPORT_PRO, perm_models.Roles.ADMIN])

        user = users_models.User.query.get(user.id)
        assert {role.name for role in user.backoffice_profile.roles} == {"support-N1", "support-pro", "admin"}

        user_permissions = user.backoffice_profile.permissions
        expected_permissions = (
            ROLE_PERMISSIONS["support-N1"] + ROLE_PERMISSIONS["support-pro"] + ROLE_PERMISSIONS["admin"]
        )

        assert set(user_permissions) == set(expected_permissions)

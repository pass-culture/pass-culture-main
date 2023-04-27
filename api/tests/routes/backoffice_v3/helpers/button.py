import pytest
import sqlalchemy as sa

import pcapi.core.permissions.models as perm_models
import pcapi.core.users.backoffice.api as backoffice_api
import pcapi.core.users.factories as users_factories
import pcapi.core.users.models as users_models


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice_v3,
]


class ButtonHelper:
    @property
    def button_label(self) -> str:
        return ""

    @property
    def needed_permission(self) -> perm_models.Permissions:
        return perm_models.Permissions.MANAGE_PRO_ENTITY

    @property
    def unauthorized_user(self) -> users_models.User:
        user = users_factories.UserFactory()
        user.backoffice_profile = perm_models.BackOfficeUserProfile(user=user)

        query = perm_models.Role.query.options(sa.orm.joinedload(perm_models.Role.permissions))
        roles_without_needed_permission = [
            perm_models.Roles(role.name) for role in query if not role.has_permission(self.needed_permission)
        ]

        backoffice_api.upsert_roles(user, roles_without_needed_permission)

        return user

    def test_button_when_can_add_one(self, authenticated_client):
        response = authenticated_client.get(self.path)
        assert response.status_code == 200

        assert self.button_label in response.data.decode("utf-8")

    def test_no_button(self, client, roles_with_permissions):
        client = client.with_bo_session_auth(self.unauthorized_user)

        response = client.get(self.path)
        assert response.status_code == 200

        assert self.button_label not in response.data.decode("utf-8")

from unittest import mock

from flask import url_for
import pytest

from pcapi.core.permissions.factories import RoleFactory
from pcapi.core.permissions.models import Permission
from pcapi.core.permissions.models import Permissions
from pcapi.core.users.factories import UserFactory
from pcapi.repository import repository


pytestmark = pytest.mark.usefixtures("db_session")


class RoleListTest:
    def test_can_list_roles_as_admin(self, client):
        # given
        permission = Permission.query.filter_by(name=Permissions.MANAGE_PERMISSIONS.value).first()
        role = RoleFactory(name="admin")
        RoleFactory(name="test_role")
        role.permissions.append(permission)
        repository.save(role)
        user = UserFactory()

        with mock.patch("flask_login.utils._get_user") as current_user_mock:
            user.groups = ["admin"]
            current_user_mock.return_value = user

            # when
            response = client.with_session_auth(user.email).get(url_for("backoffice_blueprint.list_roles"))

        # then
        assert response.status_code == 200
        roles = response.json["roles"]
        assert set(role["name"] for role in roles) == {"admin", "test_role"}
        # assert "admin" in [role["name"] for role in roles]
        # assert "test_role" in [role["name"] for role in roles]

    def test_cannot_list_roles_as_non_admin(self, client):
        # given
        permission = Permission.query.filter_by(name=Permissions.MANAGE_PERMISSIONS.value).first()
        role = RoleFactory(name="admin")
        RoleFactory(name="not_admin")
        role.permissions.append(permission)
        repository.save(role)
        user = UserFactory()

        with mock.patch("flask_login.utils._get_user") as current_user_mock:
            user.groups = ["not_admin"]
            current_user_mock.return_value = user

            # when
            response = client.with_session_auth(user.email).get(url_for("backoffice_blueprint.list_roles"))

        # then
        assert response.status_code == 403

    def test_cannot_list_roles_as_anonymous(self, client):
        # given
        permission = Permission.query.filter_by(name=Permissions.MANAGE_PERMISSIONS.value).first()
        role = RoleFactory(name="admin")
        RoleFactory(name="test_role")
        role.permissions.append(permission)
        repository.save(role)
        user = UserFactory()

        with mock.patch("flask_login.utils._get_user") as current_user_mock:
            current_user_mock.return_value = user

            # when
            response = client.get(url_for("backoffice_blueprint.list_roles"))

        # then
        assert response.status_code == 401

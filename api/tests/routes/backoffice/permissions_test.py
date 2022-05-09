from unittest import mock

from flask import url_for
import pytest

from pcapi.core.permissions.factories import PermissionFactory
from pcapi.core.permissions.factories import RoleFactory
from pcapi.core.permissions.models import Permission
from pcapi.core.permissions.models import Permissions
from pcapi.core.permissions.models import Role
from pcapi.core.testing import override_features
from pcapi.core.users.factories import UserFactory
from pcapi.repository import repository


pytestmark = pytest.mark.usefixtures("db_session")


def create_admin_role():
    permission = Permission.query.filter_by(name=Permissions.MANAGE_PERMISSIONS.name).first()
    role = RoleFactory(name="admin")
    role.permissions.append(permission)
    repository.save(role)

    return role


class RoleListTest:
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_list_roles_as_admin(self, client):
        # given
        admin_role = create_admin_role()
        RoleFactory(name="test_role")
        user = UserFactory()
        user.groups = [admin_role.name]

        with mock.patch("flask_login.utils._get_user") as current_user_mock:
            current_user_mock.return_value = user

            # when
            response = client.with_session_auth(user.email).get(url_for("backoffice_blueprint.list_roles"))

        # then
        assert response.status_code == 200
        roles = response.json["roles"]
        assert set(role["name"] for role in roles) == {"admin", "test_role"}

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_list_roles_as_non_admin(self, client):
        # given
        create_admin_role()
        non_admin_role = RoleFactory(name="not_admin")
        user = UserFactory()
        user.groups = [non_admin_role.name]

        with mock.patch("flask_login.utils._get_user") as current_user_mock:
            current_user_mock.return_value = user

            # when
            response = client.with_session_auth(user.email).get(url_for("backoffice_blueprint.list_roles"))

        # then
        assert response.status_code == 403

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_list_roles_as_anonymous(self, client):
        # given
        create_admin_role()

        # when
        response = client.get(url_for("backoffice_blueprint.list_roles"))

        # then
        assert response.status_code == 401


class PermissionListTest:
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_list_permissions_as_admin(self, client):
        # given
        admin_role = create_admin_role()
        PermissionFactory(name="test_permission")
        user = UserFactory()
        user.groups = [admin_role.name]

        with mock.patch("flask_login.utils._get_user") as current_user_mock:
            current_user_mock.return_value = user

            # when
            response = client.with_session_auth(user.email).get(url_for("backoffice_blueprint.list_permissions"))

        # then
        assert response.status_code == 200
        permissions = response.json["permissions"]
        assert set(perm["name"] for perm in permissions) == {
            *[p.name for p in Permissions],
            "test_permission",
        }

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_list_permissions_as_non_admin(self, client):
        # given
        create_admin_role()
        non_admin_role = RoleFactory(name="not_admin")
        user = UserFactory()
        user.groups = [non_admin_role.name]

        with mock.patch("flask_login.utils._get_user") as current_user_mock:
            current_user_mock.return_value = user

            # when
            response = client.with_session_auth(user.email).get(url_for("backoffice_blueprint.list_permissions"))

        # then
        assert response.status_code == 403

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_list_permissions_as_anonymous(self, client):
        # given
        create_admin_role()

        # when
        response = client.get(url_for("backoffice_blueprint.list_permissions"))

        # then
        assert response.status_code == 401


class NewRoleTest:
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_create_new_role_with_permissions_as_admin(self, client):
        # given
        admin_role = create_admin_role()
        user = UserFactory()
        user.groups = [admin_role.name]
        permissions = (PermissionFactory(), PermissionFactory())
        new_role_data = {"name": "dummy_role", "permissionIds": [p.id for p in permissions]}

        with mock.patch("flask_login.utils._get_user") as current_user_mock:
            current_user_mock.return_value = user

            # when
            response = client.with_session_auth(user.email).post(
                url_for("backoffice_blueprint.create_role"),
                json=new_role_data,
            )

        # then
        assert response.status_code == 200
        assert response.json["name"] == new_role_data["name"]
        assert {p["id"] for p in response.json["permissions"]} == set(new_role_data["permissionIds"])
        new_role_query = Role.query.filter_by(name=new_role_data["name"])
        assert new_role_query.count() == 1
        inserted_role = new_role_query[0]
        assert inserted_role.name == new_role_data["name"]
        assert set(inserted_role.permissions) == set(permissions)

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_create_new_role_with_empty_permissions_as_admin(self, client):
        # given
        admin_role = create_admin_role()
        user = UserFactory()
        user.groups = [admin_role.name]
        new_role_data = {"name": "dummy_role", "permissionIds": []}

        with mock.patch("flask_login.utils._get_user") as current_user_mock:
            current_user_mock.return_value = user

            # when
            response = client.with_session_auth(user.email).post(
                url_for("backoffice_blueprint.create_role"),
                json=new_role_data,
            )

        # then
        assert response.status_code == 200
        assert response.json["name"] == new_role_data["name"]
        assert response.json["permissions"] == []
        new_role_query = Role.query.filter_by(name=new_role_data["name"])
        assert new_role_query.count() == 1
        inserted_role = new_role_query[0]
        assert inserted_role.name == new_role_data["name"]
        assert inserted_role.permissions == []

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_create_new_role_with_empty_name_as_admin(self, client):
        # given
        admin_role = create_admin_role()
        user = UserFactory()
        user.groups = [admin_role.name]
        new_role_data = {"name": "", "permissionIds": []}

        with mock.patch("flask_login.utils._get_user") as current_user_mock:
            current_user_mock.return_value = user

            # when
            response = client.with_session_auth(user.email).post(
                url_for("backoffice_blueprint.create_role"),
                json=new_role_data,
            )

        # then
        assert response.status_code == 400

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_create_new_role_as_non_admin(self, client):
        # given
        create_admin_role()
        non_admin_role = RoleFactory(name="not_admin")
        user = UserFactory()
        user.groups = [non_admin_role.name]

        with mock.patch("flask_login.utils._get_user") as current_user_mock:
            current_user_mock.return_value = user

            # when
            response = client.with_session_auth(user.email).post(
                url_for("backoffice_blueprint.create_role"),
                json={"name": "should not work", "permissionsIds": []},
            )

        # then
        assert response.status_code == 403

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_create_new_role_as_anonymous(self, client):
        # given
        create_admin_role()

        # when
        response = client.post(
            url_for("backoffice_blueprint.create_role"),
            json={"name": "should not work", "permissionsIds": []},
        )

        # then
        assert response.status_code == 401


class UpdateRoleTest:
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_update_role_with_permissions_as_admin(self, client):
        # given
        admin_role = create_admin_role()
        user = UserFactory()
        user.groups = [admin_role.name]
        permissions = (PermissionFactory(), PermissionFactory())
        existing_role = RoleFactory(name="dummy_role", permissions=[permissions[0]])
        new_role_data = {"name": "updated_role", "permissionIds": [p.id for p in permissions]}

        with mock.patch("flask_login.utils._get_user") as current_user_mock:
            current_user_mock.return_value = user

            # when
            response = client.with_session_auth(user.email).put(
                url_for("backoffice_blueprint.update_role", id_=existing_role.id),
                json=new_role_data,
            )

        # then
        assert response.status_code == 200
        assert response.json["name"] == new_role_data["name"]
        assert {p["id"] for p in response.json["permissions"]} == set(new_role_data["permissionIds"])
        new_role_query = Role.query.filter_by(name=new_role_data["name"])
        assert new_role_query.count() == 1
        inserted_role = new_role_query[0]
        assert inserted_role.name == new_role_data["name"]
        assert set(inserted_role.permissions) == set(permissions)

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_update_role_with_empty_permissions_as_admin(self, client):
        # given
        admin_role = create_admin_role()
        user = UserFactory()
        user.groups = [admin_role.name]
        existing_role = RoleFactory(name="dummy_role", permissions=[PermissionFactory()])
        new_role_data = {"name": "updated_role", "permissionIds": []}

        with mock.patch("flask_login.utils._get_user") as current_user_mock:
            current_user_mock.return_value = user

            # when
            response = client.with_session_auth(user.email).put(
                url_for("backoffice_blueprint.update_role", id_=existing_role.id),
                json=new_role_data,
            )

        # then
        assert response.status_code == 200
        assert response.json["name"] == new_role_data["name"]
        assert response.json["permissions"] == []
        new_role_query = Role.query.filter_by(name=new_role_data["name"])
        assert new_role_query.count() == 1
        inserted_role = new_role_query[0]
        assert inserted_role.name == new_role_data["name"]
        assert inserted_role.permissions == []

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_update_role_with_empty_name_as_admin(self, client):
        # given
        admin_role = create_admin_role()
        user = UserFactory()
        user.groups = [admin_role.name]
        existing_role = RoleFactory(name="dummy_role", permissions=[PermissionFactory()])
        new_role_data = {"name": "", "permissionIds": []}

        with mock.patch("flask_login.utils._get_user") as current_user_mock:
            current_user_mock.return_value = user

            # when
            response = client.with_session_auth(user.email).put(
                url_for("backoffice_blueprint.update_role", id_=existing_role.id),
                json=new_role_data,
            )

        # then
        assert response.status_code == 400

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_update_role_as_non_admin(self, client):
        # given
        create_admin_role()
        non_admin_role = RoleFactory(name="not_admin")
        existing_role = RoleFactory(name="dummy_role", permissions=[PermissionFactory()])
        user = UserFactory()
        user.groups = [non_admin_role.name]

        with mock.patch("flask_login.utils._get_user") as current_user_mock:
            current_user_mock.return_value = user

            # when
            response = client.with_session_auth(user.email).put(
                url_for("backoffice_blueprint.update_role", id_=existing_role.id),
                json={"name": "should not work", "permissionsIds": []},
            )

        # then
        assert response.status_code == 403

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_update_role_as_anonymous(self, client):
        # given
        create_admin_role()
        existing_role = RoleFactory(name="dummy_role", permissions=[PermissionFactory()])

        # when
        response = client.put(
            url_for("backoffice_blueprint.update_role", id_=existing_role.id),
            json={"name": "should not work", "permissionsIds": []},
        )

        # then
        assert response.status_code == 401


class DeleteRoleTest:
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_delete_role_with_permissions_as_admin(self, client):
        # given
        admin_role = create_admin_role()
        permissions = (PermissionFactory(), PermissionFactory())
        role = RoleFactory(name="dummy_role", permissions=[permissions[0]])
        user = UserFactory()
        user.groups = [admin_role.name]

        with mock.patch("flask_login.utils._get_user") as current_user_mock:
            current_user_mock.return_value = user

            # when
            response = client.with_session_auth(user.email).delete(
                url_for("backoffice_blueprint.delete_role", id_=role.id)
            )

        # then
        assert response.status_code == 204
        assert Role.query.filter_by(id=role.id).count() == 0

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_delete_role_with_empty_permissions_as_admin(self, client):
        # given
        admin_role = create_admin_role()
        role = RoleFactory(name="dummy_role")
        user = UserFactory()
        user.groups = [admin_role.name]

        with mock.patch("flask_login.utils._get_user") as current_user_mock:
            current_user_mock.return_value = user

            # when
            response = client.with_session_auth(user.email).delete(
                url_for("backoffice_blueprint.delete_role", id_=role.id)
            )

        # then
        assert response.status_code == 204
        assert Role.query.filter_by(id=role.id).count() == 0

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_delete_admin_role_as_admin(self, client):
        # given
        admin_role = create_admin_role()
        user = UserFactory()
        user.groups = [admin_role.name]

        with mock.patch("flask_login.utils._get_user") as current_user_mock:
            current_user_mock.return_value = user

            # when
            response = client.with_session_auth(user.email).delete(
                url_for("backoffice_blueprint.delete_role", id_=admin_role.id)
            )

        # then
        assert response.status_code == 400
        assert "Cannot delete admin role" in response.json.values()

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_delete_role_as_non_admin(self, client):
        # given
        create_admin_role()
        non_admin_role = RoleFactory(name="not_admin")
        role = RoleFactory(name="dummy_role")
        user = UserFactory()
        user.groups = [non_admin_role.name]

        with mock.patch("flask_login.utils._get_user") as current_user_mock:
            current_user_mock.return_value = user

            # when
            response = client.with_session_auth(user.email).delete(
                url_for("backoffice_blueprint.delete_role", id_=role.id)
            )

        # then
        assert response.status_code == 403

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_delete_role_as_anonymous(self, client):
        # given
        create_admin_role()
        role = RoleFactory(name="dummy_role")

        # when
        response = client.delete(url_for("backoffice_blueprint.delete_role", id_=role.id))

        # then
        assert response.status_code == 401

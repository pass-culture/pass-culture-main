from flask import url_for
import pytest

from pcapi.core.auth.api import generate_token
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
    def test_can_list_roles(self, client):
        # given
        RoleFactory(name="test_role_1")
        RoleFactory(name="test_role_2")
        user = UserFactory()
        auth_token = generate_token(user, [Permissions.MANAGE_PERMISSIONS])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.list_roles"),
        )

        # then
        assert response.status_code == 200
        roles = response.json["roles"]
        assert set(role["name"] for role in roles) == {"test_role_1", "test_role_2"}

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_list_roles_without_permission(self, client):
        # given
        RoleFactory(name="test_role_1")
        RoleFactory(name="test_role_2")
        user = UserFactory()
        auth_token = generate_token(user, [])

        # when
        response = client.get(
            url_for("backoffice_blueprint.list_roles"),
            headers={"Authorization": auth_token},
        )

        # then
        assert response.status_code == 403

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_list_roles_as_anonymous(self, client):
        # given
        auth_token = generate_token(UserFactory.build(), [Permissions.MANAGE_PERMISSIONS])

        # when
        response = client.get(
            url_for("backoffice_blueprint.list_roles"),
            headers={"Authorization": auth_token},
        )

        # then
        assert response.status_code == 403


class PermissionListTest:
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_list_permissions(self, client):
        # given
        PermissionFactory(name="test_permission_1")
        PermissionFactory(name="test_permission_2")
        user = UserFactory()
        auth_token = generate_token(user, [Permissions.MANAGE_PERMISSIONS])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.list_permissions"),
        )

        # then
        assert response.status_code == 200
        permissions = response.json["permissions"]
        assert set(perm["name"] for perm in permissions) == {
            *[p.name for p in Permissions],
            "test_permission_1",
            "test_permission_2",
        }

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_list_permissions_without_permission(self, client):
        # given
        PermissionFactory(name="test_permission_1")
        PermissionFactory(name="test_permission_2")
        user = UserFactory()
        auth_token = generate_token(user, [])

        # when
        response = client.get(
            url_for("backoffice_blueprint.list_permissions"),
            headers={"Authorization": auth_token},
        )

        # then
        assert response.status_code == 403

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_list_permissions_as_anonymous(self, client):
        # given
        auth_token = generate_token(UserFactory.build(), [Permissions.MANAGE_PERMISSIONS])

        # when
        response = client.get(
            url_for("backoffice_blueprint.list_permissions"),
            headers={"Authorization": auth_token},
        )

        # then
        assert response.status_code == 403


class NewRoleTest:
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_create_new_role_with_non_empty_permissions(self, client):
        # given
        user = UserFactory()
        permissions = (PermissionFactory(), PermissionFactory())
        new_role_data = {"name": "dummy_role", "permissionIds": [p.id for p in permissions]}
        auth_token = generate_token(user, [Permissions.MANAGE_PERMISSIONS])

        # when
        response = client.with_explicit_token(auth_token).post(
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
    def test_can_create_new_role_with_empty_permissions(self, client):
        # given
        user = UserFactory()
        new_role_data = {"name": "dummy_role", "permissionIds": []}
        auth_token = generate_token(user, [Permissions.MANAGE_PERMISSIONS])

        # when
        response = client.with_explicit_token(auth_token).post(
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
    def test_cannot_create_new_role_with_empty_name(self, client):
        # given
        user = UserFactory()
        new_role_data = {"name": "", "permissionIds": []}
        auth_token = generate_token(user, [Permissions.MANAGE_PERMISSIONS])

        # when
        response = client.with_explicit_token(auth_token).post(
            url_for("backoffice_blueprint.create_role"),
            json=new_role_data,
        )

        # then
        assert response.status_code == 400

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_create_new_role_without_permission(self, client):
        # given
        user = UserFactory()
        auth_token = generate_token(user, [])

        # when
        response = client.post(
            url_for("backoffice_blueprint.create_role"),
            json={"name": "should not work", "permissionsIds": []},
            headers={"Authorization": auth_token},
        )

        # then
        assert response.status_code == 403

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_create_new_role_as_anonymous(self, client):
        # given
        auth_token = generate_token(UserFactory.build(), [Permissions.MANAGE_PERMISSIONS])

        # when
        response = client.post(
            url_for("backoffice_blueprint.create_role"),
            json={"name": "should not work", "permissionsIds": []},
            headers={"Authorization": auth_token},
        )

        # then
        assert response.status_code == 403


class UpdateRoleTest:
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_update_role_with_non_empty_permissions(self, client):
        # given
        user = UserFactory()
        permissions = (PermissionFactory(), PermissionFactory())
        existing_role = RoleFactory(name="dummy_role", permissions=[permissions[0]])
        new_role_data = {"name": "updated_role", "permissionIds": [p.id for p in permissions]}
        auth_token = generate_token(user, [Permissions.MANAGE_PERMISSIONS])

        # when
        response = client.with_explicit_token(auth_token).put(
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
    def test_can_update_role_with_empty_permissions(self, client):
        # given
        user = UserFactory()
        existing_role = RoleFactory(name="dummy_role", permissions=[PermissionFactory()])
        new_role_data = {"name": "updated_role", "permissionIds": []}
        auth_token = generate_token(user, [Permissions.MANAGE_PERMISSIONS])

        # when
        response = client.with_explicit_token(auth_token).put(
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
    def test_cannot_update_role_with_empty_name(self, client):
        # given
        user = UserFactory()
        existing_role = RoleFactory(name="dummy_role", permissions=[PermissionFactory()])
        new_role_data = {"name": "", "permissionIds": []}
        auth_token = generate_token(user, [Permissions.MANAGE_PERMISSIONS])

        # when
        response = client.with_explicit_token(auth_token).put(
            url_for("backoffice_blueprint.update_role", id_=existing_role.id),
            json=new_role_data,
        )

        # then
        assert response.status_code == 400

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_update_role_without_permission(self, client):
        # given
        existing_role = RoleFactory(name="dummy_role", permissions=[PermissionFactory()])
        user = UserFactory()
        auth_token = generate_token(user, [])

        # when
        response = client.put(
            url_for("backoffice_blueprint.update_role", id_=existing_role.id),
            json={"name": "should not work", "permissionsIds": []},
            headers={"Authorization": auth_token},
        )

        # then
        assert response.status_code == 403

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_update_role_as_anonymous(self, client):
        # given
        existing_role = RoleFactory(name="dummy_role", permissions=[PermissionFactory()])
        auth_token = generate_token(UserFactory.build(), [Permissions.MANAGE_PERMISSIONS])

        # when
        response = client.put(
            url_for("backoffice_blueprint.update_role", id_=existing_role.id),
            json={"name": "should not work", "permissionsIds": []},
            headers={"Authorization": auth_token},
        )

        # then
        assert response.status_code == 403


class DeleteRoleTest:
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_delete_role_with_non_empty_permissions(self, client):
        # given
        permissions = (PermissionFactory(), PermissionFactory())
        role = RoleFactory(name="dummy_role", permissions=[permissions[0]])
        user = UserFactory()
        auth_token = generate_token(user, [Permissions.MANAGE_PERMISSIONS])

        # when
        response = client.with_explicit_token(auth_token).delete(
            url_for("backoffice_blueprint.delete_role", id_=role.id),
        )

        # then
        assert response.status_code == 204
        assert Role.query.filter_by(id=role.id).count() == 0

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_delete_role_with_empty_permissions(self, client):
        # given
        role = RoleFactory(name="dummy_role")
        user = UserFactory()
        auth_token = generate_token(user, [Permissions.MANAGE_PERMISSIONS])

        # when
        response = client.with_explicit_token(auth_token).delete(
            url_for("backoffice_blueprint.delete_role", id_=role.id),
        )

        # then
        assert response.status_code == 204
        assert Role.query.filter_by(id=role.id).count() == 0

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_delete_admin_role(self, client):
        # given
        admin_role = create_admin_role()
        user = UserFactory()
        auth_token = generate_token(user, [Permissions.MANAGE_PERMISSIONS])

        # when
        response = client.with_explicit_token(auth_token).delete(
            url_for("backoffice_blueprint.delete_role", id_=admin_role.id),
        )

        # then
        assert response.status_code == 400
        assert "Cannot delete admin role" in response.json.values()

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_delete_role_without_permission(self, client):
        # given
        create_admin_role()
        role = RoleFactory(name="dummy_role")
        user = UserFactory()
        auth_token = generate_token(user, [])

        # when
        response = client.delete(
            url_for("backoffice_blueprint.delete_role", id_=role.id),
            headers={"Authorization": auth_token},
        )

        # then
        assert response.status_code == 403

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_delete_role_as_anonymous(self, client):
        # given
        role = RoleFactory(name="dummy_role")
        auth_token = generate_token(UserFactory.build(), [Permissions.MANAGE_PERMISSIONS])

        # when
        response = client.delete(
            url_for("backoffice_blueprint.delete_role", id_=role.id),
            headers={"Authorization": auth_token},
        )

        # then
        assert response.status_code == 403

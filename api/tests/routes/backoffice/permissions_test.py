from flask import url_for
import pytest

from pcapi.core.auth.api import generate_token
from pcapi.core.permissions import factories as perm_factories
from pcapi.core.permissions import models as perm_models
from pcapi.core.testing import override_features
from pcapi.core.users.factories import UserFactory
from pcapi.repository import repository
from pcapi.routes.backoffice import serialization


pytestmark = pytest.mark.usefixtures("db_session")


def create_admin_role():
    permission = perm_models.Permission.query.filter_by(name=perm_models.Permissions.MANAGE_PERMISSIONS.name).first()
    role = perm_factories.RoleFactory(name="admin")
    role.permissions.append(permission)
    repository.save(role)

    return role


class RoleListTest:
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_list_roles(self, client):
        # given
        perm_factories.RoleFactory(name="test_role_1")
        perm_factories.RoleFactory(name="test_role_2")
        user = UserFactory()
        auth_token = generate_token(user, [perm_models.Permissions.MANAGE_PERMISSIONS])

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
        perm_factories.RoleFactory(name="test_role_1")
        perm_factories.RoleFactory(name="test_role_2")
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
        auth_token = generate_token(UserFactory.build(), [perm_models.Permissions.MANAGE_PERMISSIONS])

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
        user = UserFactory()
        auth_token = generate_token(user, [perm_models.Permissions.MANAGE_PERMISSIONS])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.list_permissions"),
        )

        # then
        assert response.status_code == 200
        permissions = response.json["permissions"]
        assert set(perm["name"] for perm in permissions) == {p.value for p in perm_models.Permissions}

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_list_permissions_without_permission(self, client):
        # given
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
        auth_token = generate_token(UserFactory.build(), [perm_models.Permissions.MANAGE_PERMISSIONS])

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
        permissions = (perm_factories.PermissionFactory(), perm_factories.PermissionFactory())
        new_role_data = {"name": "dummy_role", "permissionIds": [p.id for p in permissions]}
        auth_token = generate_token(user, [perm_models.Permissions.MANAGE_PERMISSIONS])

        # when
        response = client.with_explicit_token(auth_token).post(
            url_for("backoffice_blueprint.create_role"),
            json=new_role_data,
        )

        # then
        assert response.status_code == 200
        assert response.json["name"] == new_role_data["name"]
        assert {p["id"] for p in response.json["permissions"]} == set(new_role_data["permissionIds"])
        new_role_query = perm_models.Role.query.filter_by(name=new_role_data["name"])
        assert new_role_query.count() == 1
        inserted_role = new_role_query[0]
        assert inserted_role.name == new_role_data["name"]
        assert set(inserted_role.permissions) == set(permissions)

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_create_new_role_with_empty_permissions(self, client):
        # given
        user = UserFactory()
        new_role_data = {"name": "dummy_role", "permissionIds": []}
        auth_token = generate_token(user, [perm_models.Permissions.MANAGE_PERMISSIONS])

        # when
        response = client.with_explicit_token(auth_token).post(
            url_for("backoffice_blueprint.create_role"),
            json=new_role_data,
        )

        # then
        assert response.status_code == 200
        assert response.json["name"] == new_role_data["name"]
        assert response.json["permissions"] == []
        new_role_query = perm_models.Role.query.filter_by(name=new_role_data["name"])
        assert new_role_query.count() == 1
        inserted_role = new_role_query[0]
        assert inserted_role.name == new_role_data["name"]
        assert inserted_role.permissions == []

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_create_new_role_with_empty_name(self, client):
        # given
        user = UserFactory()
        new_role_data = {"name": "", "permissionIds": []}
        auth_token = generate_token(user, [perm_models.Permissions.MANAGE_PERMISSIONS])

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
        response = client.with_explicit_token(auth_token).post(
            url_for("backoffice_blueprint.create_role"),
            json={"name": "should not work", "permissionIds": []},
        )

        # then
        assert response.status_code == 403

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_create_new_role_as_anonymous(self, client):
        # when
        response = client.post(
            url_for("backoffice_blueprint.create_role"),
            json={"name": "should not work", "permissionIds": []},
        )

        # then
        assert response.status_code == 403


class UpdateRoleTest:
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_update_role_with_non_empty_permissions(self, client):
        # given
        user = UserFactory()
        permissions = (perm_factories.PermissionFactory(), perm_factories.PermissionFactory())
        existing_role = perm_factories.RoleFactory(name="dummy_role", permissions=[permissions[0]])
        new_role_data = {"name": "updated_role", "permissionIds": [p.id for p in permissions]}
        auth_token = generate_token(user, [perm_models.Permissions.MANAGE_PERMISSIONS])

        # when
        response = client.with_explicit_token(auth_token).put(
            url_for("backoffice_blueprint.update_role", id_=existing_role.id),
            json=new_role_data,
        )

        # then
        assert response.status_code == 200
        assert response.json["name"] == new_role_data["name"]
        assert {p["id"] for p in response.json["permissions"]} == set(new_role_data["permissionIds"])
        new_role_query = perm_models.Role.query.filter_by(name=new_role_data["name"])
        assert new_role_query.count() == 1
        inserted_role = new_role_query[0]
        assert inserted_role.name == new_role_data["name"]
        assert set(inserted_role.permissions) == set(permissions)

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_update_role_with_empty_permissions(self, client):
        # given
        user = UserFactory()
        existing_role = perm_factories.RoleFactory(name="dummy_role", permissions=[perm_factories.PermissionFactory()])
        new_role_data = {"name": "updated_role", "permissionIds": []}
        auth_token = generate_token(user, [perm_models.Permissions.MANAGE_PERMISSIONS])

        # when
        response = client.with_explicit_token(auth_token).put(
            url_for("backoffice_blueprint.update_role", id_=existing_role.id),
            json=new_role_data,
        )

        # then
        assert response.status_code == 200
        assert response.json["name"] == new_role_data["name"]
        assert response.json["permissions"] == []
        new_role_query = perm_models.Role.query.filter_by(name=new_role_data["name"])
        assert new_role_query.count() == 1
        inserted_role = new_role_query[0]
        assert inserted_role.name == new_role_data["name"]
        assert inserted_role.permissions == []

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_update_role_with_empty_name(self, client):
        # given
        user = UserFactory()
        existing_role = perm_factories.RoleFactory(name="dummy_role", permissions=[perm_factories.PermissionFactory()])
        new_role_data = {"name": "", "permissionIds": []}
        auth_token = generate_token(user, [perm_models.Permissions.MANAGE_PERMISSIONS])

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
        existing_role = perm_factories.RoleFactory(name="dummy_role", permissions=[perm_factories.PermissionFactory()])
        user = UserFactory()
        auth_token = generate_token(user, [])

        # when
        response = client.with_explicit_token(auth_token).put(
            url_for("backoffice_blueprint.update_role", id_=existing_role.id),
            json={"name": "should not work", "permissionIds": []},
        )

        # then
        assert response.status_code == 403

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_update_role_as_anonymous(self, client):
        # given
        existing_role = perm_factories.RoleFactory(name="dummy_role", permissions=[perm_factories.PermissionFactory()])

        # when
        response = client.put(
            url_for("backoffice_blueprint.update_role", id_=existing_role.id),
            json={"name": "should not work", "permissionIds": []},
        )

        # then
        assert response.status_code == 403


class DeleteRoleTest:
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_delete_role_with_non_empty_permissions(self, client):
        # given
        permissions = (perm_factories.PermissionFactory(), perm_factories.PermissionFactory())
        role = perm_factories.RoleFactory(name="dummy_role", permissions=[permissions[0]])
        user = UserFactory()
        auth_token = generate_token(user, [perm_models.Permissions.MANAGE_PERMISSIONS])
        role_id, role_name, role_permissions = role.id, role.name, role.permissions

        # when
        response = client.with_explicit_token(auth_token).delete(
            url_for("backoffice_blueprint.delete_role", id_=role.id),
        )

        # then
        assert response.status_code == 200
        assert perm_models.Role.query.filter_by(id=role_id).count() == 0
        deleted_role = response.json
        assert deleted_role["id"] == role_id
        assert deleted_role["name"] == role_name
        assert deleted_role["permissions"] == [serialization.Permission.from_orm(p) for p in role_permissions]

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_delete_role_with_empty_permissions(self, client):
        # given
        role = perm_factories.RoleFactory(name="dummy_role")
        user = UserFactory()
        auth_token = generate_token(user, [perm_models.Permissions.MANAGE_PERMISSIONS])
        role_id, role_name, role_permissions = role.id, role.name, role.permissions

        # when
        response = client.with_explicit_token(auth_token).delete(
            url_for("backoffice_blueprint.delete_role", id_=role.id),
        )

        # then
        assert response.status_code == 200
        assert perm_models.Role.query.filter_by(id=role_id).count() == 0
        deleted_role = response.json
        assert deleted_role["id"] == role_id
        assert deleted_role["name"] == role_name
        assert deleted_role["permissions"] == [serialization.Permission.from_orm(p) for p in role_permissions]

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_delete_admin_role(self, client):
        # given
        admin_role = create_admin_role()
        user = UserFactory()
        auth_token = generate_token(user, [perm_models.Permissions.MANAGE_PERMISSIONS])

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
        role = perm_factories.RoleFactory(name="dummy_role")
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
        role = perm_factories.RoleFactory(name="dummy_role")
        auth_token = generate_token(UserFactory.build(), [perm_models.Permissions.MANAGE_PERMISSIONS])

        # when
        response = client.delete(
            url_for("backoffice_blueprint.delete_role", id_=role.id),
            headers={"Authorization": auth_token},
        )

        # then
        assert response.status_code == 403

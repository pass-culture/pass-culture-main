from flask import url_for
import pytest

from pcapi.core.permissions import factories as perm_factories
from pcapi.core.permissions import models as perm_models
from pcapi.models import db
from pcapi.models import feature as feature_models

from .helpers import html_parser
from .helpers.get import GetEndpointHelper
from .helpers.post import PostEndpointHelper


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice_v3,
]


class GetRolesTest(GetEndpointHelper):
    endpoint = "backoffice_v3_web.get_roles"
    needed_permission = perm_models.Permissions.MANAGE_PERMISSIONS

    def test_can_list_roles_and_permissions(self, authenticated_client):
        # given
        perm_factories.RoleFactory(name="test_role_1")
        perm_factories.RoleFactory(name="test_role_2")

        # when
        response = authenticated_client.get(url_for(self.endpoint))

        # then
        assert response.status_code == 200

        roles = html_parser.extract(response.data, class_="card-header")
        assert "test_role_1" in roles
        assert "test_role_2" in roles

        switches = html_parser.extract(response.data, class_="form-switch")
        assert set(switches) == {p.value for p in perm_models.Permissions}

    def test_can_list_roles_ignoring_obsolete_permissions(self, authenticated_client):
        # given
        obsolete_perm = perm_factories.PermissionFactory(name="OBSOLETE")
        perm_factories.RoleFactory(name="test_role_1", permissions=[obsolete_perm])
        perm_factories.RoleFactory(name="test_role_2")

        # when
        response = authenticated_client.get(url_for(self.endpoint))

        # then
        assert response.status_code == 200

        roles = html_parser.extract(response.data, class_="card-header")
        assert "test_role_1" in roles
        assert "test_role_2" in roles


class UpdateRoleTest(PostEndpointHelper):
    endpoint = "backoffice_v3_web.update_role"
    endpoint_kwargs = {"role_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_PERMISSIONS

    def test_update_role(self, authenticated_client):
        perms = perm_factories.PermissionFactory.create_batch(4)
        old_perms = [perms[0], perms[1]]
        role_to_edit = perm_factories.RoleFactory(permissions=old_perms)
        role_not_to_edit = perm_factories.RoleFactory(permissions=old_perms)

        new_perms = [perms[1], perms[3]]
        base_form = {}
        for perm in perms:
            base_form[perm.name] = perm in new_perms

        response = self.post_to_endpoint(authenticated_client, role_id=role_to_edit.id, form=base_form)
        assert response.status_code == 303

        expected_url = url_for("backoffice_v3_web.get_roles", _external=True)
        assert response.location == expected_url

        role_to_edit = perm_models.Role.query.get(role_to_edit.id)
        assert role_to_edit.permissions == new_perms

        role_not_to_edit = perm_models.Role.query.get(role_not_to_edit.id)
        assert role_not_to_edit.permissions == old_perms

    def test_update_role_with_empty_permissions(self, authenticated_client):
        role = perm_factories.RoleFactory(name="dummy_role", permissions=[perm_factories.PermissionFactory()])

        response = self.post_to_endpoint(
            authenticated_client,
            role_id=role.id,
            form={perm.name: False for perm in perm_models.Permission.query.all()},
        )
        assert response.status_code == 303

        db.session.refresh(role)
        assert role.permissions == []


class ListFeatureFlagsTest(GetEndpointHelper):
    endpoint = "backoffice_v3_web.list_feature_flags"
    needed_permission = perm_models.Permissions.FEATURE_FLIPPING

    def test_list_feature_flags(self, authenticated_client):
        first_feature_flag = feature_models.Feature.query.order_by(feature_models.Feature.name).first()
        first_feature_flag.isActive = True

        response = authenticated_client.get(url_for(self.endpoint))

        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert "Vous allez désactiver" in rows[0]["Activé"]  # "Vous allez désactiver" is inside the modal
        assert rows[0]["Nom"] == first_feature_flag.name
        assert rows[0]["Description"] == first_feature_flag.description

        first_feature_flag.isActive = False

        response = authenticated_client.get(url_for(self.endpoint))

        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert "Vous allez activer" in rows[0]["Activé"]  # "Vous allez activer" is inside the modal
        assert rows[0]["Nom"] == first_feature_flag.name
        assert rows[0]["Description"] == first_feature_flag.description


class EnableFeatureFlagTest(PostEndpointHelper):
    endpoint = "backoffice_v3_web.enable_feature_flag"
    endpoint_kwargs = {"feature_flag_id": 1}
    needed_permission = perm_models.Permissions.FEATURE_FLIPPING

    def test_enable_feature_flag(self, authenticated_client):
        first_feature_flag = feature_models.Feature.query.order_by(feature_models.Feature.name).first()
        first_feature_flag.isActive = False

        response = self.post_to_endpoint(authenticated_client, feature_flag_id=first_feature_flag.id)
        assert response.status_code == 303

        assert first_feature_flag.isActive == True
        response = authenticated_client.get(response.location)
        assert f"Le feature flag {first_feature_flag.name} a été activé" in response.data.decode("utf-8")

    def test_enable_already_active_feature_flag(self, authenticated_client):
        first_feature_flag = feature_models.Feature.query.order_by(feature_models.Feature.name).first()
        first_feature_flag.isActive = True

        response = self.post_to_endpoint(authenticated_client, feature_flag_id=first_feature_flag.id)
        assert response.status_code == 303
        response = authenticated_client.get(response.location)
        assert f"Le feature flag {first_feature_flag.name} est déjà activé" in response.data.decode("utf-8")


class DisableFeatureFlagTest(PostEndpointHelper):
    endpoint = "backoffice_v3_web.disable_feature_flag"
    endpoint_kwargs = {"feature_flag_id": 1}
    needed_permission = perm_models.Permissions.FEATURE_FLIPPING

    def test_disable_feature_flag(self, authenticated_client):
        first_feature_flag = feature_models.Feature.query.order_by(feature_models.Feature.name).first()
        first_feature_flag.isActive = True

        response = self.post_to_endpoint(authenticated_client, feature_flag_id=first_feature_flag.id)
        assert response.status_code == 303

        assert first_feature_flag.isActive == False
        response = authenticated_client.get(response.location)
        assert f"Le feature flag {first_feature_flag.name} a été désactivé" in response.data.decode("utf-8")

    def test_disable_already_inactive_feature_flag(self, authenticated_client):
        first_feature_flag = feature_models.Feature.query.order_by(feature_models.Feature.name).first()
        first_feature_flag.isActive = False

        response = self.post_to_endpoint(authenticated_client, feature_flag_id=first_feature_flag.id)
        assert response.status_code == 303
        response = authenticated_client.get(response.location)
        assert f"Le feature flag {first_feature_flag.name} est déjà désactivé" in response.data.decode("utf-8")

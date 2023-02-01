from flask import g
from flask import url_for
import pytest

from pcapi.core.permissions import factories as perm_factories
from pcapi.core.permissions import models as perm_models
from pcapi.models import db

from .helpers import html_parser
from .helpers import unauthorized as unauthorized_helpers


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice_v3,
]


class GetRolesTest:
    endpoint = "backoffice_v3_web.get_roles"

    class UnauthorizedTest(unauthorized_helpers.UnauthorizedHelper):
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


class UpdateRoleTest:
    class UnauthorizedTest(unauthorized_helpers.MissingCSRFHelper):
        endpoint = "backoffice_v3_web.update_role"
        endpoint_kwargs = {"role_id": 1}
        method = "post"

    def test_update_role(self, authenticated_client):
        perms = perm_factories.PermissionFactory.create_batch(4)
        old_perms = [perms[0], perms[1]]
        role_to_edit = perm_factories.RoleFactory(permissions=old_perms)
        role_not_to_edit = perm_factories.RoleFactory(permissions=old_perms)

        new_perms = [perms[1], perms[3]]
        base_form = {}
        for perm in perms:
            base_form[perm.name] = perm in new_perms

        response = self.update_role(authenticated_client, role_to_edit, base_form)
        assert response.status_code == 303

        expected_url = url_for("backoffice_v3_web.get_roles", _external=True)
        assert response.location == expected_url

        role_to_edit = perm_models.Role.query.get(role_to_edit.id)
        assert role_to_edit.permissions == new_perms

        role_not_to_edit = perm_models.Role.query.get(role_not_to_edit.id)
        assert role_not_to_edit.permissions == old_perms

    def test_update_role_with_empty_permissions(self, authenticated_client):
        role = perm_factories.RoleFactory(name="dummy_role", permissions=[perm_factories.PermissionFactory()])

        response = self.update_role(
            authenticated_client, role, {perm.name: False for perm in perm_models.Permission.query.all()}
        )
        assert response.status_code == 303

        db.session.refresh(role)
        assert role.permissions == []

    def update_role(self, authenticated_client, role_to_edit, form):
        # generate csrf token
        edit_url = url_for("backoffice_v3_web.get_roles")
        authenticated_client.get(edit_url)

        url = url_for("backoffice_v3_web.update_role", role_id=role_to_edit.id)

        form["csrf_token"] = g.get("csrf_token", "")
        return authenticated_client.post(url, form=form)

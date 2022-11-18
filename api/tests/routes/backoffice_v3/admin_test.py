from flask import g
from flask import url_for
import pytest

from pcapi.core.permissions import factories as permissions_factories
from pcapi.core.permissions import models as perm_models
from pcapi.core.testing import override_features

from .helpers import unauthorized as unauthorized_helpers


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice_v3,
]


class GetRolesAuthorizedTest:
    endpoint = "backoffice_v3_web.get_roles"

    class UnauthorizedTest(unauthorized_helpers.UnauthorizedHelper):
        endpoint = "backoffice_v3_web.get_roles"
        needed_permission = perm_models.Permissions.MANAGE_PERMISSIONS


class UpdateRoleTest:
    class UnauthorizedTest(unauthorized_helpers.MissingCSRFHelper):
        endpoint = "backoffice_v3_web.update_role"
        endpoint_kwargs = {"role_id": 1}
        method = "post"

    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    def test_update_role(self, client, legit_user):
        perms = permissions_factories.PermissionFactory.create_batch(4)
        old_perms = [perms[0], perms[1]]
        role_to_edit = permissions_factories.RoleFactory(permissions=old_perms)
        role_not_to_edit = permissions_factories.RoleFactory(permissions=old_perms)

        new_perms = [perms[1], perms[3]]
        base_form = {}
        for perm in perms:
            base_form[perm.name] = perm in new_perms

        response = self.update_role(client, legit_user, role_to_edit, base_form)
        assert response.status_code == 303

        expected_url = url_for("backoffice_v3_web.get_roles", _external=True)
        assert response.location == expected_url

        role_to_edit = perm_models.Role.query.get(role_to_edit.id)
        assert role_to_edit.permissions == new_perms

        role_not_to_edit = perm_models.Role.query.get(role_not_to_edit.id)
        assert role_not_to_edit.permissions == old_perms

    def update_role(self, client, legit_user, role_to_edit, form):
        # generate csrf token
        edit_url = url_for("backoffice_v3_web.get_roles")
        client.with_bo_session_auth(legit_user).get(edit_url)

        url = url_for("backoffice_v3_web.update_role", role_id=role_to_edit.id)

        form["csrf_token"] = g.get("csrf_token", "")
        return client.with_bo_session_auth(legit_user).post(url, form=form)

from unittest import mock

import pytest

from pcapi.core.auth.api import NotAPassCultureTeamAccountError
from pcapi.core.auth.api import authenticate_with_permissions
from pcapi.core.auth.api import extract_roles_from_google_workspace_groups
from pcapi.core.permissions.factories import PermissionFactory
from pcapi.core.permissions.factories import RoleFactory
from pcapi.core.users.factories import UserFactory
from pcapi.core.users.utils import decode_jwt_token
from pcapi.repository import repository

from .factories import GoogleWorkspaceGroup
from .factories import GoogleWorkspaceGroupList


pytestmark = pytest.mark.usefixtures("db_session")


def test_can_extract_roles_from_google_workspace_groups():
    # given
    backoffice_groups = ["backoffice-admin", "backoffice-public-support", "backoffice-pro-support"]
    other_groups = ["random-group", "dummy-group"]
    api_response_json = GoogleWorkspaceGroupList(
        groups=[GoogleWorkspaceGroup(name=group) for group in backoffice_groups + other_groups]
    )

    # when
    extracted_roles = extract_roles_from_google_workspace_groups(api_response_json)

    # then
    assert sorted(extracted_roles) == ["admin", "pro-support", "public-support"]


def test_get_token_with_permission_from_google_token_id():
    # given
    user = UserFactory(email="pepe@passculture.app")
    role_1 = RoleFactory()
    role_2 = RoleFactory()
    permissions = [PermissionFactory(), PermissionFactory(), PermissionFactory()]
    PermissionFactory()  # this one is not linked to a user role and should not appear in the token
    role_1.permissions.extend(permissions[:-1])
    role_2.permissions.extend(permissions[1:])
    repository.save(role_1, role_2)

    with mock.patch("pcapi.core.auth.api.get_user_from_google_id") as user_from_google_id_mock:
        user_from_google_id_mock.return_value = user
        with mock.patch("pcapi.core.auth.api.get_groups_from_google_workspace") as groups_from_workspace_mock:
            groups_from_workspace_mock.return_value = GoogleWorkspaceGroupList(
                groups=[GoogleWorkspaceGroup(name=f"backoffice-{r.name}") for r in (role_1, role_2)]
            )

            # when
            token = authenticate_with_permissions("random google token id")

    # then
    payload = decode_jwt_token(token)
    assert payload.get("email") == user.email
    assert sorted(payload.get("perms", [])) == sorted(p.name for p in permissions)


def test_non_passculture_accounts_cannot_get_a_token():
    # given
    user = UserFactory(email="pepe@example.com")

    with mock.patch("pcapi.core.auth.api.get_user_from_google_id") as user_from_google_id_mock:
        user_from_google_id_mock.return_value = user

        # then
        with pytest.raises(NotAPassCultureTeamAccountError):

            # when
            authenticate_with_permissions("random google token id")


def test_unknown_accounts_cannot_get_a_token():
    # given
    with mock.patch("pcapi.core.auth.api.get_user_from_google_id") as user_from_google_id_mock:
        user_from_google_id_mock.return_value = None

        # then
        with pytest.raises(NotAPassCultureTeamAccountError):

            # when
            authenticate_with_permissions("random google token id")

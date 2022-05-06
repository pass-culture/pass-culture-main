import enum
from unittest import mock

from flask import current_app

from pcapi.core.permissions.factories import PermissionFactory
from pcapi.core.permissions.factories import RoleFactory
from pcapi.core.permissions.utils import permission_required
from pcapi.core.testing import override_settings
from pcapi.core.users.factories import UserFactory
from pcapi.repository import repository


def test_access_granted_with_right_permission(db_session, client):
    # given
    permission = PermissionFactory()
    role = RoleFactory()
    role.permissions.append(permission)
    repository.save(role)
    user = UserFactory()
    user.groups = [role.name]
    view_func_stub = mock.Mock()
    perm_decorator = permission_required(
        getattr(enum.Enum("TestPerms", {permission.name: permission.name}), permission.name)
    )

    with mock.patch.object(current_app.login_manager, "unauthorized") as unauthorized_mock:
        with mock.patch("flask_login.utils._get_user") as current_user_mock:
            current_user_mock.return_value = user

            # when
            perm_decorator(view_func_stub)("test_arg")

    # then
    assert view_func_stub.call_count == 1
    assert unauthorized_mock.call_count == 0


def test_access_denied_without_right_permission(db_session, client):
    # given
    permission = PermissionFactory()
    role = RoleFactory()
    role.permissions.append(permission)
    repository.save(role)
    user = UserFactory()
    user.groups = [role.name]
    view_func_stub = mock.Mock()
    perm_decorator = permission_required(
        getattr(enum.Enum("TestPerms", {"BAD_PERMISSION": "bad permission"}), "BAD_PERMISSION")
    )

    with mock.patch("pcapi.core.permissions.utils.send_403_permission_needed") as unauthorized_mock:
        with mock.patch("flask_login.utils._get_user") as current_user_mock:
            current_user_mock.return_value = user

            # when
            perm_decorator(view_func_stub)("test_arg")

    # then
    assert view_func_stub.call_count == 0
    assert unauthorized_mock.call_count == 1


def test_access_denied_as_anonymous(db_session, client):
    # given
    permission = PermissionFactory()
    role = RoleFactory()
    role.permissions.append(permission)
    repository.save(role)
    view_func_stub = mock.Mock()
    perm_decorator = permission_required(
        getattr(enum.Enum("TestPerms", {permission.name: permission.name}), permission.name)
    )

    with mock.patch.object(current_app.login_manager, "unauthorized") as unauthorized_mock:

        # when
        perm_decorator(view_func_stub)("test_arg")

    # then
    assert view_func_stub.call_count == 0
    assert unauthorized_mock.call_count == 1


@override_settings(IS_TESTING=True)
def test_no_need_for_permissions_on_testing_environment(db_session, client):
    # given
    permission = PermissionFactory()
    role = RoleFactory()
    role.permissions.append(permission)
    repository.save(role)
    user = UserFactory()
    view_func_stub = mock.Mock()
    perm_decorator = permission_required(
        getattr(enum.Enum("TestPerms", {"BAD_PERMISSION": "bad permission"}), "BAD_PERMISSION")
    )

    with mock.patch("pcapi.core.permissions.utils.send_403_permission_needed") as unauthorized_mock:
        with mock.patch("flask_login.utils._get_user") as current_user_mock:
            user.groups = [role.name]
            current_user_mock.return_value = user

            # when
            perm_decorator(view_func_stub)("test_arg")

    # then
    assert view_func_stub.call_count == 1
    assert unauthorized_mock.call_count == 0

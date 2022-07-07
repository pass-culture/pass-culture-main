import enum
from unittest import mock

from flask import current_app
import pytest

from pcapi.core.auth.api import generate_token
from pcapi.core.permissions.factories import PermissionFactory
from pcapi.core.permissions.utils import permission_required
from pcapi.core.testing import override_features
from pcapi.core.testing import override_settings
from pcapi.core.users.factories import UserFactory
from pcapi.models.api_errors import ApiErrors
from pcapi.repository import repository


@override_features(ENABLE_BACKOFFICE_API=True)
def test_access_granted_with_right_permission(db_session, client):
    # given
    permission = PermissionFactory()
    repository.save(permission)
    user = UserFactory()
    view_func_stub = mock.Mock()
    perm_decorator = permission_required(
        getattr(enum.Enum("TestPerms", {permission.name: permission.name}), permission.name)
    )
    auth_token = generate_token(user, [permission])

    with current_app.test_request_context("http://any.thing", headers={"Authorization": f"Bearer {auth_token}"}):

        # when
        perm_decorator(view_func_stub)("test_arg")

    # then
    assert view_func_stub.call_count == 1


@override_features(ENABLE_BACKOFFICE_API=True)
def test_access_denied_without_right_permission(db_session, client):
    # given
    permission = PermissionFactory()
    repository.save(permission)
    user = UserFactory()
    view_func_stub = mock.Mock()
    perm_decorator = permission_required(
        getattr(enum.Enum("TestPerms", {"BAD_PERMISSION": "bad permission"}), "BAD_PERMISSION")
    )
    auth_token = generate_token(user, [permission])

    with current_app.test_request_context(
        "http://any.thing", headers={"Authorization": f"Bearer {auth_token}"}
    ), pytest.raises(ApiErrors) as exc_info:

        # when
        perm_decorator(view_func_stub)("test_arg")

    # then
    assert view_func_stub.call_count == 0
    assert exc_info.value.errors == {"global": "missing permission"}
    assert exc_info.value.status_code == 403


@override_features(ENABLE_BACKOFFICE_API=True)
def test_access_denied_as_anonymous(db_session, client):
    # given
    permission = PermissionFactory()
    repository.save(permission)
    view_func_stub = mock.Mock()
    perm_decorator = permission_required(
        getattr(enum.Enum("TestPerms", {permission.name: permission.name}), permission.name)
    )

    with current_app.test_request_context("http://any.thing"), pytest.raises(ApiErrors) as exc_info:

        # when
        perm_decorator(view_func_stub)("test_arg")

    # then
    assert view_func_stub.call_count == 0
    assert exc_info.value.errors == {"global": "bad token"}
    assert exc_info.value.status_code == 403


@override_features(ENABLE_BACKOFFICE_API=True)
@override_settings(IS_TESTING=True)
def test_no_need_for_permissions_on_testing_environment(db_session, client):
    # given
    permission = PermissionFactory()
    repository.save(permission)
    user = UserFactory()
    view_func_stub = mock.Mock()
    perm_decorator = permission_required(
        getattr(enum.Enum("TestPerms", {"BAD_PERMISSION": "bad permission"}), "BAD_PERMISSION")
    )
    auth_token = generate_token(user, [permission])

    with current_app.test_request_context("http://any.thing", headers={"Authorization": f"Bearer {auth_token}"}):

        # when
        perm_decorator(view_func_stub)("test_arg")

    # then
    assert view_func_stub.call_count == 1


@override_features(ENABLE_BACKOFFICE_API=False)
def test_access_denied_when_backoffice_api_disabled(db_session, client):
    # given
    permission = PermissionFactory()
    repository.save(permission)
    user = UserFactory()
    view_func_stub = mock.Mock()
    perm_decorator = permission_required(
        getattr(enum.Enum("TestPerms", {permission.name: permission.name}), permission.name)
    )
    auth_token = generate_token(user, [permission])

    with current_app.test_request_context(
        "http://any.thing", headers={"Authorization": f"Bearer {auth_token}"}
    ), pytest.raises(ApiErrors) as exc_info:

        # when
        perm_decorator(view_func_stub)("test_arg")

    # then
    assert view_func_stub.call_count == 0
    assert exc_info.value.errors == {
        "global": "This function is behind the deactivated ENABLE_BACKOFFICE_API feature flag"
    }
    assert exc_info.value.status_code == 403

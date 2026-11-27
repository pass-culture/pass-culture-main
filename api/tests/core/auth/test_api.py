import logging
from unittest import mock

import pytest

from pcapi.connectors.sso import SSOUser
from pcapi.connectors.sso.apple import AppleSSOProvider
from pcapi.core.auth import exceptions as auth_exceptions
from pcapi.core.auth import repository as auth_repository
from pcapi.core.auth.api import attach_sso_to_user
from pcapi.core.auth.api import extract_roles_from_google_workspace_groups
from pcapi.core.auth.api import remove_sso_from_user
from pcapi.core.history import factories as history_factories
from pcapi.core.users import constants as users_constants
from pcapi.core.users import factories as users_factories
from pcapi.core.users.models import SingleSignOn
from pcapi.models import db

from .factories import GoogleWorkspaceGroup
from .factories import GoogleWorkspaceGroupList


pytestmark = pytest.mark.usefixtures("db_session")


@pytest.mark.settings(ENV="staging")
def test_can_extract_roles_from_google_workspace_groups():
    # given
    backoffice_groups = ["backoffice-staging-admin", "backoffice-testing-pro_support"]
    other_groups = ["random-group", "dummy-group"]
    api_response_json = GoogleWorkspaceGroupList(
        groups=[GoogleWorkspaceGroup(name=group) for group in backoffice_groups + other_groups]
    )

    # when
    extracted_roles = extract_roles_from_google_workspace_groups(api_response_json)

    # then
    assert extracted_roles == {"admin"}


class AttachSsoToUserTest:
    sso_user = SSOUser(sub="100428144463745704968", email="jeune@example.com", email_verified=True)

    def test_attaches_sso(self):
        user = users_factories.UserFactory(isEmailValidated=True)

        attach_sso_to_user(user, self.sso_user, "google")

        [sso] = db.session.query(SingleSignOn).filter(SingleSignOn.userId == user.id).all()
        assert sso.ssoProvider == "google"
        assert sso.ssoUserId == self.sso_user.sub

    def test_unsupported_provider(self):
        user = users_factories.UserFactory(isEmailValidated=True)

        with pytest.raises(auth_exceptions.SSOUnsupportedProvider):
            attach_sso_to_user(user, self.sso_user, "facebook")

        assert db.session.query(SingleSignOn).filter(SingleSignOn.userId == user.id).count() == 0

    def test_deleted_account(self):
        # the native route already rejects inactive users: the check must also hold on its own
        user = users_factories.UserFactory(isActive=False, isEmailValidated=True)
        history_factories.SuspendedUserActionHistoryFactory(user=user, reason=users_constants.SuspensionReason.DELETED)

        with pytest.raises(auth_exceptions.SSOAccountNotActive):
            attach_sso_to_user(user, self.sso_user, "google")

        assert db.session.query(SingleSignOn).filter(SingleSignOn.userId == user.id).count() == 0


class RemoveSsoFromUserTest:
    def _get_user_ssos(self, user):
        return db.session.query(SingleSignOn).filter(SingleSignOn.userId == user.id).all()

    def test_removes_sso(self):
        user = users_factories.UserFactory()
        sso = users_factories.SingleSignOnFactory(user=user, ssoProvider="google", ssoUserId="100428144463745704968")
        other_sso = users_factories.SingleSignOnFactory(ssoProvider="google")

        remove_sso_from_user(user, sso.id)

        assert self._get_user_ssos(user) == []
        # the SSO can no longer be used to log in to this account
        assert auth_repository.get_single_sign_on_from_provider("google", "100428144463745704968") is None
        assert db.session.query(SingleSignOn).filter(SingleSignOn.id == other_sso.id).count() == 1

    def test_removes_apple_sso_and_revokes_apple_token(self):
        user = users_factories.UserFactory()
        sso = users_factories.SingleSignOnFactory(
            user=user, ssoProvider="apple", ssoExtraData={"mobile": "apple-refresh-token"}
        )

        with mock.patch.object(AppleSSOProvider, "revoke_access") as mock_revoke:
            remove_sso_from_user(user, sso.id)

        mock_revoke.assert_called_once_with("apple-refresh-token")
        assert self._get_user_ssos(user) == []

    def test_removes_apple_sso_even_if_revocation_fails(self, caplog):
        user = users_factories.UserFactory()
        sso = users_factories.SingleSignOnFactory(
            user=user, ssoProvider="apple", ssoExtraData={"mobile": "apple-refresh-token"}
        )

        with (
            mock.patch.object(AppleSSOProvider, "revoke_access", side_effect=Exception("Apple is down")),
            caplog.at_level(logging.WARNING),
        ):
            remove_sso_from_user(user, sso.id)

        assert caplog.records[0].message == "Could not revoke Apple SSO"
        assert caplog.records[0].extra["user_id"] == user.id
        assert self._get_user_ssos(user) == []

    def test_removes_sso_without_password_when_another_sso_remains(self):
        user = users_factories.UserFactory()
        user.password = None
        apple_sso = users_factories.SingleSignOnFactory(user=user, ssoProvider="apple")
        google_sso = users_factories.SingleSignOnFactory(user=user, ssoProvider="google")

        with mock.patch.object(AppleSSOProvider, "revoke_access"):
            remove_sso_from_user(user, apple_sso.id)

        assert self._get_user_ssos(user) == [google_sso]

    def test_refuses_to_remove_last_sso_without_password(self):
        user = users_factories.UserFactory()
        user.password = None
        sso = users_factories.SingleSignOnFactory(user=user, ssoProvider="google")

        with pytest.raises(auth_exceptions.SSOUnauthorizedRemove):
            remove_sso_from_user(user, sso.id)

        assert self._get_user_ssos(user) == [sso]
        assert user.password is None

    def test_removes_last_sso_once_password_is_created(self):
        user = users_factories.UserFactory()
        user.password = None
        sso = users_factories.SingleSignOnFactory(user=user, ssoProvider="google")
        with pytest.raises(auth_exceptions.SSOUnauthorizedRemove):
            remove_sso_from_user(user, sso.id)

        user.setPassword("user@AZERTY123")
        remove_sso_from_user(user, sso.id)

        assert self._get_user_ssos(user) == []
        assert user.checkPassword("user@AZERTY123")

    def test_unknown_sso(self):
        user = users_factories.UserFactory()

        with pytest.raises(auth_exceptions.SSOUserNotFound):
            remove_sso_from_user(user, 0)

    def test_sso_of_another_account(self):
        user = users_factories.UserFactory()
        other_sso = users_factories.SingleSignOnFactory(ssoProvider="google")

        with pytest.raises(auth_exceptions.SSOAttachedToAnotherAccount):
            remove_sso_from_user(user, other_sso.id)

        assert db.session.query(SingleSignOn).filter(SingleSignOn.id == other_sso.id).count() == 1

    def test_sso_of_another_account_with_same_provider(self):
        user = users_factories.UserFactory()
        sso = users_factories.SingleSignOnFactory(user=user, ssoProvider="google")
        other_sso = users_factories.SingleSignOnFactory(ssoProvider="google")

        with pytest.raises(auth_exceptions.SSOAttachedToAnotherAccount):
            remove_sso_from_user(user, other_sso.id)

        assert self._get_user_ssos(user) == [sso]
        assert db.session.query(SingleSignOn).filter(SingleSignOn.id == other_sso.id).count() == 1

    def test_unsupported_provider(self):
        user = users_factories.UserFactory()
        sso = users_factories.SingleSignOnFactory(user=user, ssoProvider="facebook")

        with pytest.raises(auth_exceptions.SSOUnsupportedProvider):
            remove_sso_from_user(user, sso.id)

        assert self._get_user_ssos(user) == [sso]

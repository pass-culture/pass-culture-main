from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from sqlalchemy import exc as sa_exc

from pcapi.connectors.sso import SSOUser
from pcapi.core.auth import exceptions as auth_exceptions
from pcapi.core.auth.api import attach_sso_to_user
from pcapi.core.auth.api import extract_roles_from_google_workspace_groups
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

    def test_deleted_account(self):
        # the native route already rejects inactive users: the check must also hold on its own
        user = users_factories.UserFactory(isActive=False, isEmailValidated=True)
        history_factories.SuspendedUserActionHistoryFactory(user=user, reason=users_constants.SuspensionReason.DELETED)

        with pytest.raises(auth_exceptions.SSOAccountNotActive):
            attach_sso_to_user(user, self.sso_user, "google")

        assert db.session.query(SingleSignOn).filter(SingleSignOn.userId == user.id).count() == 0

    @pytest.mark.parametrize(
        "constraint_name,expected_exception",
        [
            ("unique_user_per_sso_provider", auth_exceptions.SSOAlreadyAttached),
            ("unique_sso_user_per_sso_provider", auth_exceptions.SSOAttachedToAnotherAccount),
        ],
    )
    def test_unique_constraint_violation_raises_dedicated_exception(self, constraint_name, expected_exception):
        user = users_factories.UserFactory(isEmailValidated=True)
        error = sa_exc.IntegrityError(
            "INSERT INTO single_sign_on ...", {}, MagicMock(diag=MagicMock(constraint_name=constraint_name))
        )

        with patch("pcapi.core.users.repository.create_single_sign_on", side_effect=error):
            with pytest.raises(expected_exception):
                attach_sso_to_user(user, self.sso_user, "google")

    def test_other_integrity_error_is_not_hidden(self):
        user = users_factories.UserFactory(isEmailValidated=True)
        error = sa_exc.IntegrityError(
            "INSERT INTO single_sign_on ...", {}, MagicMock(diag=MagicMock(constraint_name="other"))
        )

        with patch("pcapi.core.users.repository.create_single_sign_on", side_effect=error):
            with pytest.raises(sa_exc.IntegrityError):
                attach_sso_to_user(user, self.sso_user, "google")

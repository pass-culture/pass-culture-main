import pytest

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

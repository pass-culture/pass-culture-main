import pytest

from pcapi.core.auth.api import extract_roles_from_google_workspace_groups

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

import pytest

from pcapi.core.testing import assert_num_queries
import pcapi.core.users.backoffice.api as backoffice_api

from tests.routes.backoffice_v3.conftest import legit_user_fixture  # pylint: disable=unused-import
from tests.routes.backoffice_v3.conftest import roles_with_permissions_fixture  # pylint: disable=unused-import


pytestmark = pytest.mark.usefixtures("db_session")


def test_fetch_user_with_profile(legit_user) -> None:
    user_id = legit_user.id

    with assert_num_queries(1):
        user_with_profile = backoffice_api.fetch_user_with_profile(user_id)
        assert user_with_profile.backoffice_profile.permissions

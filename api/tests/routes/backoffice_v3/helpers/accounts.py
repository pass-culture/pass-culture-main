import pytest

from pcapi.core.testing import override_features
from pcapi.core.users import factories as users_factories

from . import base


pytestmark = pytest.mark.usefixtures("db_session")


class PageRendersHelper(base.BaseHelper):
    @property
    def user(self):
        return users_factories.UserFactory()

    @property
    def endpoint_kwargs(self):
        return {"user_id": self.user.id}

    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    def test_page_renders(self, client, legit_user):
        response = client.with_session_auth(legit_user.email).get(self.path)
        assert response.status_code == 200

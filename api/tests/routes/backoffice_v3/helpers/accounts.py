import pytest

from pcapi.core.users import factories as users_factories

from . import base


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice_v3,
]


class PageRendersHelper(base.BaseHelper):
    @property
    def user(self):
        return users_factories.UserFactory()

    @property
    def endpoint_kwargs(self):
        return {"user_id": self.user.id}

    def test_page_renders(self, client, legit_user):
        response = client.with_bo_session_auth(legit_user).get(self.path)
        assert response.status_code == 200

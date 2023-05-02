from flask import url_for
import pytest

import pcapi.core.users.factories as users_factories

from tests.routes.backoffice_v3.helpers import html_parser


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice_v3,
]


class UserGenerationGetRouteTest:
    endpoint = "backoffice_v3_web.get_generated_user"
    needed_permission = None

    def test_returns_user_data(self, authenticated_client):
        generated_user = users_factories.UserFactory()

        response = authenticated_client.get(url_for(self.endpoint, userId=generated_user.id))

        assert response.status_code == 200
        assert generated_user.email in html_parser.content_as_text(response.data)

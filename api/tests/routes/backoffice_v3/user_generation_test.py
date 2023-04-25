from flask import url_for
import pytest

from pcapi.core.testing import override_settings
from pcapi.core.users.models import User

from tests.routes.backoffice_v3.helpers import html_parser


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice_v3,
]


class UserGenerationRouteTest:
    endpoint = "backoffice_v3_web.generate_user"

    @override_settings(ENABLE_TEST_USER_GENERATION=False)
    def test_returns_not_found_if_generation_disabled(self, authenticated_client):
        response = authenticated_client.get(url_for(self.endpoint))
        assert response.status_code == 404

    def test_returns_user(self, authenticated_client):
        response = authenticated_client.get(url_for(self.endpoint))

        created_user = User.query.order_by(User.id.desc()).first()
        assert response.status_code == 200
        assert created_user.email in html_parser.content_as_text(response.data)

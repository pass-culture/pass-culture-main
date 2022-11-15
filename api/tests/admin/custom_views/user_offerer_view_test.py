from unittest.mock import patch

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offerers.models as offerers_models
import pcapi.core.users.factories as users_factories
import pcapi.core.users.models as users_models

from tests.conftest import clean_database


class UserOffererViewTest:
    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_delete_user_offerer(self, mocked_validate_csrf_token, client):
        users_factories.AdminFactory(email="admin@example.com")

        user_offerer = offerers_factories.UserOffererFactory()

        api_client = client.with_session_auth("admin@example.com")

        response = api_client.post(
            "/pc/back-office/userofferer/delete/",
            form={"id": f"{user_offerer.id},{user_offerer.userId},{user_offerer.offererId}"},
        )

        assert response.status_code == 302
        assert offerers_models.UserOfferer.query.count() == 0
        assert users_models.User.query.count() == 2
        assert offerers_models.Offerer.query.count() == 1

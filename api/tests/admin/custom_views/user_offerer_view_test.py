from unittest.mock import patch

from pcapi.core.offerers.models import Offerer
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.core.users.models import User
from pcapi.models.user_offerer import UserOfferer

from tests.conftest import clean_database


class UserOffererViewTest:
    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_delete_user_offerer(self, mocked_validate_csrf_token, client):
        users_factories.AdminFactory(email="admin@example.com")

        user_offerer = offers_factories.UserOffererFactory()

        api_client = client.with_session_auth("admin@example.com")

        response = api_client.post(
            "/pc/back-office/userofferer/delete/",
            form={"id": f"{user_offerer.id},{user_offerer.userId},{user_offerer.offererId}"},
        )

        assert response.status_code == 302
        assert UserOfferer.query.count() == 0
        assert User.query.count() == 2
        assert Offerer.query.count() == 1

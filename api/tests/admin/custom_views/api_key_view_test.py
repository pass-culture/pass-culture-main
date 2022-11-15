from unittest.mock import patch

import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offerers.models import ApiKey
import pcapi.core.users.factories as users_factories

from tests.conftest import TestClient
from tests.conftest import clean_database


class ApiKeyViewTest:
    @clean_database
    @patch("flask_wtf.csrf.validate_csrf")
    def test_api_key_creation(self, mocked_validate_csrf_token, app):
        users_factories.AdminFactory(email="admin@example.com")
        offerer = offerers_factories.OffererFactory(siren=123456789)

        data = dict(
            offererSiren=offerer.siren,
        )

        client = TestClient(app.test_client()).with_session_auth("admin@example.com")
        response = client.post("/pc/back-office/apikey/new", form=data)

        assert response.status_code == 302

        api_key = ApiKey.query.filter_by(offererId=offerer.id).one()
        assert api_key.prefix is not None
        assert api_key.secret is not None

    @clean_database
    @patch("flask_wtf.csrf.validate_csrf")
    def test_api_key_creation_with_wrong_siren(self, mocked_validate_csrf_token, app):
        users_factories.AdminFactory(email="admin@example.com")

        data = dict(
            offererSiren=123456789,
        )

        client = TestClient(app.test_client()).with_session_auth("admin@example.com")
        response = client.post("/pc/back-office/apikey/new", form=data)

        assert response.status_code == 200

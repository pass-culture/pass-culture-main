import flask
import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.providers.factories as providers_factories
from pcapi.models import api_errors
from pcapi.validation.routes import users_authentifications

from tests.conftest import TestClient


@pytest.mark.usefixtures("db_session")
class ApiKeyRequiredTest:
    def _make_app(self):
        app = flask.Flask(__name__)

        @app.route("/test", methods=["GET"])
        @users_authentifications.api_key_required
        def index():
            return "OK"

        # Simulate `routes.error_handlers.generic_error_handlers.restize_api_errors`...
        # without importing the function, which fails because it
        # expects to have a proper Flask app with a context.
        @app.errorhandler(api_errors.ApiErrors)
        def handle_api_errors(error):
            return "", error.status_code

        return app

    @pytest.mark.parametrize(
        "offerer_is_active,expected_response_status",
        [(True, 200), (False, 403)],
    )
    def test_require_api_key(self, offerer_is_active, expected_response_status):
        app = self._make_app()
        client = TestClient(app.test_client())

        offerers_factories.ApiKeyFactory(offerer__isActive=offerer_is_active)
        headers = {"Authorization": "Bearer development_prefix_clearSecret"}
        response = client.get("/test", headers=headers)

        assert response.status_code == expected_response_status

    @pytest.mark.parametrize(
        "provider_is_active,expected_response_status",
        [(True, 200), (False, 403)],
    )
    def test_require_active_provider(self, provider_is_active, expected_response_status):
        offerer = offerers_factories.OffererFactory(name="Technical provider")
        provider = providers_factories.ProviderFactory(
            name="Technical provider", localClass=None, isActive=provider_is_active, enabledForPro=True
        )
        offerers_factories.ApiKeyFactory(
            offerer=offerer,
            provider=provider,
        )
        providers_factories.OffererProviderFactory(
            offerer=offerer,
            provider=provider,
        )
        app = self._make_app()
        client = TestClient(app.test_client())

        headers = {"Authorization": "Bearer development_prefix_clearSecret"}
        response = client.get("/test", headers=headers)

        assert response.status_code == expected_response_status

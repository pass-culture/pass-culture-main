import uuid

import flask
import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.providers.factories as providers_factories
from pcapi.models import api_errors
from pcapi.validation.routes import users_authentifications

from tests.conftest import TestClient


@pytest.mark.usefixtures("db_session")
class ProviderApiKeyRequiredTest:
    def _setup_api_key(self, provider=None, offerer=None) -> str:
        offerer = offerer or offerers_factories.OffererFactory(name="Technical provider")

        if provider and offerer:
            providers_factories.OffererProviderFactory(offerer=offerer, provider=provider)

        secret = str(uuid.uuid4())
        env = "test"
        prefix_id = str(uuid.uuid1())

        offerers_factories.ApiKeyFactory(
            offerer=offerer, provider=provider, secret=secret, prefix="%s_%s" % (env, prefix_id)
        )
        plain_api_key = "%s_%s_%s" % (env, prefix_id, secret)

        return plain_api_key

    def test_should_raise_401_because_no_api_key_given(self, client):
        response = client.get("/public/providers/v1/provider")

        assert response.status_code == 401
        assert response.json == {"auth": "API key required"}

    def test_should_raise_401_because_invalid_api_key_given(self, client):
        response = client.with_explicit_token("invalid API key").get("/public/providers/v1/provider")

        assert response.status_code == 401
        assert response.json == {"auth": "API key required"}

    def test_should_raise_401_because_deprecated_api_key_given(self, client):
        # deprecated = not linked to a provider
        plain_api_key = self._setup_api_key(provider=None)
        response = client.with_explicit_token(plain_api_key).get("/public/providers/v1/provider")

        assert response.status_code == 401
        assert response.json == {"auth": "Deprecated API key. Please contact provider support to get a new API key"}

    def test_should_raise_403_because_inactive_offerer(self, client):
        provider = providers_factories.PublicApiProviderFactory()
        offerer = offerers_factories.OffererFactory(isActive=False)
        plain_api_key = self._setup_api_key(provider=provider, offerer=offerer)
        response = client.with_explicit_token(plain_api_key).get("/public/providers/v1/provider")

        assert response.status_code == 403
        assert response.json == {"auth": ["Inactive offerer"]}

    def test_should_raise_403_because_inactive_provider(self, client):
        provider = providers_factories.PublicApiProviderFactory(isActive=False)
        offerer = offerers_factories.OffererFactory()
        plain_api_key = self._setup_api_key(provider=provider, offerer=offerer)
        response = client.with_explicit_token(plain_api_key).get("/public/providers/v1/provider")

        assert response.status_code == 403
        assert response.json == {"auth": ["Inactive provider"]}

    def test_should_be_successful(self, client):
        provider = providers_factories.PublicApiProviderFactory()
        offerer = offerers_factories.OffererFactory()
        plain_api_key = self._setup_api_key(provider=provider, offerer=offerer)
        response = client.with_explicit_token(plain_api_key).get("/public/providers/v1/provider")

        assert response.status_code == 200
        assert "Public API Provider" in response.json.get("name")


@pytest.mark.usefixtures("db_session")
class BrevoWebhookTest:
    def _make_app(self):
        app = flask.Flask(__name__)

        @app.route("/test", methods=["GET"])
        @users_authentifications.brevo_webhook
        def index():
            return "OK"

        # Simulate `routes.error_handlers.generic_error_handlers.restize_api_errors`...
        # without importing the function, which fails because it
        # expects to have a proper Flask app with a context.
        @app.errorhandler(api_errors.ApiErrors)
        def handle_api_errors(error):
            return "KO", error.status_code

        return app

    @pytest.mark.settings(BREVO_WEBHOOK_SECRET="valid")
    @pytest.mark.parametrize("secret,expected_response_status", [("valid", 200), ("invalid", 401)])
    def test_require_token(self, secret, expected_response_status):
        app = self._make_app()
        client = TestClient(app.test_client())

        headers = {"Authorization": f"Bearer {secret}"}
        response = client.get("/test", headers=headers)

        assert response.status_code == expected_response_status

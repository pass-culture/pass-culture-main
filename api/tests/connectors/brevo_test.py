import flask
import pytest

from pcapi.connectors.serialization.brevo_serializers import brevo_webhook
from pcapi.models import api_errors

from tests.conftest import TestClient


@pytest.mark.usefixtures("db_session")
class BrevoWebhookTest:
    def _make_app(self):
        app = flask.Flask(__name__)

        @app.route("/test", methods=["GET"])
        @brevo_webhook
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

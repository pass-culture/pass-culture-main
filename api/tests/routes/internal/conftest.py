import pytest

from tests.conftest import TestClient


@pytest.fixture(name="auth_client")
def auth_client_fixture(app, settings):
    settings.E2E_API_KEY = "secret"
    _client = TestClient(app.test_client())
    _client.auth_header = {"x-api-key": settings.E2E_API_KEY}
    return _client

import pytest

from pcapi.core.offerers import factories as offerers_factories


@pytest.fixture(name="client_email", scope="module")
def client_email_fixture():
    return "user@example.com"


@pytest.fixture(name="auth_client")
def auth_client_fixture(client, client_email):
    offerers_factories.UserOffererFactory(user__email=client_email)
    return client.with_session_auth(client_email)

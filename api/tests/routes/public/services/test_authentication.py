import uuid

import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.providers.factories as providers_factories


@pytest.mark.usefixtures("db_session")
class ProviderApiKeyRequiredTest:
    def _setup_api_key(self, provider=None, offerer=None) -> str:
        offerer = offerer or offerers_factories.OffererFactory(name="Technical provider")

        if provider and offerer:
            providers_factories.OffererProviderFactory(offerer=offerer, provider=provider)

        secret = str(uuid.uuid4())
        env = "test"
        prefix_id = str(uuid.uuid1())

        offerers_factories.ApiKeyFactory(provider=provider, secret=secret, prefix="%s_%s" % (env, prefix_id))
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

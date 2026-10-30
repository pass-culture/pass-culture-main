import pytest

from pcapi.connectors.sso import SSOProviderFactory
from pcapi.connectors.sso import SSOProviderName
from pcapi.connectors.sso.apple import AppleSSOProvider
from pcapi.connectors.sso.base import SSOProvider
from pcapi.connectors.sso.google import GoogleSSOProvider
from pcapi.connectors.sso.models import AppleEndpoints


@pytest.mark.settings(
    APPLE_WEB_CLIENT_ID="apple-web-client-id",
    APPLE_MOBILE_CLIENT_ID="apple-mobile-client-id",
    APPLE_TEAM_ID="apple-team-id",
    APPLE_KEY_ID="apple-key-id",
    APPLE_PRIVATE_KEY="apple-private-key",
    APPLE_TOKEN_EXPIRATION="300",
    APPLE_TOKEN_ENDPOINT="https://apple.test/auth/token",
    APPLE_REVOKE_TOKEN_ENDPOINT="https://apple.test/auth/revoke",
    APPLE_KEYS_URL="https://apple.test/auth/keys",
    APPLE_ISSUER_URL="https://apple.test",
)
class CreateAppleProviderTest:
    @pytest.mark.parametrize(
        "is_web,client_type,client_id",
        [(True, "web", "apple-web-client-id"), (False, "mobile", "apple-mobile-client-id")],
    )
    def test_uses_the_client_id_of_the_platform(self, is_web, client_type, client_id):
        provider = SSOProviderFactory.create(SSOProviderName.APPLE, is_web=is_web)

        assert isinstance(provider, AppleSSOProvider)
        assert provider.client_type == client_type
        assert provider.client_id == client_id

    def test_reads_credentials_from_settings(self):
        provider = SSOProviderFactory.create(SSOProviderName.APPLE, is_web=False)

        assert isinstance(provider, AppleSSOProvider)
        assert provider.team_id == "apple-team-id"
        assert provider.key_id == "apple-key-id"
        assert provider.private_key == "apple-private-key"
        assert provider.token_exp == 300

    def test_reads_endpoints_from_settings(self):
        provider = SSOProviderFactory.create(SSOProviderName.APPLE, is_web=False)

        assert isinstance(provider, AppleSSOProvider)
        assert provider.endpoints == AppleEndpoints(
            auth_url="https://apple.test/auth/token",
            revoke_url="https://apple.test/auth/revoke",
            keys_url="https://apple.test/auth/keys",
            issuer_url="https://apple.test",
        )


class CreateGoogleProviderTest:
    @pytest.mark.parametrize(
        "is_web,client_type,redirect_uri",
        [(True, "web", "postmessage"), (False, "mobile", None)],
    )
    def test_uses_the_redirect_uri_of_the_platform(self, is_web, client_type, redirect_uri):
        provider = SSOProviderFactory.create(SSOProviderName.GOOGLE, is_web=is_web)

        assert isinstance(provider, GoogleSSOProvider)
        assert provider.client_type == client_type
        assert provider.redirect_uri == redirect_uri


class CreateTest:
    @pytest.mark.parametrize("provider", list(SSOProviderName))
    def test_every_provider_can_be_created(self, provider):
        assert isinstance(SSOProviderFactory.create(provider, is_web=False), SSOProvider)


class SSOProviderTest:
    def test_cannot_be_instantiated_without_implementation(self):
        with pytest.raises(TypeError):
            SSOProvider(client_type="web")  # type: ignore[abstract]

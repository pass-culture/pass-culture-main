import pytest

from pcapi.connectors.sso import SSOProviderFactory
from pcapi.connectors.sso import SSOProviderName
from pcapi.connectors.sso.apple import AppleSSOProvider
from pcapi.connectors.sso.base import SSOProvider
from pcapi.connectors.sso.exceptions import SSOException
from pcapi.connectors.sso.exceptions import UnsupportedProvider
from pcapi.connectors.sso.google import GoogleSSOProvider


@pytest.mark.settings(
    APPLE_WEB_CLIENT_ID="apple-web-client-id",
    APPLE_MOBILE_CLIENT_ID="apple-mobile-client-id",
    APPLE_TEAM_ID="apple-team-id",
    APPLE_KEY_ID="apple-key-id",
    APPLE_PRIVATE_KEY="apple-private-key",
    APPLE_TOKEN_EXPIRATION="300",
)
class CreateAppleProviderTest:
    @pytest.mark.parametrize(
        "is_web,client_type,client_id",
        [(True, "web", "apple-web-client-id"), (False, "mobile", "apple-mobile-client-id")],
    )
    def test_uses_the_client_id_of_the_platform(self, is_web, client_type, client_id):
        provider = SSOProviderFactory.create("apple", is_web=is_web)

        assert isinstance(provider, AppleSSOProvider)
        assert provider.client_type == client_type
        assert provider.client_id == client_id

    def test_reads_credentials_from_settings(self):
        provider = SSOProviderFactory.create("apple", is_web=False)

        assert isinstance(provider, AppleSSOProvider)
        assert provider.team_id == "apple-team-id"
        assert provider.key_id == "apple-key-id"
        assert provider.private_key == "apple-private-key"
        assert provider.token_exp == 300


class CreateGoogleProviderTest:
    @pytest.mark.parametrize(
        "is_web,client_type,redirect_uri",
        [(True, "web", "postmessage"), (False, "mobile", None)],
    )
    def test_uses_the_redirect_uri_of_the_platform(self, is_web, client_type, redirect_uri):
        provider = SSOProviderFactory.create("google", is_web=is_web)

        assert isinstance(provider, GoogleSSOProvider)
        assert provider.client_type == client_type
        assert provider.redirect_uri == redirect_uri


class CreateTest:
    @pytest.mark.parametrize("name", list(SSOProviderName))
    def test_every_provider_name_can_be_created(self, name):
        assert isinstance(SSOProviderFactory.create(name, is_web=False), SSOProvider)

    @pytest.mark.parametrize("name", ["Google", "GOOGLE", " google "])
    def test_provider_name_is_case_insensitive_and_stripped(self, name):
        assert isinstance(SSOProviderFactory.create(name, is_web=False), GoogleSSOProvider)

    @pytest.mark.parametrize("name", ["unknown_sso", "", "__all__"])
    def test_raises_on_unknown_provider(self, name):
        with pytest.raises(UnsupportedProvider) as exc_info:
            SSOProviderFactory.create(name, is_web=False)

        assert str(exc_info.value) == name

    def test_unsupported_provider_is_an_sso_exception(self):
        assert issubclass(UnsupportedProvider, SSOException)


class SSOProviderTest:
    def test_cannot_be_instantiated_without_implementation(self):
        with pytest.raises(TypeError):
            SSOProvider(client_type="web")  # type: ignore[abstract]

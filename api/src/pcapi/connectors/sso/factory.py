import typing

from pcapi import settings
from pcapi.connectors.sso.apple import AppleSSOProvider
from pcapi.connectors.sso.base import SSOProvider
from pcapi.connectors.sso.exceptions import UnsupportedProvider
from pcapi.connectors.sso.google import GoogleSSOProvider
from pcapi.connectors.sso.models import SSOProviderName


class SSOProviderFactory:
    """
    Factory that generates ready-to-use SSOProvider instances

    It is the only place reading the providers configuration from `pcapi.settings`.

    Supported providers: see `SSOProviderName`.

    >>> SSOProviderFactory.create("apple", is_web=True)
    <AppleSSOProvider type="web">
    >>> SSOProviderFactory.create("google", is_web=False)
    <GoogleSSOProvider type="mobile">
    >>>
    """

    @classmethod
    def create(cls, provider: str, is_web: bool) -> SSOProvider:
        """Build the provider configured for the given client platform.

        :param provider: provider name, case-insensitive (e.g. the `sso_provider` URL parameter).
        :param is_web: whether the login comes from the web app (`platform: web` header) or the mobile apps.
        :raise UnsupportedProvider: if the provider is unknown.
        """
        try:
            provider_name = SSOProviderName(provider.lower().strip())
        except ValueError as e:
            raise UnsupportedProvider(provider) from e

        match provider_name:
            case SSOProviderName.APPLE:
                return cls.__create_apple_provider(is_web)
            case SSOProviderName.GOOGLE:
                return cls.__create_google_provider(is_web)
            case _:
                # mypy fails here if a name of SSOProviderName is not handled above
                typing.assert_never(provider_name)

    @classmethod
    def __create_apple_provider(self, is_web: bool) -> AppleSSOProvider:
        """Apple uses a different client id for the web (Services ID) and the mobile apps (App ID)."""
        return AppleSSOProvider(
            client_id=settings.APPLE_WEB_CLIENT_ID if is_web else settings.APPLE_MOBILE_CLIENT_ID,
            team_id=settings.APPLE_TEAM_ID,
            key_id=settings.APPLE_KEY_ID,
            private_key=settings.APPLE_PRIVATE_KEY,
            token_exp=int(settings.APPLE_TOKEN_EXPIRATION),
            client_type="web" if is_web else "mobile",
        )

    @classmethod
    def __create_google_provider(self, is_web: bool) -> GoogleSSOProvider:
        """The web app gets its code from a popup, which requires the "postmessage" redirect uri.

        https://stackoverflow.com/questions/71968377
        """
        return GoogleSSOProvider(
            redirect_uri="postmessage" if is_web else None,
            client_type="web" if is_web else "mobile",
        )

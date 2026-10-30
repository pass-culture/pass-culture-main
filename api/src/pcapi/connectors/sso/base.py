from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Literal

from pcapi.connectors.sso.models import SSOUser


class SSOProvider(ABC):
    """Interface of an SSO provider.

    An instance is bound to one client platform (`client_type`), because providers may use different credentials
    (client id, redirect uri) for the web and the mobile apps. Build instances with `SSOProviderFactory.create`
    rather than directly, so that the configuration is read from the settings in a single place.
    """

    def __init__(self, *, client_type: Literal["web", "mobile"]):
        """
        :param client_type: platform that initiated the SSO login, deduced from the `platform` request header.
        """
        self.client_type = client_type

    @abstractmethod
    def validate_token(self, authorization_code: str) -> SSOUser:
        """Exchange the authorization code for the identity of the user.

        Implementations must verify the identity token returned by the provider (signature, audience, issuer,
        expiration) before trusting its content.

        :param authorization_code: one-time code obtained by the frontend at the end of the SSO login flow.
        :return: the identity of the user. `email_verified` must be filled: unverified emails are rejected by
            the authentication route.
        :raise SSOException: (subclass) when the code cannot be exchanged or the identity token is invalid.
        """
        raise NotImplementedError

    @abstractmethod
    def revoke_access(self, *args: Any, **kwargs: Any) -> None:
        """Revoke our access to the user account on the provider side.

        Called when a user deletes their account. The arguments depend on the provider (e.g. Apple needs the
        refresh token stored in `SingleSignOn.ssoExtraData`): see the implementations. Providers without a
        revocation API may implement it as a no-op.

        :raise SSOException: (subclass) when the revocation fails.
        """
        raise NotImplementedError

    def __str__(self) -> str:
        return f"<{self.__class__.__name__} type={self.client_type}>"

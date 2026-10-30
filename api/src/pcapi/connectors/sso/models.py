import enum

from pydantic import BaseModel


class SSOProviderName(enum.StrEnum):
    """Names of the supported SSO providers.

    Single source of truth: the authentication route only accepts these names, and `SSOProviderFactory` must be
    able to build each of them. The value is the one used in the authentication URL and stored in
    `SingleSignOn.ssoProvider`: never rename it.
    """

    APPLE = "apple"
    GOOGLE = "google"


class SSOUser(BaseModel):
    """Identity of a user, as returned by any SSO provider.

    Field names follow the OpenID Connect standard claims, so that a standard identity token can be loaded
    directly with `SSOUser.model_validate(id_token)`.

    Attributes:
        sub: unique and stable identifier of the user at the provider. Stored in `SingleSignOn.ssoUserId` and used
            to find the user on the next logins, even if their email changed.
        email: email of the user, if the provider shares it. Required to log in.
        email_verified: whether the provider verified the email. The login is refused when it is not `True`.
        is_private_email: Apple only, the email is a relay address (`...@privaterelay.appleid.com`).
        extra_data: provider-specific data to keep, stored in `SingleSignOn.ssoExtraData`. Apple stores here the
            refresh token needed by `revoke_access`, keyed by client type (`{"web": ..., "mobile": ...}`).
    """

    sub: str
    email: str | None = None
    email_verified: bool | None = None
    is_private_email: bool | None = None
    extra_data: dict | None = None


class AppleSignInAuthenticationResponse(BaseModel):
    """Response of the Apple token endpoint (`POST /auth/token`).

    https://developer.apple.com/documentation/signinwithapplerestapi/tokenresponse
    """

    id_token: str
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str

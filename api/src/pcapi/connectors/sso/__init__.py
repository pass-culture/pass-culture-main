"""Single Sign-On (SSO) connectors.

Turn the authorization code sent by a frontend after an SSO login (native app or web) into an `SSOUser`, a
provider-agnostic identity used by the authentication routes.

Usage::

    from pcapi.connectors.sso import SSOProviderFactory

    provider = SSOProviderFactory.create("apple", is_web=False)
    sso_user = provider.validate_token(authorization_code)

Layout:

- `base.py`: `SSOProvider`, the interface every provider implements
- `models.py`: `SSOProviderName` (the supported providers), `SSOUser` (the common output) and provider-specific
  response models
- `exceptions.py`: errors raised by the providers
- `factory.py`: `SSOProviderFactory`, builds a configured provider from its name and the client platform
- `google.py`, `apple.py`: provider implementations

Adding a new provider (e.g. "acme"):

1. Create `acme.py` with an `AcmeSSOProvider(SSOProvider)` implementing:
   - `validate_token`: exchange the authorization code against the provider token endpoint, verify the identity
     token (signature, audience = our client id, issuer, expiration) and map its claims to an `SSOUser`;
   - `revoke_access`: revoke our access on the provider side (called when a user deletes their account).
2. Declare its errors in `exceptions.py`, as subclasses of `SSOException`, and wrap every network / validation
   error into them: callers must never receive a raw `requests` or `jwt` exception.
3. Add its credentials to `pcapi.settings`. Some providers issue one client id per platform (web / mobile):
   select it from `is_web` in the factory, as for Apple.
4. Add its name to `SSOProviderName` and register it in `SSOProviderFactory`: a `case` in `create` and a private
   `__create_acme_provider` method (mypy fails if a name of the enum is not handled by the factory). The v2
   authentication route accepts the names of this enum, nothing else to do there to allow it.
5. Update the callers:
   - `routes/native/v2/authentication.py::sso_authorize` (`POST /native/v2/oauth/<sso_provider>/authorize`): it
     already turns any `SSOException` into a 401; handle `extra_data` if the provider returns some (see Apple).
     The deprecated v1 route still uses the old `apple_oauth` / `google_oauth` connectors: do not add providers
     there;
   - `core/users/api.py`: add the provider to `SingleSignOnProviders` and handle its revocation in
     `revoke_sso_access`.
   The provider name is the one used in the URL and stored in `SingleSignOn.ssoProvider`: never rename it.
6. Test the provider in `tests/connectors/sso/`, mocking the provider HTTP endpoints (sockets are disabled in
   tests), and the route in `tests/routes/native/v2/authentication_test.py`.
"""

from pcapi.connectors.sso.factory import SSOProviderFactory
from pcapi.connectors.sso.models import SSOProviderName
from pcapi.connectors.sso.models import SSOUser


__all__ = [
    "SSOProviderFactory",
    "SSOProviderName",
    "SSOUser",
]

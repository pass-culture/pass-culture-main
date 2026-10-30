class SSOException(Exception):
    """Base class of the errors raised by the SSO connectors.

    Provider-specific errors must subclass it, so that callers can handle any provider failure at once.
    """


class UnsupportedProvider(SSOException):
    """Raised by `SSOProviderFactory.create` for an unknown provider name."""


class GoogleSignInException(SSOException):
    """Raised by `GoogleSSOProvider.validate_token` when the login cannot be completed.

    Covers OAuth errors (e.g. expired or already used code), network errors and invalid identity tokens.
    """


class AppleSignInException(SSOException):
    """Raised by `AppleSSOProvider.validate_token` when the login cannot be completed.

    Covers network errors, unexpected responses and invalid identity tokens.
    """


class AppleRevokeException(SSOException):
    """Raised by `AppleSSOProvider.revoke_access` when Apple refuses or fails the revocation."""

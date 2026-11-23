class SSOException(Exception):
    """Base class of the errors raised by the SSO connectors.

    Provider-specific errors must subclass it, so that callers can handle any provider failure at once.
    """


class GoogleSignInException(SSOException):
    """Covers OAuth errors (e.g. expired or already used code), network errors and invalid identity tokens."""


class AppleSignInException(SSOException):
    """Covers network errors, unexpected responses and invalid identity tokens."""


class AppleRevokeException(SSOException):
    """Raised when Apple refuses or fails the revocation."""

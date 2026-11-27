from pcapi.core.core_exception import CoreException


class AuthException(CoreException):
    code = "AUTH_EXCEPTION"


class SSOUserNotFound(AuthException):
    code = "SSO_USER_NOT_FOUND"


class SSOUnsupportedProvider(AuthException):
    code = "SSO_UNSUPPORTED_PROVIDER"


class SSOAlreadyAttached(AuthException):
    code = "SSO_ALREADY_ATTACHED"


class SSOAttachedToAnotherAccount(AuthException):
    code = "SSO_ATTACHED_TO_ANOTHER_ACCOUNT"


class SSOUnverifiedEmail(AuthException):
    code = "SSO_UNVERIFIED_EMAIL"


class SSOAccountNotActive(AuthException):
    code = "SSO_ACCOUNT_NOT_ACTIVE"

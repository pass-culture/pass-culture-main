from . import models


class CredentialsException(Exception):
    pass


class InvalidIdentifier(CredentialsException):
    pass


class UnvalidatedAccount(CredentialsException):
    pass


class UserAlreadyExistsException(Exception):
    pass


class UnderAgeUserException(Exception):
    pass


class IncompleteDataException(Exception):
    pass


class EmailNotSent(Exception):
    pass


class UserDoesNotExist(Exception):
    pass


class MissingEmailInMetadataException(Exception):
    pass


class IdentityDocumentVerificationException(Exception):
    pass


class InvalidUserRoleException(Exception):
    pass


class EmailUpdateLimitReached(Exception):
    pass


class EmailUpdateInvalidPassword(Exception):
    pass


class EmailExistsError(Exception):
    pass


class InvalidEmailError(Exception):
    pass


class EmailUpdateTokenExists(Exception):
    pass


class UnsuspensionNotEnabled(Exception):
    pass


class CantAskForUnsuspension(Exception):
    pass


class UnsuspensionTimeLimitExceeded(Exception):
    pass


class NotSuspended(Exception):
    pass


class InvalidToken(Exception):
    pass


class ExpiredToken(InvalidToken):
    user: models.User

    def __init__(self, user: models.User):
        self.user = user
        super().__init__()

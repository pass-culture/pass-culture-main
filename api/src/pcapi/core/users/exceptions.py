from pcapi.core.core_exception import CoreException

from . import models


class UserException(CoreException):
    pass


class CredentialsException(UserException):
    pass


class InvalidIdentifier(CredentialsException):
    pass


class UnvalidatedAccount(CredentialsException):
    pass


class UserAlreadyExistsException(UserException):
    pass


class UnderAgeUserException(UserException):
    pass


class IncompleteDataException(UserException):
    pass


class UserDoesNotExist(UserException):
    pass


class InvalidUserRoleException(UserException):
    pass


class EmailValidationLimitReached(UserException):
    pass


class EmailUpdateLimitReached(UserException):
    pass


class EmailUpdateInvalidPassword(UserException):
    pass


class EmailExistsError(UserException):
    pass


class InvalidEmailError(UserException):
    pass


class EmailUpdateTokenExists(UserException):
    pass


class CantAskForUnsuspension(UserException):
    pass


class UnsuspensionTimeLimitExceeded(UserException):
    pass


class NotSuspended(UserException):
    pass


class InvalidToken(UserException):
    pass


class ExpiredToken(InvalidToken):
    user: models.User | None = None

    def __init__(self, user: models.User | None = None):
        self.user = user
        super().__init__()


class UserGenerationForbiddenException(UserException):
    pass


class MissingLoginMethod(UserException):
    pass


class UserAlreadyHasPendingAnonymization(UserException):
    pass


class DiscordException(UserException):
    pass


class DiscordUserAlreadyLinked(DiscordException):
    pass


class UserNotAllowed(DiscordException):
    pass


class UserNotABeneficiary(DiscordException):
    pass


class UserNotEligible(DiscordException):
    pass


class UnknownDepositType(Exception):
    pass


class InvalidEligibilityTypeException(Exception):
    pass


class UnderageEligibilityWhenAlreadyEighteenException(InvalidEligibilityTypeException):
    pass


class PreDecreeEligibilityWhenPostDecreeBeneficiaryException(InvalidEligibilityTypeException):
    pass

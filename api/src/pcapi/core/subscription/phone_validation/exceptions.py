import typing


class PhoneVerificationException(Exception):
    pass


class PhoneVerificationCodeSendingException(PhoneVerificationException):
    pass


class SMSSendingLimitReached(PhoneVerificationException):
    pass


class PhoneValidationAttemptsLimitReached(PhoneVerificationException):
    def __init__(self, attempts: int):
        self.attempts = attempts
        super().__init__()


class PhoneAlreadyExists(PhoneVerificationException):
    pass


class UnvalidatedEmail(PhoneVerificationException):
    pass


class UserPhoneNumberAlreadyValidated(PhoneVerificationException):
    pass


class UserAlreadyBeneficiary(PhoneVerificationException):
    pass


class NotValidCode(PhoneVerificationException):
    def __init__(self, remaining_attempts: typing.Optional[int] = None):
        self.remaining_attempts = remaining_attempts
        super().__init__()


class ExpiredCode(NotValidCode):
    pass


class InvalidPhoneNumber(PhoneVerificationException):
    pass


class BlacklistedPhoneNumber(InvalidPhoneNumber):
    pass


class InvalidCountryCode(InvalidPhoneNumber):
    pass

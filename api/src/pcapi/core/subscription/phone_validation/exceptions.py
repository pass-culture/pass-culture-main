import typing


class PhoneVerificationException(Exception):
    pass


class UserPhoneNumberAlreadyValidated(PhoneVerificationException):
    pass


class InvalidPhoneNumber(PhoneVerificationException):
    pass


class InvalidCountryCode(InvalidPhoneNumber):
    pass


class SMSSendingLimitReached(PhoneVerificationException):
    pass


class PhoneAlreadyExists(PhoneVerificationException):
    pass


class PhoneValidationAttemptsLimitReached(PhoneVerificationException):
    def __init__(self, attempts: int):
        self.attempts = attempts
        super().__init__()


class NotValidCode(PhoneVerificationException):
    def __init__(self, remaining_attempts: typing.Optional[int] = None):
        self.remaining_attempts = remaining_attempts
        super().__init__()


class ExpiredCode(NotValidCode):
    pass

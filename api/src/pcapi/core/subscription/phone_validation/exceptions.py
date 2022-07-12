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


class UnvalidatedEmail(PhoneVerificationException):
    pass


class UserAlreadyBeneficiary(PhoneVerificationException):
    pass


class NotValidCode(PhoneVerificationException):
    def __init__(self, remaining_attempts: int | None = None):
        self.remaining_attempts = remaining_attempts
        super().__init__()


class ExpiredCode(NotValidCode):
    pass

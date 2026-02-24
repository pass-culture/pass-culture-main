class PhoneVerificationException(Exception):
    pass


class RequiredPhoneNumber(PhoneVerificationException):
    pass


class InvalidPhoneNumber(PhoneVerificationException):
    pass


class InvalidCountryCode(InvalidPhoneNumber):
    pass

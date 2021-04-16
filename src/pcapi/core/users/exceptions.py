class CredentialsException(Exception):
    pass


class InvalidIdentifier(CredentialsException):
    pass


class UnvalidatedAccount(CredentialsException):
    pass


class UserAlreadyExistsException(Exception):
    pass


class NotEligible(Exception):
    pass


class UnderAgeUserException(Exception):
    pass


class EmailNotSent(Exception):
    pass


class PhoneVerificationCodeSendingException(Exception):
    pass


class UnvalidatedEmail(PhoneVerificationCodeSendingException):
    pass


class UserWithoutPhoneNumberException(PhoneVerificationCodeSendingException):
    pass


class UserAlreadyBeneficiary(PhoneVerificationCodeSendingException):
    pass

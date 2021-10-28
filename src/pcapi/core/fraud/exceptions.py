class FraudException(Exception):
    pass


class UserAlreadyBeneficiary(FraudException):
    pass


class UserEmailNotValidated(FraudException):
    pass


class UserPhoneNotValidated(FraudException):
    pass


class UserAgeNotValid(FraudException):
    pass


class DuplicateUser(FraudException):
    pass

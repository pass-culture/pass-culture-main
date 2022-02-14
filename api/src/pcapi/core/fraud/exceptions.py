class FraudException(Exception):
    pass


class UserAlreadyBeneficiary(FraudException):
    pass


class UserAgeNotValid(FraudException):
    pass


class DuplicateUser(FraudException):
    pass


class NotWhitelistedINE(FraudException):
    pass


class InvalidContentTypeException(FraudException):
    pass

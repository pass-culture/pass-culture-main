class FraudException(Exception):
    pass


class UserAlreadyBeneficiary(FraudException):
    pass


class InvalidContentTypeException(FraudException):
    pass

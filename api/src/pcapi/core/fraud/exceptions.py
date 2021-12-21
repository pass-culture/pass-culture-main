class FraudException(Exception):
    pass


class UserAlreadyBeneficiary(FraudException):
    pass


class IncompatibleFraudCheckStatus(FraudException):
    pass

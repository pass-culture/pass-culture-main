class SubscriptionException(Exception):
    pass


class InvalidEligibilityTypeException(SubscriptionException):
    pass


class InvalidAgeException(SubscriptionException):
    def __init__(self, age: int | None) -> None:
        super().__init__()
        self.age = age


class BeneficiaryFraudCheckMissingException(SubscriptionException):
    pass


class CannotUpgradeBeneficiaryRole(SubscriptionException):
    pass

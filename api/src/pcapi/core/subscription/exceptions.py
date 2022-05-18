from typing import Optional


class SubscriptionException(Exception):
    pass


class InvalidEligibilityTypeException(SubscriptionException):
    pass


class InvalidAgeException(SubscriptionException):
    def __init__(self, age: Optional[int]) -> None:
        super().__init__()
        self.age = age


class BeneficiaryFraudCheckMissingException(SubscriptionException):
    pass


class CannotUpgradeBeneficiaryRole(SubscriptionException):
    pass


class DMSParsingError(ValueError):
    def __init__(self, user_email: str, errors: dict[str, Optional[str]], *args, **kwargs):  # type: ignore [no-untyped-def]
        super().__init__(*args, **kwargs)
        self.errors = errors
        self.user_email = user_email

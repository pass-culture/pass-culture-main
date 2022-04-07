class SubscriptionException(Exception):
    pass


class InvalidEligibilityTypeException(SubscriptionException):
    pass


class BeneficiaryFraudCheckMissingException(SubscriptionException):
    pass


class CannotUpgradeBeneficiaryRole(SubscriptionException):
    pass


class DMSParsingError(ValueError):
    def __init__(self, user_email: str, errors: dict[str, str], *args, **kwargs):  # type: ignore [no-untyped-def]
        super().__init__(*args, **kwargs)
        self.errors = errors
        self.user_email = user_email

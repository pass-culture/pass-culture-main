class SubscriptionException(Exception):
    pass


class InvalidEligibilityTypeException(SubscriptionException):
    pass


class BeneficiaryImportMissingException(SubscriptionException):
    pass


class BeneficiaryFraudResultMissing(SubscriptionException):
    pass


class BeneficiaryFraudCheckMissingException(SubscriptionException):
    pass


class BeneficiaryFraudCheckEligibilityTypeMismatchException(SubscriptionException):
    pass


class CannotUpgradeBeneficiaryRole(SubscriptionException):
    pass

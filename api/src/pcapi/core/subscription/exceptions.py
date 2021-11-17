class SubscriptionException(Exception):
    pass


class BeneficiaryImportMissingException(SubscriptionException):
    pass


class BeneficiaryFraudResultMissing(SubscriptionException):
    pass


class CannotUpgradeBeneficiaryRole(SubscriptionException):
    pass

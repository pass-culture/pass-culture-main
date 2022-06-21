from typing import Optional

from pcapi.core.fraud.common.models import IdentityCheckContent
from pcapi.core.subscription.dms import types as dms_types


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
    def __init__(self, user_email: str, errors: list[dms_types.DmsParsingErrorDetails], result_content: IdentityCheckContent, *args, **kwargs):  # type: ignore [no-untyped-def]
        super().__init__(*args, **kwargs)
        self.errors = errors
        self.user_email = user_email
        self.result_content = result_content

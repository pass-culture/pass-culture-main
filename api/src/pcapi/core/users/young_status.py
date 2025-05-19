import dataclasses
import enum
from datetime import datetime

from pcapi.core.subscription import api as subscription_api
from pcapi.core.users import models


class YoungStatusType(enum.Enum):
    ELIGIBLE = "eligible"
    NON_ELIGIBLE = "non_eligible"
    BENEFICIARY = "beneficiary"
    EX_BENEFICIARY = "ex_beneficiary"
    SUSPENDED = "suspended"


class SubscriptionStatus(enum.Enum):
    HAS_TO_COMPLETE_SUBSCRIPTION = "has_to_complete_subscription"
    HAS_SUBSCRIPTION_PENDING = "has_subscription_pending"
    HAS_SUBSCRIPTION_ISSUES = "has_subscription_issues"


@dataclasses.dataclass(frozen=True)
class YoungStatus:
    # All subclasses have a the following attribute:
    #   status_type: YoungStatusType
    # We cannot define it here, otherwise the definition of `Eligible`
    # fails with:
    #     TypeError: non-default argument 'subscription_status' follows default argument
    pass


@dataclasses.dataclass(frozen=True)
class Eligible(YoungStatus):
    subscription_status: SubscriptionStatus
    status_type: YoungStatusType = YoungStatusType.ELIGIBLE


@dataclasses.dataclass(frozen=True)
class NonEligible(YoungStatus):
    status_type: YoungStatusType = YoungStatusType.NON_ELIGIBLE


@dataclasses.dataclass(frozen=True)
class Beneficiary(YoungStatus):
    status_type: YoungStatusType = YoungStatusType.BENEFICIARY


@dataclasses.dataclass(frozen=True)
class ExBeneficiary(YoungStatus):
    status_type: YoungStatusType = YoungStatusType.EX_BENEFICIARY


@dataclasses.dataclass(frozen=True)
class Suspended(YoungStatus):
    status_type: YoungStatusType = YoungStatusType.SUSPENDED


def young_status(user: models.User) -> YoungStatus:
    if not user.isActive:
        return Suspended()

    if user.is_beneficiary:
        if user.deposit_expiration_date and user.deposit_expiration_date < datetime.utcnow():
            return ExBeneficiary()

        return Beneficiary()

    return subscription_api.get_user_subscription_state(user).young_status

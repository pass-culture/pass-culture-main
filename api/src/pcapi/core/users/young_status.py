import dataclasses
from datetime import datetime
import enum

import attrs

from pcapi.core.fraud import models as fraud_models
from pcapi.core.subscription import api as subscription_api
from pcapi.core.subscription import models as subscription_models
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


@attrs.frozen
class YoungStatus:
    status_type: YoungStatusType


@attrs.frozen
class Eligible(YoungStatus):
    subscription_status: SubscriptionStatus
    status_type: YoungStatusType = YoungStatusType.ELIGIBLE


@attrs.frozen
class NonEligible(YoungStatus):
    status_type: YoungStatusType = YoungStatusType.NON_ELIGIBLE


@attrs.frozen
class Beneficiary(YoungStatus):
    status_type: YoungStatusType = YoungStatusType.BENEFICIARY


@attrs.frozen
class ExBeneficiary(YoungStatus):
    status_type: YoungStatusType = YoungStatusType.EX_BENEFICIARY


@attrs.frozen
class Suspended(YoungStatus):
    status_type: YoungStatusType = YoungStatusType.SUSPENDED


@dataclasses.dataclass
class UserSubscriptionState:
    # fraud_status holds the user status relative to its fraud checks. It is mainly used in the admin interface.
    fraud_status: subscription_models.SubscriptionItemStatus

    # next_step holds the next step to be done by the user to complete its subscription.
    # In the frontend, each enum value corresponds to a call to action.
    next_step: subscription_models.SubscriptionStep | None

    # young_status holds the user status relative to its subscription. It is mainly used in the frontend.
    young_status: YoungStatus

    # identity_fraud_check is the relevant identity fraud check used to calculate their status.
    fraud_check: fraud_models.BeneficiaryFraudCheck | None = None  # identity fraud check (a renommer)

    # is_activable is True if beneficiary role can be upgraded.
    is_activable: bool = False

    # subscription_message is the message to display to the user.
    # Be careful : in the frontend, this message is displayed with higher priority than next_step call to action
    subscription_message: subscription_models.SubscriptionMessage | None = None


def young_status(user: models.User) -> YoungStatus:
    if not user.isActive:
        return Suspended()

    if user.is_beneficiary:
        if user.deposit_expiration_date and user.deposit_expiration_date < datetime.utcnow():
            return ExBeneficiary()

        return Beneficiary()

    return subscription_api.get_user_subscription_state(user).young_status

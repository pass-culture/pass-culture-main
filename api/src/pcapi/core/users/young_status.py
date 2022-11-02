from datetime import datetime
import enum

import attrs

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


def young_status(user: models.User) -> YoungStatus:
    if not user.isActive:
        return Suspended()

    if user.is_beneficiary:
        if user.deposit_expiration_date and user.deposit_expiration_date < datetime.utcnow():
            return ExBeneficiary()

        return Beneficiary()

    if user.eligibility is not None:
        if (
            subscription_api.get_identity_check_subscription_status(user, user.eligibility)
            == subscription_models.SubscriptionItemStatus.PENDING
        ):
            return Eligible(subscription_status=SubscriptionStatus.HAS_SUBSCRIPTION_PENDING)

        if subscription_api.has_subscription_issues(user):
            return Eligible(subscription_status=SubscriptionStatus.HAS_SUBSCRIPTION_ISSUES)

        if subscription_api.get_next_subscription_step(user) is not None:
            return Eligible(subscription_status=SubscriptionStatus.HAS_TO_COMPLETE_SUBSCRIPTION)

        # should never happen

    return NonEligible()

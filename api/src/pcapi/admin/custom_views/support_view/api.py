import enum
import logging

from pcapi.core.subscription import api as subscription_api
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription.models import SubscriptionItemStatus
from pcapi.core.users import api as users_api
from pcapi.core.users import models as users_models


logger = logging.getLogger(__name__)


class BeneficiaryActivationStatus(enum.Enum):
    INCOMPLETE = "incomplete"
    KO = "ko"
    NOT_APPLICABLE = "n/a"
    OK = "ok"
    SUSPICIOUS = "suspicious"


SUBSCRIPTION_ITEM_METHODS = [
    subscription_api.get_email_validation_subscription_item,
    subscription_api.get_phone_validation_subscription_item,
    subscription_api.get_user_profiling_subscription_item,
    subscription_api.get_profile_completion_subscription_item,
    subscription_api.get_identity_check_subscription_item,
    subscription_api.get_honor_statement_subscription_item,
]


def get_subscription_items_by_eligibility(
    user: users_models.User,
) -> list[dict[str, subscription_models.SubscriptionItem]]:
    subscription_items = []
    for method in SUBSCRIPTION_ITEM_METHODS:
        subscription_items.append(
            {
                users_models.EligibilityType.UNDERAGE.name: method(user, users_models.EligibilityType.UNDERAGE),
                users_models.EligibilityType.AGE18.name: method(user, users_models.EligibilityType.AGE18),
            },
        )

    return subscription_items


def get_beneficiary_activation_status(user: users_models.User) -> BeneficiaryActivationStatus:
    if user.is_beneficiary and not users_api.is_eligible_for_beneficiary_upgrade(user, user.eligibility):
        return BeneficiaryActivationStatus.OK

    # even if the user is above 18, we want to know the status in case subscription steps were performed
    eligibility = user.eligibility or users_models.EligibilityType.AGE18

    subscription_items = [method(user, eligibility) for method in SUBSCRIPTION_ITEM_METHODS]
    if any(item.status == SubscriptionItemStatus.KO for item in subscription_items):
        return BeneficiaryActivationStatus.KO
    if any(item.status == SubscriptionItemStatus.SUSPICIOUS for item in subscription_items):
        return BeneficiaryActivationStatus.SUSPICIOUS
    if any(item.status in (SubscriptionItemStatus.TODO, SubscriptionItemStatus.PENDING) for item in subscription_items):
        return BeneficiaryActivationStatus.INCOMPLETE

    return BeneficiaryActivationStatus.NOT_APPLICABLE

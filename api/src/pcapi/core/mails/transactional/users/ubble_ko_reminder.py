import datetime
import logging

from dateutil.relativedelta import relativedelta

import pcapi.core.fraud.models as fraud_models
import pcapi.core.users.api as users_api
import pcapi.core.subscription.api as subscription_api
import pcapi.core.subscription.models as subscription_models
import pcapi.core.users.models as users_models


logger = logging.getLogger(__name__)


def find_users_that_failed_ubble_check(days_ago: int = 7) -> list[users_models.User]:
    users = (
        users_models.User.query.join(users_models.User.beneficiaryFraudChecks)
        .filter(
            users_models.User.is_beneficiary == False,
            fraud_models.BeneficiaryFraudCheck.type == fraud_models.FraudCheckType.UBBLE,
            fraud_models.BeneficiaryFraudCheck.status.in_(
                [fraud_models.FraudCheckStatus.KO, fraud_models.FraudCheckStatus.SUSPICIOUS]
            ),
            fraud_models.BeneficiaryFraudCheck.dateCreated < datetime.datetime.utcnow() - relativedelta(days=days_ago),
            fraud_models.BeneficiaryFraudCheck.dateCreated
            >= datetime.datetime.utcnow() - relativedelta(days=days_ago + 1),
        )
        .all()
    )

    return [
        user
        for user in users
        if users_api.is_eligible_for_beneficiary_upgrade(user, user.eligibility)
        and subscription_api.get_identity_check_subscription_status(user, user.eligibility)
        == subscription_models.SubscriptionItemStatus.TODO
    ]

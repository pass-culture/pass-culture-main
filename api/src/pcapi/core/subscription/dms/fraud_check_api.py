import logging

import pcapi.core.subscription.models as subscription_models
import pcapi.core.users.models as users_models
from pcapi.models import db


logger = logging.getLogger(__name__)


def get_fraud_check(
    user: users_models.User, application_number: int
) -> subscription_models.BeneficiaryFraudCheck | None:
    return (
        db.session.query(subscription_models.BeneficiaryFraudCheck)
        .filter(
            subscription_models.BeneficiaryFraudCheck.user == user,
            subscription_models.BeneficiaryFraudCheck.type == subscription_models.FraudCheckType.DMS,
            subscription_models.BeneficiaryFraudCheck.thirdPartyId == str(application_number),
        )
        .order_by(subscription_models.BeneficiaryFraudCheck.id.desc())
        .first()
    )

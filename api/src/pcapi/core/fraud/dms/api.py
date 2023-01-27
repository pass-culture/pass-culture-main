import logging

import pcapi.core.fraud.models as fraud_models
import pcapi.core.users.models as users_models


logger = logging.getLogger(__name__)


def get_fraud_check(user: users_models.User, application_number: int) -> fraud_models.BeneficiaryFraudCheck | None:
    return (
        fraud_models.BeneficiaryFraudCheck.query.filter(
            fraud_models.BeneficiaryFraudCheck.user == user,
            fraud_models.BeneficiaryFraudCheck.type == fraud_models.FraudCheckType.DMS,
            fraud_models.BeneficiaryFraudCheck.thirdPartyId == str(application_number),
        )
        .order_by(fraud_models.BeneficiaryFraudCheck.id.desc())
        .first()
    )

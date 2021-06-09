import logging

from pcapi.core.fraud.models import BeneficiaryFraudCheck
from pcapi.core.fraud.models import FraudCheckType
from pcapi.core.fraud.models import JouveContent
from pcapi.core.users.models import User
from pcapi.repository import repository


logger = logging.getLogger(__name__)


def save_jouve_beneficiary_fraud_check(user: User, application_id: int, jouve_content: dict):
    jouve_fraud_content = JouveContent(**jouve_content)
    fraud_check = BeneficiaryFraudCheck(
        user=user,
        type=FraudCheckType.JOUVE,
        thirdPartyId=str(application_id),
        resultContent=jouve_fraud_content,
    )
    repository.save(fraud_check)


def on_beneficiary_fraud_check_creation(
    fraud_check_type: FraudCheckType, user: User, result_content: JouveContent, third_party_id: str
):
    if BeneficiaryFraudCheck.query.filter_by(user=user, type=fraud_check_type).count() > 0:
        # TODO: raise error and do not allow 2 DMS/Jouve FraudChecks
        return

    fraud_check = BeneficiaryFraudCheck(
        user=user,
        type=fraud_check_type,
        thirdPartyId=third_party_id,
        resultContent=result_content.dict(),
    )
    repository.save(fraud_check)

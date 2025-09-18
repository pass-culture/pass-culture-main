import logging

from pcapi.core import mails
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription import schemas as subscription_schemas
from pcapi.core.users import models as users_models


logger = logging.getLogger(__name__)


def send_duplicate_beneficiary_email(
    rejected_user: users_models.User,
    identity_content: subscription_schemas.IdentityCheckContent,
    duplicate_reason_code: subscription_models.FraudReasonCode,
) -> None:
    from pcapi.core.subscription import fraud_check_api as fraud_api

    anonymized_email = fraud_api.get_duplicate_beneficiary_anonymized_email(
        rejected_user, identity_content, duplicate_reason_code
    )

    mails.send(
        recipients=[rejected_user.email],
        data=models.TransactionalEmailData(
            template=TransactionalEmail.SUBCRIPTION_REJECTED_FOR_DUPLICATE_BENEFICIARY.value,
            params={"DUPLICATE_BENEFICIARY_EMAIL": anonymized_email or "***"},
        ),
    )

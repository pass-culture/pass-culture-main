from typing import Union

from pcapi.core import mails
from pcapi.core.mails.transactional.sendinblue_template_ids import SendinblueTransactionalEmailData
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.subscription.models import BeneficiaryPreSubscription
from pcapi.models.feature import FeatureToggle


def make_fraud_suspicion_data() -> Union[dict, SendinblueTransactionalEmailData]:
    if not FeatureToggle.ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS.is_active():
        return {
            "Mj-TemplateID": 2905960,
            "Mj-TemplateLanguage": True,
            "Mj-campaign": "dossier-en-analyse",
        }

    return SendinblueTransactionalEmailData(template=TransactionalEmail.FRAUD_SUSPICION.value, params={})


def send_fraud_suspicion_email(
    beneficiary_pre_subscription: BeneficiaryPreSubscription,
) -> None:
    data = make_fraud_suspicion_data()
    mails.send(recipients=[beneficiary_pre_subscription.email], data=data)

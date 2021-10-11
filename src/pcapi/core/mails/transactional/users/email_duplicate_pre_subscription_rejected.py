from typing import Union

from pcapi.core import mails
from pcapi.core.mails.transactional.sendinblue_template_ids import SendinblueTransactionalEmailData
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.models.feature import FeatureToggle


def get_not_eligible_beneficiary_pre_subscription_rejected_data() -> dict:
    return {
        "Mj-TemplateID": 1619528,
        "Mj-TemplateLanguage": True,
    }


def send_not_eligible_beneficiary_pre_subscription_rejected_data(email: str) -> bool:
    data = get_not_eligible_beneficiary_pre_subscription_rejected_data()
    return mails.send(recipients=[email], data=data, send_with_sendinblue=False)


def get_duplicate_beneficiary_pre_subscription_rejected_data() -> Union[dict, SendinblueTransactionalEmailData]:
    if not FeatureToggle.ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS.is_active():
        return {
            "Mj-TemplateID": 1530996,
            "Mj-TemplateLanguage": True,
        }

    return SendinblueTransactionalEmailData(
        template=TransactionalEmail.EMAIL_DUPLICATE_BENEFICIARY_PRE_SUBCRIPTION_REJECTED,
        params={},
    )


def send_duplicate_beneficiary_pre_subscription_rejected_data(email: str) -> bool:
    data = get_duplicate_beneficiary_pre_subscription_rejected_data()
    return mails.send(recipients=[email], data=data, send_with_sendinblue=True)

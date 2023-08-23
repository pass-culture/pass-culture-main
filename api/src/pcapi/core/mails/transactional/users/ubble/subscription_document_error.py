from pcapi.core import mails
from pcapi.core.fraud import models as fraud_models
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail

from . import constants


def send_subscription_document_error_email(email: str, code: fraud_models.FraudReasonCode) -> bool:
    data = get_subscription_document_error_email_data(code)
    return mails.send(recipients=[email], data=data)


def get_subscription_document_error_email_data(code: fraud_models.FraudReasonCode) -> models.TransactionalEmailData:
    mapping = constants.ubble_error_to_email_mapping.get(code.value)
    if not mapping:
        template = TransactionalEmail.SUBSCRIPTION_UNREADABLE_DOCUMENT_ERROR
    else:
        template = mapping.template

    return models.TransactionalEmailData(template=template.value)

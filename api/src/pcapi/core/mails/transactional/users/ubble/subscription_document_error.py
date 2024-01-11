from pcapi.core import mails
from pcapi.core.fraud import models as fraud_models
from pcapi.core.mails import models

from . import constants


def send_subscription_document_error_email(
    email: str, code: fraud_models.FraudReasonCode, is_reminder: bool = False
) -> None:
    data = get_subscription_document_error_email_data(code, is_reminder)
    mails.send(recipients=[email], data=data)


def get_subscription_document_error_email_data(
    code: fraud_models.FraudReasonCode, is_reminder: bool = False
) -> models.TransactionalEmailData:
    mapping = constants.ubble_error_to_email_mapping.get(code.value, constants.default_email)
    template = mapping.reminder_template if is_reminder else mapping.template

    return models.TransactionalEmailData(template=template.value)

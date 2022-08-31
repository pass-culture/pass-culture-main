from pcapi.core import mails
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail


def send_subscription_document_error_email(email: str, code: str) -> bool:
    data = get_subscription_document_error_email_data(code)
    return mails.send(recipients=[email], data=data)


def get_subscription_document_error_email_data(code: str) -> models.TransactionalEmailData:
    error_codes_switch = {
        "information-error": TransactionalEmail.SUBSCRIPTION_INFORMATION_ERROR,
        "unread-document": TransactionalEmail.SUBSCRIPTION_UNREADABLE_DOCUMENT_ERROR,
        "invalid-document": TransactionalEmail.SUBSCRIPTION_INVALID_DOCUMENT_ERROR,
        "unread-mrz-document": TransactionalEmail.SUBSCRIPTION_FOREIGN_DOCUMENT_ERROR,
    }
    template = error_codes_switch.get(code, TransactionalEmail.SUBSCRIPTION_INFORMATION_ERROR)
    return models.TransactionalEmailData(template=template.value)

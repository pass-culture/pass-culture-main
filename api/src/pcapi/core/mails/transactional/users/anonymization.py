from pcapi.core import mails
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail


def get_anonymization_email_data() -> models.TransactionalEmailData:
    return models.TransactionalEmailData(template=TransactionalEmail.ANONYMIZATION_CONFIRMATION.value)


def send_anonymization_confirmation_email_to_pro(user_email: str) -> None:
    data = get_anonymization_email_data()
    mails.send(recipients=[user_email], data=data)

from pcapi.core import mails
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail


def get_bank_account_validated_email_data() -> models.TransactionalEmailData:
    return models.TransactionalEmailData(template=TransactionalEmail.BANK_ACCOUNT_VALIDATED.value)


def send_bank_account_validated_email(email: str) -> None:
    data = get_bank_account_validated_email_data()
    mails.send(recipients=[email], data=data)

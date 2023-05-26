from pcapi.core import mails
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail


def get_suspicious_login_email_data() -> models.TransactionalEmailData:
    return models.TransactionalEmailData(template=TransactionalEmail.SUSPICIOUS_LOGIN.value)


def send_suspicious_login_email(
    user_email: str,
) -> bool:
    data = get_suspicious_login_email_data()
    return mails.send(recipients=[user_email], data=data)

from pcapi.core import mails
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.users.models import User


def send_unsuspension_email(user: User) -> None:
    data = models.TransactionalEmailData(template=TransactionalEmail.ACCOUNT_UNSUSPENDED.value)
    mails.send(recipients=[user.email], data=data)

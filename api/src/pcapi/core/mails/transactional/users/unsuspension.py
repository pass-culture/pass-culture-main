from pcapi.core import mails
from pcapi.core.mails.models.sendinblue_models import SendinblueTransactionalEmailData
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.users.models import User


def send_unsuspension_email(user: User) -> bool:
    data = SendinblueTransactionalEmailData(template=TransactionalEmail.ACCOUNT_UNSUSPENDED.value)
    return mails.send(recipients=[user.email], data=data)

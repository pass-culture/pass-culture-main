from pcapi.core import mails
from pcapi.core.mails.models.sendinblue_models import SendinblueTransactionalEmailData
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.users.models import User


def get_welcome_to_pro_email_data() -> SendinblueTransactionalEmailData:
    return SendinblueTransactionalEmailData(
        template=TransactionalEmail.WELCOME_TO_PRO.value,
    )


def send_welcome_to_pro_email(user: User) -> bool:
    data = get_welcome_to_pro_email_data()
    return mails.send(recipients=[user.email], data=data)

from pcapi.core import mails
from pcapi.core.mails.transactional.sendinblue_template_ids import SendinblueTransactionalEmailData
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.users.models import User


def get_delete_account_confirmation_email_data(user: User) -> SendinblueTransactionalEmailData:
    return SendinblueTransactionalEmailData(
        template=TransactionalEmail.DELETE_ACCOUNT_CONFIRMATION_TO_USER.value,
        params={
            "FIRSTNAME": user.firstName,
        },
    )


def send_delete_account_confirmation_email_to_user(user: User) -> bool:
    data = get_delete_account_confirmation_email_data(user)
    return mails.send(recipients=[user.email], data=data)

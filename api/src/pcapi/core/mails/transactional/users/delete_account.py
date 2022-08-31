from pcapi.core import mails
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.users.models import User


def get_user_request_to_delete_account_email_data(user: User) -> models.TransactionalEmailData:
    return models.TransactionalEmailData(
        template=TransactionalEmail.USER_REQUEST_DELETE_ACCOUNT_RECEPTION.value,
        params={
            "FIRSTNAME": user.firstName,
        },
    )


def send_user_request_to_delete_account_reception_email(user: User) -> bool:
    data = get_user_request_to_delete_account_email_data(user)
    return mails.send(recipients=[user.email], data=data)

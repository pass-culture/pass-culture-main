from pcapi.core import mails
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
import pcapi.core.users.models as users_models


def get_send_email_before_deletion_of_suspended_account_data(user: users_models.User) -> models.TransactionalEmailData:
    return models.TransactionalEmailData(
        template=TransactionalEmail.NOTIFICATION_BEFORE_DELETING_SUSPENDED_ACCOUNT.value,
        params={
            "FIRSTNAME": user.firstName,
        },
    )


def send_email_before_deletion_of_suspended_account(user: users_models.User) -> bool:
    data = get_send_email_before_deletion_of_suspended_account_data(user)
    return mails.send(recipients=[user.email], data=data)

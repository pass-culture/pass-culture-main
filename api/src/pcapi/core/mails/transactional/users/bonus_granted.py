from pcapi.core import mails
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.users import models as users_models


def get_bonus_granted_email_data(user: users_models.User) -> models.TransactionalEmailData:
    return models.TransactionalEmailData(
        template=TransactionalEmail.BONUS_GRANTED.value,
    )


def send_bonus_granted_email(user: users_models.User) -> None:
    data = get_bonus_granted_email_data(user)
    mails.send(recipients=[user.email], data=data)

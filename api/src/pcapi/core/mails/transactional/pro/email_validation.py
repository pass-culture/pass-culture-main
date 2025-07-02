from pcapi import settings
from pcapi.core import mails
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.users.models import User


def get_email_validation_to_pro_email_data(token: str) -> models.TransactionalEmailData:
    return models.TransactionalEmailData(
        template=TransactionalEmail.SIGNUP_EMAIL_CONFIRMATION_TO_PRO.value,
        params={
            "EMAIL_VALIDATION_LINK": f"{settings.PRO_URL}/inscription/compte/confirmation/{token}",
        },
    )


def send_signup_email_confirmation_to_pro(user: User, token: str) -> None:
    data = get_email_validation_to_pro_email_data(token)
    mails.send(recipients=[user.email], data=data)

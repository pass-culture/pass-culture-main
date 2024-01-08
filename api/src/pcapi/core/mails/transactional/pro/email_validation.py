from pcapi import settings
from pcapi.core import mails
from pcapi.core import token as token_utils
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.users.models import User


def get_email_validation_to_pro_email_data(token: token_utils.Token) -> models.TransactionalEmailData:
    return models.TransactionalEmailData(
        template=TransactionalEmail.EMAIL_VALIDATION_TO_PRO.value,
        params={
            "EMAIL_VALIDATION_LINK": f"{settings.PRO_URL}/inscription/validation/{token.encoded_token}",
        },
    )


def send_email_validation_to_pro_email(user: User, token: token_utils.Token) -> bool:
    data = get_email_validation_to_pro_email_data(token)
    return mails.send(recipients=[user.email], data=data)

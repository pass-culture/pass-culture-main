from datetime import datetime

from pcapi.core import mails
from pcapi.core import token as token_utils
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.users import constants
from pcapi.utils.urls import generate_app_link


def get_email_confirmation_email_data(email: str, token: token_utils.Token) -> models.TransactionalEmailData:
    expiration_date = (
        token.get_expiration_date_from_token() or datetime.utcnow() + constants.EMAIL_VALIDATION_TOKEN_LIFE_TIME
    )
    expiration_timestamp = int(expiration_date.timestamp())
    email_confirmation_link = generate_app_link(
        path="signup-confirmation",
        params={"token": token.encoded_token, "expiration_timestamp": expiration_timestamp, "email": email},
    )

    return models.TransactionalEmailData(
        template=TransactionalEmail.EMAIL_CONFIRMATION.value,
        params={
            "CONFIRMATION_LINK": email_confirmation_link,
        },
    )


def send_email_confirmation_email(email: str, token: token_utils.Token) -> None:
    data = get_email_confirmation_email_data(email, token)
    mails.send(recipients=[email], data=data)

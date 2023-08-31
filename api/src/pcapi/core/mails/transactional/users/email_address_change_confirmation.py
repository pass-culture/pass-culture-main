from datetime import datetime

from pcapi.core import mails
from pcapi.core import token as token_utils
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.users import constants
from pcapi.core.users import models as users_models
from pcapi.core.users.models import User
from pcapi.utils.urls import generate_firebase_dynamic_link


def get_email_confirmation_email_data(
    user: users_models.User, token: token_utils.Token
) -> models.TransactionalEmailData:
    expiration_date = (
        token.get_expiration_date(token_utils.TokenType.EMAIL_VALIDATION, user.id)
        or datetime.utcnow() + constants.EMAIL_VALIDATION_TOKEN_LIFE_TIME
    )
    expiration_timestamp = int(expiration_date.timestamp())
    email_confirmation_link = generate_firebase_dynamic_link(
        path="signup-confirmation",
        params={"token": token.encoded_token, "expiration_timestamp": expiration_timestamp, "email": user.email},
    )

    return models.TransactionalEmailData(
        template=TransactionalEmail.EMAIL_CONFIRMATION.value,
        params={
            "CONFIRMATION_LINK": email_confirmation_link,
        },
    )


def send_email_confirmation_email(user: User, token: token_utils.Token) -> bool:
    data = get_email_confirmation_email_data(user=user, token=token)
    return mails.send(recipients=[user.email], data=data)

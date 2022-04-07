from pcapi.core import mails
from pcapi.core.mails.models.sendinblue_models import SendinblueTransactionalEmailData
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.users import models as users_models
from pcapi.core.users.models import Token
from pcapi.core.users.models import User
from pcapi.utils.urls import generate_firebase_dynamic_link


def get_email_confirmation_email_data(
    user: users_models.User, token: users_models.Token
) -> SendinblueTransactionalEmailData:
    expiration_timestamp = int(token.expirationDate.timestamp())  # type: ignore [union-attr]
    email_confirmation_link = generate_firebase_dynamic_link(
        path="signup-confirmation",
        params={"token": token.value, "expiration_timestamp": expiration_timestamp, "email": user.email},
    )

    return SendinblueTransactionalEmailData(
        template=TransactionalEmail.EMAIL_CONFIRMATION.value,
        params={
            "CONFIRMATION_LINK": email_confirmation_link,
        },
    )


def send_email_confirmation_email(user: User, token: Token) -> bool:
    data = get_email_confirmation_email_data(user=user, token=token)
    return mails.send(recipients=[user.email], data=data)

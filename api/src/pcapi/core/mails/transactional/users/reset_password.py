from pcapi.core import mails
from pcapi.core.mails.models.sendinblue_models import SendinblueTransactionalEmailData
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.users import api as users_api
from pcapi.core.users.models import Token
from pcapi.core.users.models import User
from pcapi.utils.urls import generate_firebase_dynamic_link


def send_reset_password_email_to_user(user: User) -> bool:
    token = users_api.create_reset_password_token(user)
    data = get_reset_password_email_data(user, token)
    return mails.send(recipients=[user.email], data=data)


def get_reset_password_email_data(user: User, token: Token) -> SendinblueTransactionalEmailData:
    reset_password_link = generate_firebase_dynamic_link(
        path="mot-de-passe-perdu",
        params={
            "token": token.value,
            "expiration_timestamp": int(token.expirationDate.timestamp()),
            "email": user.email,
        },
    )

    return SendinblueTransactionalEmailData(
        template=TransactionalEmail.NEW_PASSWORD_REQUEST.value,
        params={
            "FIRSTNAME": user.firstName,
            "RESET_PASSWORD_LINK": reset_password_link,
        },
    )

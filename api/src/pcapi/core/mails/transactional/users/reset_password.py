from pcapi.core import mails
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.users import api as users_api
from pcapi.core.users import models as user_models
from pcapi.utils.urls import generate_firebase_dynamic_link


def send_reset_password_email_to_user(user: user_models.User) -> bool:
    token = users_api.create_reset_password_token(user)
    data = get_reset_password_email_data(user, token, TransactionalEmail.NEW_PASSWORD_REQUEST.value)
    return mails.send(recipients=[user.email], data=data)


def send_email_already_exists_email(user: user_models.User) -> bool:
    token = users_api.create_reset_password_token(user)
    data = get_reset_password_email_data(user, token, TransactionalEmail.EMAIL_ALREADY_EXISTS.value)
    return mails.send(recipients=[user.email], data=data)


def get_reset_password_email_data(
    user: user_models.User, token: user_models.Token, email_template: models.Template
) -> models.TransactionalEmailData:
    # We called `create_reset_password_token()` without explicly
    # passing an empty expiration date. The token hence has one.
    assert token.expirationDate  # helps mypy
    reset_password_link = generate_firebase_dynamic_link(
        path="mot-de-passe-perdu",
        params={
            "token": token.value,
            "expiration_timestamp": int(token.expirationDate.timestamp()),
            "email": user.email,
        },
    )

    return models.TransactionalEmailData(
        template=email_template,
        params={
            "FIRSTNAME": user.firstName,
            "RESET_PASSWORD_LINK": reset_password_link,
        },
    )

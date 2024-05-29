from pcapi.core import mails
from pcapi.core import token as token_utils
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.users import constants
import pcapi.core.users.models as users_models
from pcapi.utils.urls import generate_firebase_dynamic_link


def send_reset_password_email_to_user(
    token: token_utils.Token, reason: constants.SuspensionReason | None = None
) -> None:
    user = users_models.User.query.filter_by(id=token.user_id).one()
    email_template = (
        TransactionalEmail.NEW_PASSWORD_REQUEST_FOR_SUSPICIOUS_LOGIN
        if reason == constants.SuspensionReason.SUSPICIOUS_LOGIN_REPORTED_BY_USER
        else TransactionalEmail.NEW_PASSWORD_REQUEST
    )
    data = get_reset_password_email_data(user, token, email_template.value)
    mails.send(recipients=[user.email], data=data)


def send_email_already_exists_email(token: token_utils.Token) -> None:
    user = users_models.User.query.filter_by(id=token.user_id).one()
    data = get_reset_password_email_data(user, token, TransactionalEmail.EMAIL_ALREADY_EXISTS.value)
    mails.send(recipients=[user.email], data=data)


def get_reset_password_email_data(
    user: users_models.User, token: token_utils.Token, email_template: models.Template
) -> models.TransactionalEmailData:
    # We called `create_reset_password_token()` without explicly
    # passing an empty expiration date. The token hence has one.
    expiration_date = token.get_expiration_date_from_token()
    assert expiration_date  # helps mypy
    reset_password_link = generate_firebase_dynamic_link(
        path="mot-de-passe-perdu",
        params={
            "token": token.encoded_token,
            "expiration_timestamp": int(expiration_date.timestamp()),
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

import typing

from pcapi.core import mails
from pcapi.core.mails.transactional.sendinblue_template_ids import SendinblueTransactionalEmailData
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.users import api as users_api
from pcapi.core.users.models import Token
from pcapi.core.users.models import User
from pcapi.models.feature import FeatureToggle
from pcapi.utils.urls import generate_firebase_dynamic_link


def retrieve_data_for_reset_password_user_email(user: User, token: Token) -> dict:
    return {
        "MJ-TemplateID": 912168,
        "MJ-TemplateLanguage": True,
        "Vars": {"prenom_user": user.firstName, "token": token.value},
    }


def retrieve_data_for_reset_password_native_app_email(
    user: User, token: Token
) -> typing.Union[dict, SendinblueTransactionalEmailData]:
    reset_password_link = generate_firebase_dynamic_link(
        path="mot-de-passe-perdu",
        params={
            "token": token.value,
            "expiration_timestamp": int(token.expirationDate.timestamp()),
            "email": user.email,
        },
    )

    if not FeatureToggle.ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS.is_active():
        return {
            "MJ-TemplateID": 1838526,
            "MJ-TemplateLanguage": True,
            "Mj-trackclick": 1,
            "Vars": {"native_app_link": reset_password_link},
        }

    return SendinblueTransactionalEmailData(
        template=TransactionalEmail.NEW_PASSWORD_REQUEST.value, params={"NATIVE_APP_LINK": reset_password_link}
    )


def send_reset_password_email_to_user(user: User) -> bool:
    token = users_api.create_reset_password_token(user)
    data = retrieve_data_for_reset_password_user_email(user, token)
    return mails.send(recipients=[user.email], data=data)


def send_reset_password_email_to_native_app_user(user: User) -> bool:
    token = users_api.create_reset_password_token(user)
    data = retrieve_data_for_reset_password_native_app_email(user, token)
    return mails.send(recipients=[user.email], data=data, send_with_sendinblue=True)

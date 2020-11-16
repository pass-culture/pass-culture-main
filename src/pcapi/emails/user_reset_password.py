from datetime import datetime
from typing import Dict

from pcapi.models import UserSQLEntity
from pcapi.repository.feature_queries import feature_send_mail_to_users_enabled
from pcapi.utils.config import NATIVE_APP_URL
from pcapi.utils.mailing import DEV_EMAIL_ADDRESS
from pcapi.utils.mailing import SUPPORT_EMAIL_ADDRESS
from pcapi.utils.mailing import format_environment_for_email


def retrieve_data_for_reset_password_user_email(user: UserSQLEntity) -> Dict:
    user_first_name = user.firstName
    user_email = user.email
    user_reset_password_token = user.resetPasswordToken
    env = format_environment_for_email()

    return {
        "FromEmail": SUPPORT_EMAIL_ADDRESS,
        "MJ-TemplateID": 912168,
        "MJ-TemplateLanguage": True,
        "To": user_email if feature_send_mail_to_users_enabled() else DEV_EMAIL_ADDRESS,
        "Vars": {"prenom_user": user_first_name, "token": user_reset_password_token, "env": env},
    }


def retrieve_data_for_reset_password_native_app_email(
    user_email: str, token_value: str, expiration_date: datetime
) -> Dict:
    reset_password_link = (
        f"{NATIVE_APP_URL}/mot-de-passe-perdu?token={token_value}"
        f"&expiration_timestamp={int(expiration_date.timestamp())}"
    )

    return {
        "FromEmail": SUPPORT_EMAIL_ADDRESS,
        "MJ-TemplateID": 1838526,
        "MJ-TemplateLanguage": True,
        "To": user_email if feature_send_mail_to_users_enabled() else DEV_EMAIL_ADDRESS,
        "Vars": {"native_app_link": reset_password_link},
    }

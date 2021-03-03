from datetime import datetime
from typing import Dict
from urllib.parse import urlencode

from pcapi import settings
from pcapi.core.users.models import User


def retrieve_data_for_reset_password_user_email(user: User) -> Dict:
    user_first_name = user.firstName
    user_reset_password_token = user.resetPasswordToken

    return {
        "MJ-TemplateID": 912168,
        "MJ-TemplateLanguage": True,
        "Vars": {"prenom_user": user_first_name, "token": user_reset_password_token},
    }


def retrieve_data_for_reset_password_native_app_email(
    user_email: str, token_value: str, expiration_date: datetime
) -> Dict:
    query_string = urlencode(
        {
            "token": token_value,
            "expiration_timestamp": int(expiration_date.timestamp()),
            "email": user_email,
        }
    )
    reset_password_link = f"{settings.NATIVE_APP_URL}/mot-de-passe-perdu?{query_string}"

    return {
        "MJ-TemplateID": 1838526,
        "MJ-TemplateLanguage": True,
        "Mj-trackclick": 1,
        "Vars": {"native_app_link": reset_password_link},
    }

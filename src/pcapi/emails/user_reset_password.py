from typing import Dict
from urllib.parse import urlencode

from pcapi import settings
from pcapi.core.users.models import Token
from pcapi.core.users.models import User


def retrieve_data_for_reset_password_user_email(user: User, token: Token) -> Dict:
    return {
        "MJ-TemplateID": 912168,
        "MJ-TemplateLanguage": True,
        "Vars": {"prenom_user": user.firstName, "token": token.value},
    }


def retrieve_data_for_reset_password_native_app_email(user: User, token: Token) -> Dict:
    query_string = urlencode(
        {
            "token": token.value,
            "expiration_timestamp": int(token.expirationDate.timestamp()),
            "email": user.email,
        }
    )
    reset_password_link = f"{settings.NATIVE_APP_URL}/mot-de-passe-perdu?{query_string}"

    return {
        "MJ-TemplateID": 1838526,
        "MJ-TemplateLanguage": True,
        "Mj-trackclick": 1,
        "Vars": {"native_app_link": reset_password_link},
    }

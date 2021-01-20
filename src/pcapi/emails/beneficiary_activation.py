from datetime import datetime
from typing import Dict
from urllib.parse import quote
from urllib.parse import urlencode

from dateutil.relativedelta import relativedelta

from pcapi import settings
from pcapi.core.users import api as users_api
from pcapi.core.users import models as users_models
from pcapi.repository.feature_queries import feature_send_mail_to_users_enabled
from pcapi.utils.mailing import format_environment_for_email


def get_activation_email_data(user: users_models.User) -> Dict:
    first_name = user.firstName.capitalize()
    email = user.email
    token = user.resetPasswordToken
    env = format_environment_for_email()

    return {
        "FromEmail": settings.SUPPORT_EMAIL_ADDRESS,
        "Mj-TemplateID": 994771,
        "Mj-TemplateLanguage": True,
        "To": email if feature_send_mail_to_users_enabled() else settings.DEV_EMAIL_ADDRESS,
        "Vars": {"prenom_user": first_name, "token": token, "email": quote(email), "env": env},
    }


def get_activation_email_data_for_native(user: users_models.User, token: users_models.Token) -> Dict:
    expiration_timestamp = int(token.expirationDate.timestamp())
    query_string = urlencode({"token": token.value, "expiration_timestamp": expiration_timestamp, "email": user.email})
    email_confirmation_link = f"{settings.NATIVE_APP_URL}/signup-confirmation?{query_string}"
    return {
        "FromEmail": settings.SUPPORT_EMAIL_ADDRESS,
        "Mj-TemplateID": 2015423,
        "Mj-TemplateLanguage": True,
        "To": user.email if feature_send_mail_to_users_enabled() else settings.DEV_EMAIL_ADDRESS,
        "Vars": {
            "nativeAppLink": email_confirmation_link,
            "isEligible": int(users_api.is_user_eligible(user)),
            "isMinor": int(user.dateOfBirth + relativedelta(years=18) > datetime.today()),
        },
    }

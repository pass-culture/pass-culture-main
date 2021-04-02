from datetime import datetime
from typing import Dict
from urllib.parse import quote
from urllib.parse import urlencode

from dateutil.relativedelta import relativedelta

from pcapi import settings
from pcapi.core.bookings import conf
from pcapi.core.users import models as users_models


def get_activation_email_data(user: users_models.User) -> Dict:
    first_name = user.firstName.capitalize()
    email = user.email
    token = user.resetPasswordToken

    return {
        "Mj-TemplateID": 994771,
        "Mj-TemplateLanguage": True,
        "Vars": {
            "prenom_user": first_name,
            "token": token,
            "email": quote(email),
        },
    }


def get_activation_email_data_for_native(user: users_models.User, token: users_models.Token) -> Dict:
    expiration_timestamp = int(token.expirationDate.timestamp())
    query_string = urlencode({"token": token.value, "expiration_timestamp": expiration_timestamp, "email": user.email})
    email_confirmation_link = f"{settings.NATIVE_APP_URL}/signup-confirmation?{query_string}"
    limit_configuration = conf.LIMIT_CONFIGURATIONS[conf.get_current_deposit_version()]
    deposit_amount = limit_configuration.TOTAL_CAP
    return {
        "Mj-TemplateID": 2015423,
        "Mj-TemplateLanguage": True,
        "Mj-trackclick": 1,
        "Vars": {
            "nativeAppLink": email_confirmation_link,
            "isEligible": int(user.is_eligible),
            "isMinor": int(user.dateOfBirth + relativedelta(years=18) > datetime.today()),
            "depositAmount": int(deposit_amount),
        },
    }


def get_accepted_as_beneficiary_email_data() -> Dict:
    limit_configuration = conf.LIMIT_CONFIGURATIONS[conf.get_current_deposit_version()]
    deposit_amount = limit_configuration.TOTAL_CAP
    return {
        "Mj-TemplateID": 2016025,
        "Mj-TemplateLanguage": True,
        "Vars": {
            "depositAmount": int(deposit_amount),
        },
    }


def get_newly_eligible_user_email_data(user: users_models.User, token: users_models.Token) -> Dict:
    expiration_timestamp = int(token.expirationDate.timestamp())
    query_string = urlencode(
        {"licenceToken": token.value, "expirationTimestamp": expiration_timestamp, "email": user.email}
    )
    email_link = f"{settings.NATIVE_APP_URL}/id-check?{query_string}"
    return {
        "Mj-TemplateID": 2030056,
        "Mj-TemplateLanguage": True,
        "Mj-trackclick": 1,
        "Vars": {
            "nativeAppLink": email_link,
        },
    }

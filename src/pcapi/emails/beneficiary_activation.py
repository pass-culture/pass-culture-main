from datetime import datetime
from typing import Union
from urllib.parse import quote

from dateutil.relativedelta import relativedelta

from pcapi import settings
from pcapi.core.bookings import conf
from pcapi.core.mails.transactional.models import SendinblueTransactionalEmailData
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmailSlug
from pcapi.core.users import models as users_models
from pcapi.models.deposit import DepositType
from pcapi.models.feature import FeatureToggle
from pcapi.utils.urls import generate_firebase_dynamic_link


def get_activation_email_data(
    user: users_models.User, token: users_models.Token
) -> Union[dict, SendinblueTransactionalEmailData]:
    first_name = user.firstName.capitalize()
    email = user.email

    if FeatureToggle.ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS.is_active():
        return SendinblueTransactionalEmailData(
            template_id_slug=TransactionalEmailSlug.ACTIVATION_EMAIL,
            params={
                "prenom_user": first_name,
                "token": token,
                "activation_link": f"{settings.WEBAPP_FOR_NATIVE_REDIRECTION}/activation/{token}?email={email}",
            },
            tags=[],
        )

    return {
        "Mj-TemplateID": 994771,
        "Mj-TemplateLanguage": True,
        "Vars": {
            "prenom_user": first_name,
            "token": token.value,
            "email": quote(email),
        },
    }


def get_activation_email_data_for_native(user: users_models.User, token: users_models.Token) -> dict:
    expiration_timestamp = int(token.expirationDate.timestamp())
    email_confirmation_link = generate_firebase_dynamic_link(
        path="signup-confirmation",
        params={"token": token.value, "expiration_timestamp": expiration_timestamp, "email": user.email},
    )
    limit_configuration = conf.get_current_limit_configuration_for_type(DepositType.GRANT_18)
    deposit_amount = limit_configuration.TOTAL_CAP
    return {
        "Mj-TemplateID": 2015423,
        "Mj-TemplateLanguage": True,
        "Mj-campaign": "confirmation-compte",
        "Mj-trackclick": 1,
        "Vars": {
            "nativeAppLink": email_confirmation_link,
            "isEligible": int(user.is_eligible),
            "isMinor": int(user.dateOfBirth + relativedelta(years=18) > datetime.today()),
            "depositAmount": int(deposit_amount),
        },
    }


def get_accepted_as_beneficiary_email_data() -> dict:
    limit_configuration = conf.get_current_limit_configuration_for_type(DepositType.GRANT_18)
    deposit_amount = limit_configuration.TOTAL_CAP
    return {
        "Mj-TemplateID": 2016025,
        "Mj-TemplateLanguage": True,
        "Mj-campaign": "confirmation-credit",
        "Vars": {
            "depositAmount": int(deposit_amount),
        },
    }


def get_newly_eligible_user_email_data(user: users_models.User) -> dict:
    email_link = generate_firebase_dynamic_link(
        path="id-check",
        params={"email": user.email},
    )
    limit_configuration = conf.get_current_limit_configuration_for_type(DepositType.GRANT_18)
    deposit_amount = limit_configuration.TOTAL_CAP
    return {
        "Mj-TemplateID": 2030056,
        "Mj-TemplateLanguage": True,
        "Mj-trackclick": 1,
        "Vars": {
            "nativeAppLink": email_link,
            "depositAmount": int(deposit_amount),
        },
    }


def get_dms_application_data() -> dict:
    return {
        "Mj-TemplateID": 3062771,
        "Mj-TemplateLanguage": True,
    }

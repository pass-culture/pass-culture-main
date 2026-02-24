from pcapi import settings
from pcapi.core.subscription import fraud_check_api as fraud_api
from pcapi.core.users import models as users_models

from . import constants
from . import exceptions


def check_phone_number_is_legit(user: users_models.User, phone_number: str, country_code: int | None) -> None:
    if phone_number in settings.BLACKLISTED_SMS_RECIPIENTS:
        fraud_api.handle_blacklisted_sms_recipient(user, phone_number)
        raise exceptions.InvalidPhoneNumber()

    if country_code not in constants.WHITELISTED_COUNTRY_PHONE_CODES:
        fraud_api.handle_invalid_country_code(user, phone_number)
        raise exceptions.InvalidCountryCode()

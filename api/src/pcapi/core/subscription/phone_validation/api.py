from contextlib import contextmanager
from datetime import datetime
import typing

from flask import current_app as app
from redis import Redis

from pcapi import settings
import pcapi.core.fraud.api as fraud_api
from pcapi.core.fraud.phone_validation.sending_limit import get_code_validation_attempts
from pcapi.core.fraud.phone_validation.sending_limit import is_SMS_sending_allowed
from pcapi.core.fraud.phone_validation.sending_limit import update_sent_SMS_counter
from pcapi.core.subscription import api as subscription_api
from pcapi.core.users.api import create_phone_validation_token
from pcapi.core.users.models import PhoneValidationStatusType
from pcapi.core.users.models import Token
from pcapi.core.users.models import TokenType
from pcapi.core.users.models import User
from pcapi.core.users.repository import does_validated_phone_exist
from pcapi.models import db
from pcapi.notifications.sms import send_transactional_sms
from pcapi.repository import repository
from pcapi.utils import phone_number as phone_number_utils

from . import constants
from . import exceptions


def validate_phone_number_and_activate_user(user: User, code: str) -> User:  # type: ignore [return]
    validate_phone_number(user, code)

    subscription_api.activate_beneficiary_if_no_missing_step(user)


def send_phone_validation_code(user: User, phone_number: str) -> None:
    _check_phone_number_validation_is_authorized(user)

    phone_data = phone_number_utils.ParsedPhoneNumber(phone_number)
    with fraud_manager(user=user, phone_number=phone_data.phone_number):
        check_phone_number_is_legit(phone_data.phone_number, phone_data.country_code)
        check_phone_number_not_used(phone_data.phone_number)
        check_sms_sending_is_allowed(user)

    # delete previous token so that the user validates with another phone number
    Token.query.filter(Token.user == user, Token.type == TokenType.PHONE_VALIDATION).delete()
    user.phoneNumber = phone_data.phone_number
    repository.save(user)

    phone_validation_token = create_phone_validation_token(user)
    content = f"{phone_validation_token.value} est ton code de confirmation pass Culture"  # type: ignore [union-attr]

    if not send_transactional_sms(phone_data.phone_number, content):
        raise exceptions.PhoneVerificationCodeSendingException()

    update_sent_SMS_counter(app.redis_client, user)  # type: ignore [attr-defined]


def validate_phone_number(user: User, code: str) -> None:
    _check_phone_number_validation_is_authorized(user)

    phone_data = phone_number_utils.ParsedPhoneNumber(user.phoneNumber)  # type: ignore [arg-type]
    with fraud_manager(user=user, phone_number=phone_data.phone_number):
        check_phone_number_is_legit(phone_data.phone_number, phone_data.country_code)
        check_and_update_phone_validation_attempts(app.redis_client, user)  # type: ignore [attr-defined]

    token = Token.query.filter(
        Token.user == user, Token.value == code, Token.type == TokenType.PHONE_VALIDATION
    ).one_or_none()

    if not token:
        code_validation_attempts = get_code_validation_attempts(app.redis_client, user)  # type: ignore [attr-defined]
        if code_validation_attempts.remaining == 0:
            fraud_api.handle_phone_validation_attempts_limit_reached(user, code_validation_attempts.attempts)
        raise exceptions.NotValidCode(remaining_attempts=code_validation_attempts.remaining)

    if token.expirationDate and token.expirationDate < datetime.utcnow():
        raise exceptions.ExpiredCode()

    db.session.delete(token)

    # not wrapped inside a fraud_manager because we don't need to add any fraud
    # log in case this check raises an exception at this point
    check_phone_number_not_used(phone_data.phone_number)

    user.phoneValidationStatus = PhoneValidationStatusType.VALIDATED  # type: ignore [assignment]
    user.validate_phone()
    repository.save(user)


def check_phone_number_is_legit(phone_number: str, country_code: str) -> None:
    if phone_number in settings.BLACKLISTED_SMS_RECIPIENTS:
        raise exceptions.BlacklistedPhoneNumber(phone_number)

    if country_code not in constants.WHITELISTED_COUNTRY_PHONE_CODES:
        raise exceptions.InvalidCountryCode(country_code)


def _check_phone_number_validation_is_authorized(user: User) -> None:
    if user.is_phone_validated:
        raise exceptions.UserPhoneNumberAlreadyValidated()

    if not user.isEmailValidated:
        raise exceptions.UnvalidatedEmail()

    if user.has_beneficiary_role:
        raise exceptions.UserAlreadyBeneficiary()


def check_and_update_phone_validation_attempts(redis: Redis, user: User) -> None:
    code_validation_attempts = get_code_validation_attempts(redis, user)

    if code_validation_attempts.remaining == 0:
        raise exceptions.PhoneValidationAttemptsLimitReached(code_validation_attempts.attempts)

    phone_validation_attempts_key = f"phone_validation_attempts_user_{user.id}"
    count = redis.incr(phone_validation_attempts_key)
    if count == 1:
        redis.expire(phone_validation_attempts_key, settings.PHONE_VALIDATION_ATTEMPTS_TTL)


def check_phone_number_not_used(phone_number: str) -> None:
    if does_validated_phone_exist(phone_number):
        raise exceptions.PhoneAlreadyExists(phone_number)


def check_sms_sending_is_allowed(user: User) -> None:
    if not is_SMS_sending_allowed(app.redis_client, user):  # type: ignore [attr-defined]
        raise exceptions.SMSSendingLimitReached()


@contextmanager
def fraud_manager(user: User, phone_number: str) -> typing.Generator:
    try:
        yield
    except exceptions.BlacklistedPhoneNumber:
        fraud_api.handle_blacklisted_sms_recipient(user, phone_number)
        user.validate_phone_failed()
        repository.save(user)
        raise
    except exceptions.PhoneAlreadyExists:
        fraud_api.handle_phone_already_exists(user, phone_number)
        user.validate_phone_failed()
        repository.save(user)
        raise
    except exceptions.SMSSendingLimitReached:
        fraud_api.handle_sms_sending_limit_reached(user)
        user.validate_phone_failed()
        repository.save(user)
        raise
    except exceptions.PhoneValidationAttemptsLimitReached as error:
        fraud_api.handle_phone_validation_attempts_limit_reached(user, error.attempts)
        user.validate_phone_failed()
        repository.save(user)
        raise
    except exceptions.InvalidCountryCode:
        fraud_api.handle_invalid_country_code(user, phone_number)
        raise

import datetime

from flask import current_app as app
from redis import Redis

from pcapi import settings
from pcapi.core.fraud import api as fraud_api
from pcapi.core.fraud.phone_validation import sending_limit
from pcapi.core.users import api as users_api
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.notifications import sms as sms_notifications
from pcapi.repository import repository
from pcapi.utils import phone_number as phone_number_utils

from . import constants
from . import exceptions


def _check_phone_number_validation_is_authorized(user: users_models.User) -> None:
    if user.is_phone_validated:
        raise exceptions.UserPhoneNumberAlreadyValidated()

    if not user.isEmailValidated or user.has_beneficiary_role:
        raise exceptions.PhoneVerificationException()


def _check_phone_number_is_legit(user: users_models.User, phone_number: str, country_code: str) -> None:
    if phone_number in settings.BLACKLISTED_SMS_RECIPIENTS:
        fraud_api.handle_blacklisted_sms_recipient(user, phone_number)
        raise exceptions.InvalidPhoneNumber()

    if country_code not in constants.WHITELISTED_COUNTRY_PHONE_CODES:
        fraud_api.handle_invalid_country_code(user, phone_number)
        raise exceptions.InvalidCountryCode()


def _check_sms_sending_is_allowed(user: users_models.User) -> None:
    if not sending_limit.is_SMS_sending_allowed(app.redis_client, user):  # type: ignore [attr-defined]
        fraud_api.handle_sms_sending_limit_reached(user)
        raise exceptions.SMSSendingLimitReached()


def _check_phone_number_not_used(user: users_models.User, phone_number: str) -> None:
    if db.session.query(
        users_models.User.query.filter(
            users_models.User.phoneNumber == phone_number, users_models.User.is_phone_validated
        ).exists()
    ).scalar():
        fraud_api.handle_phone_already_exists(user, phone_number)
        raise exceptions.PhoneAlreadyExists(phone_number)


def _check_and_update_phone_validation_attempts(redis: Redis, user: users_models.User) -> None:
    code_validation_attempts = sending_limit.get_code_validation_attempts(redis, user)

    if code_validation_attempts.remaining == 0:
        raise exceptions.PhoneValidationAttemptsLimitReached(code_validation_attempts.attempts)

    phone_validation_attempts_key = f"phone_validation_attempts_user_{user.id}"
    count = redis.incr(phone_validation_attempts_key)
    if count == 1:
        redis.expire(phone_validation_attempts_key, settings.PHONE_VALIDATION_ATTEMPTS_TTL)


def send_phone_validation_code(user: users_models.User, phone_number: str) -> None:
    phone_data = phone_number_utils.ParsedPhoneNumber(phone_number)

    _check_phone_number_validation_is_authorized(user)
    _check_phone_number_is_legit(user, phone_data.phone_number, phone_data.country_code)
    _check_sms_sending_is_allowed(user)
    _check_phone_number_not_used(user, phone_data.phone_number)

    # delete previous token so that the user does not validate with another phone number
    users_models.Token.query.filter(
        users_models.Token.user == user, users_models.Token.type == users_models.TokenType.PHONE_VALIDATION
    ).delete()
    user.phoneNumber = phone_number
    repository.save(user)

    phone_validation_token = users_api.create_phone_validation_token(user)
    content = f"{phone_validation_token.value} est ton code de confirmation pass Culture"  # type: ignore [union-attr]

    is_sms_sent = sms_notifications.send_transactional_sms(phone_data.phone_number, content)

    if not is_sms_sent:
        raise exceptions.PhoneVerificationException()

    sending_limit.update_sent_SMS_counter(app.redis_client, user)  # type: ignore [attr-defined]


def validate_phone_number(user: users_models.User, code: str) -> None:
    if not user.phoneNumber:
        raise exceptions.InvalidPhoneNumber()

    phone_data = phone_number_utils.ParsedPhoneNumber(user.phoneNumber)

    _check_phone_number_validation_is_authorized(user)
    _check_phone_number_is_legit(user, phone_data.phone_number, phone_data.country_code)
    _check_phone_number_not_used(user, phone_data.phone_number)
    _check_and_update_phone_validation_attempts(app.redis_client, user)  # type: ignore [attr-defined]

    token = users_models.Token.query.filter(
        users_models.Token.user == user,
        users_models.Token.value == code,
        users_models.Token.type == users_models.TokenType.PHONE_VALIDATION,
    ).one_or_none()

    if not token:
        code_validation_attempts = sending_limit.get_code_validation_attempts(app.redis_client, user)  # type: ignore [attr-defined]
        if code_validation_attempts.remaining == 0:
            fraud_api.handle_phone_validation_attempts_limit_reached(user, code_validation_attempts.attempts)
        raise exceptions.NotValidCode(remaining_attempts=code_validation_attempts.remaining)

    if token.expirationDate and token.expirationDate < datetime.datetime.utcnow():
        raise exceptions.ExpiredCode()

    db.session.delete(token)

    user.phoneValidationStatus = users_models.PhoneValidationStatusType.VALIDATED  # type: ignore [assignment]
    repository.save(user)

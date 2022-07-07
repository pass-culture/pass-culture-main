import datetime
import logging

from flask import current_app as app
from redis import Redis
from sqlalchemy.orm import exc as sqla_exc

from pcapi import settings
from pcapi.core.fraud import api as fraud_api
from pcapi.core.fraud import models as fraud_models
from pcapi.core.fraud.phone_validation import sending_limit
from pcapi.core.users import api as users_api
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.notifications import sms as sms_notifications
from pcapi.repository import repository
from pcapi.utils import phone_number as phone_number_utils

from . import constants
from . import exceptions


logger = logging.getLogger(__name__)


def _check_phone_number_validation_is_authorized(user: users_models.User) -> None:
    if user.is_phone_validated:
        raise exceptions.UserPhoneNumberAlreadyValidated

    if not user.isEmailValidated:
        raise exceptions.UnvalidatedEmail

    if user.has_beneficiary_role:
        raise exceptions.UserAlreadyBeneficiary


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


def _ensure_phone_number_unicity(
    user_validating_phone: users_models.User, phone_number: str, change_owner: bool = False
) -> None:
    """
    We allow a user to validate a number on an account A
    and then validate the same number on another account B.
    If the account A is already beneficiary, we raise an error.
    Once the account B validates the same number (flag change_owner=True),
    we remove the validated phone on account A and we create "SUSPICIOUS" fraud_checks to keep a track of this action:
    - a fraud_check with reasonCode PHONE_UNVALIDATED_BY_PEER on account A: the phone was unvalidated by account B
    - a fraud_check with reasonCode PHONE_UNVALIDATED_FOR_PEER on account B: the phone was unvalidated for account A
    """
    try:
        user_with_same_validated_number = users_models.User.query.filter(
            users_models.User.phoneNumber == phone_number, users_models.User.is_phone_validated
        ).one_or_none()
    except sqla_exc.MultipleResultsFound:
        logger.exception("Multiple users with the same validated phone number", extra={"phone_number": phone_number})
        raise exceptions.PhoneAlreadyExists()

    if not user_with_same_validated_number:
        return

    if user_with_same_validated_number.has_beneficiary_role:
        fraud_api.handle_phone_already_exists(user_validating_phone, phone_number)
        raise exceptions.PhoneAlreadyExists()

    if not change_owner:
        return

    user_with_same_validated_number.phoneValidationStatus = users_models.PhoneValidationStatusType.UNVALIDATED

    unvalidated_by_peer_check = fraud_models.BeneficiaryFraudCheck(
        user=user_with_same_validated_number,
        type=fraud_models.FraudCheckType.PHONE_VALIDATION,
        reasonCodes=[fraud_models.FraudReasonCode.PHONE_UNVALIDATED_BY_PEER],  # type: ignore [list-item]
        reason=f"Phone number {phone_number} was unvalidated by user {user_validating_phone.id}",
        status=fraud_models.FraudCheckStatus.SUSPICIOUS,
        thirdPartyId=f"PC-{user_with_same_validated_number.id}",
    )

    unvalidated_for_peer_check = fraud_models.BeneficiaryFraudCheck(
        user=user_validating_phone,
        type=fraud_models.FraudCheckType.PHONE_VALIDATION,
        reasonCodes=[fraud_models.FraudReasonCode.PHONE_UNVALIDATION_FOR_PEER],  # type: ignore [list-item]
        reason=f"The phone number validation had the following side effect: phone number {phone_number} was unvalidated for user {user_with_same_validated_number.id}",
        status=fraud_models.FraudCheckStatus.SUSPICIOUS,
        thirdPartyId=f"PC-{user_validating_phone.id}",
    )

    repository.save(unvalidated_by_peer_check, unvalidated_for_peer_check)


def _check_and_update_phone_validation_attempts(redis: Redis, user: users_models.User) -> None:
    code_validation_attempts = sending_limit.get_code_validation_attempts(redis, user)

    if code_validation_attempts.remaining == 0:
        raise exceptions.PhoneValidationAttemptsLimitReached(code_validation_attempts.attempts)

    phone_validation_attempts_key = f"phone_validation_attempts_user_{user.id}"
    count = redis.incr(phone_validation_attempts_key)
    if count == 1:
        redis.expire(phone_validation_attempts_key, settings.PHONE_VALIDATION_ATTEMPTS_TTL)


def send_phone_validation_code(
    user: users_models.User,
    phone_number: str | None,
    expiration: datetime.datetime | None = None,
    ignore_limit: bool = False,
) -> None:
    if not phone_number:
        raise ValueError("phone number is empty")

    phone_data = phone_number_utils.ParsedPhoneNumber(phone_number)

    _check_phone_number_validation_is_authorized(user)
    _check_phone_number_is_legit(user, phone_data.phone_number, phone_data.country_code)
    if not ignore_limit:
        _check_sms_sending_is_allowed(user)
    _ensure_phone_number_unicity(user, phone_data.phone_number, change_owner=False)

    user.phoneNumber = phone_number
    repository.save(user)

    phone_validation_token = users_api.create_phone_validation_token(user, phone_number, expiration=expiration)
    content = f"{phone_validation_token.value} est ton code de confirmation pass Culture"  # type: ignore [union-attr]

    is_sms_sent = sms_notifications.send_transactional_sms(phone_data.phone_number, content)

    if not is_sms_sent:
        raise exceptions.PhoneVerificationException()

    sending_limit.update_sent_SMS_counter(app.redis_client, user)  # type: ignore [attr-defined]


def validate_phone_number(user: users_models.User, code: str) -> None:
    _check_phone_number_validation_is_authorized(user)
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

    if token.get_extra_data():
        phone_number = token.get_extra_data().phone_number
    else:
        # TODO(viconnex): raise here in next release
        phone_number = user.phoneNumber

    db.session.delete(token)

    _ensure_phone_number_unicity(user, phone_number, change_owner=True)

    user.phoneNumber = phone_number
    user.phoneValidationStatus = users_models.PhoneValidationStatusType.VALIDATED
    repository.save(user)

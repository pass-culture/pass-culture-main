import logging
import re
import time

from flask import current_app as app
from redis import Redis
from sqlalchemy.orm import exc as sa_exc

from pcapi import settings
from pcapi.core import token as token_utils
from pcapi.core.subscription import fraud_check_api as fraud_api
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription import schemas as subscription_schemas
from pcapi.core.subscription.phone_validation import sending_limit
from pcapi.core.users import exceptions as users_exceptions
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.notifications import sms as sms_notifications
from pcapi.utils import phone_number as phone_number_utils
from pcapi.utils import requests
from pcapi.utils.transaction_manager import is_managed_transaction

from . import constants
from . import exceptions


logger = logging.getLogger(__name__)

PHONE_VALIDATION_TEST_EMAIL_RE = re.compile(r"^.+\+e2e@.+$")


def _check_phone_number_validation_is_authorized(user: users_models.User) -> None:
    if user.is_phone_validated:
        raise exceptions.UserPhoneNumberAlreadyValidated

    if not user.isEmailValidated:
        raise exceptions.UnvalidatedEmail

    if user.has_beneficiary_role:
        raise exceptions.UserAlreadyBeneficiary


def check_phone_number_is_legit(user: users_models.User, phone_number: str, country_code: int | None) -> None:
    if phone_number in settings.BLACKLISTED_SMS_RECIPIENTS:
        fraud_api.handle_blacklisted_sms_recipient(user, phone_number)
        raise exceptions.InvalidPhoneNumber()

    if country_code not in constants.WHITELISTED_COUNTRY_PHONE_CODES:
        fraud_api.handle_invalid_country_code(user, phone_number)
        raise exceptions.InvalidCountryCode()


def _check_sms_sending_is_allowed(user: users_models.User) -> None:
    if not sending_limit.is_SMS_sending_allowed(app.redis_client, user):
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
        user_with_same_validated_number = (
            db.session.query(
                users_models.User,
            )
            .filter(
                users_models.User.phoneNumber == phone_number,
                users_models.User.is_phone_validated,
            )
            .one_or_none()
        )
    except sa_exc.MultipleResultsFound:
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

    unvalidated_by_peer_check = subscription_models.BeneficiaryFraudCheck(
        user=user_with_same_validated_number,
        type=subscription_models.FraudCheckType.PHONE_VALIDATION,
        reasonCodes=[subscription_models.FraudReasonCode.PHONE_UNVALIDATED_BY_PEER],
        reason=f"Phone number {phone_number} was unvalidated by user {user_validating_phone.id}",
        status=subscription_models.FraudCheckStatus.SUSPICIOUS,
        eligibilityType=user_with_same_validated_number.eligibility,
        thirdPartyId=f"PC-{user_with_same_validated_number.id}",
    )

    unvalidated_for_peer_check = subscription_models.BeneficiaryFraudCheck(
        user=user_validating_phone,
        type=subscription_models.FraudCheckType.PHONE_VALIDATION,
        reasonCodes=[subscription_models.FraudReasonCode.PHONE_UNVALIDATION_FOR_PEER],
        reason=f"The phone number validation had the following side effect: phone number {phone_number} was unvalidated for user {user_with_same_validated_number.id}",
        status=subscription_models.FraudCheckStatus.SUSPICIOUS,
        eligibilityType=user_validating_phone.eligibility,
        thirdPartyId=f"PC-{user_validating_phone.id}",
    )

    db.session.add(unvalidated_by_peer_check)
    db.session.add(unvalidated_for_peer_check)
    if is_managed_transaction():
        db.session.flush()
    else:
        db.session.commit()


def _check_and_update_phone_validation_attempts(redis: Redis, user: users_models.User) -> None:
    code_validation_attempts = sending_limit.get_code_validation_attempts(redis, user)

    if code_validation_attempts.remaining == 0:
        raise exceptions.PhoneValidationAttemptsLimitReached(code_validation_attempts.attempts)

    phone_validation_attempts_key = f"phone_validation_attempts_user_{user.id}"
    count = redis.incr(phone_validation_attempts_key)
    if count == 1:
        redis.expire(phone_validation_attempts_key, settings.PHONE_VALIDATION_ATTEMPTS_TTL)


def _send_sms_with_retry(phone_number: str, message: str, max_attempt: int = 3) -> None:
    base_backoff = 1
    for i_retry in range(max_attempt):
        try:
            sms_notifications.send_transactional_sms(phone_number, message)
            return
        except requests.ExternalAPIException as exception:
            if exception.is_retryable:
                if i_retry < max_attempt - 1:
                    time.sleep(base_backoff * i_retry)
                    continue
                logger.exception("Max retry reached to send SMS", extra={"phone_number": phone_number})
            raise exceptions.PhoneVerificationException()


def send_phone_validation_code(
    user: users_models.User,
    phone_number: str | None,
    ignore_limit: bool = False,
) -> None:
    from pcapi.core.users import api as users_api

    if not phone_number:
        raise ValueError("phone number is empty")

    phone_data = phone_number_utils.ParsedPhoneNumber(phone_number)

    _check_phone_number_validation_is_authorized(user)
    check_phone_number_is_legit(user, phone_data.phone_number, phone_data.country_code)
    if not ignore_limit:
        _check_sms_sending_is_allowed(user)
    _ensure_phone_number_unicity(user, phone_data.phone_number, change_owner=False)

    user.phoneNumber = phone_data.phone_number
    db.session.add(user)
    if is_managed_transaction():
        db.session.flush()
    else:
        db.session.commit()

    phone_validation_token = users_api.create_phone_validation_token(
        user,
        phone_data.phone_number,
    )
    content = f"{phone_validation_token.encoded_token} est ton code de confirmation pass Culture"

    _send_sms_with_retry(phone_data.phone_number, content)

    sending_limit.update_sent_SMS_counter(app.redis_client, user)


def validate_phone_number(user: users_models.User, code: str) -> None:
    _check_phone_number_validation_is_authorized(user)
    _check_and_update_phone_validation_attempts(app.redis_client, user)

    try:
        if settings.DISABLE_PHONE_VALIDATION_FOR_E2E_TESTS and PHONE_VALIDATION_TEST_EMAIL_RE.match(user.email):
            token = token_utils.SixDigitsToken.load_without_checking(
                code, token_utils.TokenType.PHONE_VALIDATION, user.id
            )
        else:
            token = token_utils.SixDigitsToken.load_and_check(code, token_utils.TokenType.PHONE_VALIDATION, user.id)
    except users_exceptions.InvalidToken:
        code_validation_attempts = sending_limit.get_code_validation_attempts(app.redis_client, user)
        raise exceptions.NotValidCode(
            remaining_attempts=code_validation_attempts.remaining, attempts=code_validation_attempts.attempts
        )
    try:
        phone_number = token.data["phone_number"]
    except KeyError:
        logger.exception("Phone number not found in token", extra={"token_type": token.type_, "user_id": user.id})
        raise exceptions.PhoneNumberNotFoundInToken()
    token.expire()

    _ensure_phone_number_unicity(user, phone_number, change_owner=True)

    user.phoneNumber = phone_number
    user.phoneValidationStatus = users_models.PhoneValidationStatusType.VALIDATED

    fraud_check = subscription_models.BeneficiaryFraudCheck(
        user=user,
        type=subscription_models.FraudCheckType.PHONE_VALIDATION,
        status=subscription_models.FraudCheckStatus.OK,
        eligibilityType=user.eligibility,
        resultContent=subscription_schemas.PhoneValidationFraudData(phone_number=phone_number).dict(exclude_none=True),
        thirdPartyId=f"PC-{user.id}",
    )
    db.session.add(fraud_check)
    db.session.flush()

from datetime import datetime
from datetime import timedelta
import enum
import logging

from flask import current_app as app
import jwt
import sqlalchemy as sqla

from pcapi import settings
from pcapi.core import token as token_utils
from pcapi.core.mails import transactional as transactional_mails
from pcapi.core.token import Token
from pcapi.core.users import api
from pcapi.core.users import constants
from pcapi.core.users import exceptions
from pcapi.core.users import models
from pcapi.core.users import repository as users_repository
from pcapi.core.users import utils
from pcapi.models import db
from pcapi.models.api_errors import ApiErrors
from pcapi.repository import repository
from pcapi.repository import transaction
from pcapi.routes.native.v1.serialization.account import ChangeEmailTokenContent
from pcapi.utils.urls import generate_firebase_dynamic_link

from .send import send_pro_user_emails_for_email_change


logger = logging.getLogger(__name__)


class EmailChangeAction(enum.Enum):
    CONFIRMATION = "changement-email/confirmation"
    CANCELLATION = "suspension-compte/confirmation"
    VALIDATION = "changement-email/validation"


class TokenType(enum.Enum):
    CONFIRMATION = "confirmation"
    VALIDATION = "validation"


def _build_link_for_email_change_action(
    action: EmailChangeAction, new_email: str, expiration_date: datetime, token: str
) -> str:
    expiration = int(expiration_date.timestamp())
    path = action.value
    params = {
        "token": token,
        "expiration_timestamp": expiration,
        "new_email": new_email,
    }

    return generate_firebase_dynamic_link(path, params)


def generate_and_send_beneficiary_confirmation_email_for_email_change(user: models.User, new_email: str) -> bool:
    """Generate a Token
    Generate a link with the token
    Send an email with the link"""

    expiration_date = generate_email_change_token_expiration_date()

    encoded_token = Token.create(
        token_utils.TokenType.EMAIL_CHANGE_CONFIRMATION,
        constants.EMAIL_CHANGE_TOKEN_LIFE_TIME,
        user.id,
        {"new_email": new_email},
    ).encoded_token
    check_email_address_does_not_exist(new_email)

    link_for_email_change_confirmation = _build_link_for_email_change_action(
        EmailChangeAction.CONFIRMATION,
        new_email,
        expiration_date,
        token=encoded_token,
    )
    link_for_email_change_cancellation = _build_link_for_email_change_action(
        EmailChangeAction.CANCELLATION,
        new_email,
        expiration_date,
        token=encoded_token,
    )
    return transactional_mails.send_confirmation_email_change_email(
        user,
        link_for_email_change_confirmation,
        link_for_email_change_cancellation,
    )


def generate_and_send_beneficiary_validation_email_for_email_change(user: models.User, new_email: str) -> bool:
    expiration_date = generate_email_change_token_expiration_date()
    token = generate_email_change_token(user, new_email, expiration_date, TokenType.VALIDATION)

    link_for_email_change_validation = _build_link_for_email_change_action(
        EmailChangeAction.VALIDATION,
        new_email,
        expiration_date,
        token=token,
    )

    return transactional_mails.send_validation_email_change_email(
        user,
        new_email,
        link_for_email_change_validation,
    )


def request_email_update(user: models.User, new_email: str, password: str) -> None:
    check_no_ongoing_email_update_request(user)
    check_email_update_attempts_count(user)
    check_user_password(user, password)

    email_history = models.UserEmailHistory.build_update_request(user=user, new_email=new_email)
    repository.save(email_history)
    increment_email_update_attempts_count(user)
    generate_and_send_beneficiary_confirmation_email_for_email_change(user, new_email)


def _check_token(user: models.User, token_to_check: str, token_type: TokenType) -> None:
    token_key = get_token_key(user, token_type)
    if app.redis_client.get(token_key) != token_to_check:  # type: ignore [attr-defined]
        raise exceptions.InvalidToken()


def _expire_token(user: models.User, token_type: TokenType) -> None:
    token_key = get_token_key(user, token_type)
    app.redis_client.delete(token_key)  # type: ignore [attr-defined]


def confirm_email_update_request(encoded_token: str) -> None:
    """Confirm the email update request for the given user"""
    try:
        jwt_payload = utils.decode_jwt_token(encoded_token)
    except jwt.PyJWTError:
        raise exceptions.InvalidToken()
    new_token_type = "token_type" in jwt_payload
    if new_token_type:  # nouveau type de tokens celui de pcapi.core.token
        token = Token.load_without_checking(encoded_token)
        user = models.User.query.get(token.user_id)
        new_email = token.data["new_email"]
    else:  # old token type. should be removed when old token type is removed
        payload = ChangeEmailTokenContent.from_token(encoded_token)
        current_email = payload.current_email
        new_email = payload.new_email
        user = users_repository.find_user_by_email(current_email)
    if not user:
        raise exceptions.InvalidEmailError()
    if new_token_type:
        token.check(token_utils.TokenType.EMAIL_CHANGE_CONFIRMATION)
    else:  # should be removed when old token type is removed
        _check_token(user, encoded_token, TokenType.CONFIRMATION)
    check_email_address_does_not_exist(new_email)
    try:
        generate_and_send_beneficiary_validation_email_for_email_change(user, new_email)
        with transaction():
            models.UserEmailHistory.build_confirmation(user, new_email)
        if new_token_type:
            token.expire()
        else:  # should be removed when old token type is removed
            _expire_token(user, TokenType.CONFIRMATION)

    except Exception as error:
        raise ApiErrors(
            errors={"message": f"erreur inattendue: {error}"},
        )


def cancel_email_update_request(encoded_token: str) -> None:
    """Cancel the email update request for the given user"""

    try:
        jwt_payload = utils.decode_jwt_token(encoded_token)
    except jwt.PyJWTError:
        raise exceptions.InvalidToken()
    new_token_type = "token_type" in jwt_payload
    if new_token_type:  # nouveau type de tokens celui de pcapi.core.token
        token = Token.load_without_checking(encoded_token)
        user = models.User.query.get(token.user_id)
        new_email = token.data["new_email"]
    else:  # old token type. should be removed when old token type is removed
        payload = ChangeEmailTokenContent.from_token(encoded_token)
        current_email = payload.current_email
        new_email = payload.new_email
        user = users_repository.find_user_by_email(current_email)
    if not user:
        raise exceptions.InvalidEmailError()
    if new_token_type:
        token.check(token_utils.TokenType.EMAIL_CHANGE_CONFIRMATION)
    else:  # should be removed when old token type is removed
        _check_token(user, encoded_token, TokenType.CONFIRMATION)
    api.suspend_account(
        user, constants.SuspensionReason.FRAUD_SUSPICION, user, "Suspension suite à un changement d'email annulé"
    )
    transactional_mails.send_email_update_cancellation_email(user)
    models.UserEmailHistory.build_cancellation(user, new_email)
    if new_token_type:
        token.expire()
    else:  # should be removed when old token type is removed
        _expire_token(user, TokenType.CONFIRMATION)


def validate_email_update_request(
    token: str,
) -> None:
    """
    Change a user's email and add a new (validation) entry to its email
    history.

    If no user is found, check whether a validated update request
    exists: if so, there is no need to panic nor to redo the update
    since it already has been done.

    Therefore this function can be called multiple times with the same
    inputs safely.
    """
    payload = ChangeEmailTokenContent.from_token(token)
    current_email = payload.current_email
    new_email = payload.new_email
    user = users_repository.find_user_by_email(current_email)
    if not user:
        if not validated_update_request_exists(current_email, new_email):
            raise exceptions.UserDoesNotExist()
        return
    _check_token(user, token, TokenType.VALIDATION)
    check_email_address_does_not_exist(new_email)
    api.change_email(user, new_email)
    transactional_mails.send_email_change_information_email(user)
    _expire_token(user, TokenType.VALIDATION)


def request_email_update_from_pro(user: models.User, email: str, password: str) -> None:
    check_user_password(user, password)
    check_pro_email_update_attempts(user)
    check_email_address_does_not_exist(email)

    expiration_date = generate_email_change_token_expiration_date()

    email_history = models.UserEmailHistory.build_update_request(user=user, new_email=email)
    repository.save(email_history)

    send_pro_user_emails_for_email_change(user, email, expiration_date)


def check_email_update_attempts_count(user: models.User) -> None:
    """Check if the user has reached the maximum number of email update attempts.
    If yes, raise an exception.
    """
    update_email_attempts = app.redis_client.get(f"update_email_attemps_user_{user.id}")  # type: ignore [attr-defined]
    if update_email_attempts and int(update_email_attempts) >= settings.MAX_EMAIL_UPDATE_ATTEMPTS:
        raise exceptions.EmailUpdateLimitReached()


def increment_email_update_attempts_count(user: models.User) -> None:
    """
    increment or intitiate the number of attempts
    """
    update_email_attempts_key = f"update_email_attemps_user_{user.id}"

    result = app.redis_client.incr(update_email_attempts_key)  # type: ignore [attr-defined]
    if result == 1:
        # If the key did not exist, set the expiration time
        app.redis_client.expire(update_email_attempts_key, settings.EMAIL_UPDATE_ATTEMPTS_TTL)  # type: ignore [attr-defined]


def check_pro_email_update_attempts(user: models.User) -> None:
    update_email_attempts_key = f"update_email_attemps_user_{user.id}"
    count = app.redis_client.incr(update_email_attempts_key)  # type: ignore [attr-defined]

    if count == 1:
        app.redis_client.expire(update_email_attempts_key, constants.EMAIL_PRO_UPDATE_ATTEMPTS_TTL)  # type: ignore [attr-defined]

    if count > constants.MAX_EMAIL_UPDATE_ATTEMPTS_FOR_PRO:
        raise exceptions.EmailUpdateLimitReached()


def request_email_update_from_admin(user: models.User, email: str) -> None:
    """
    When email is changed by admin, it is immediately changed in the user profile.
    User can no longer login with his former email, and must confirm new email.
    """
    check_email_address_does_not_exist(email)

    email_history = models.UserEmailHistory.build_update_request(user=user, new_email=email, by_admin=True)

    user.email = email
    user.isEmailValidated = False

    repository.save(email_history, user)

    api.request_email_confirmation(user)


def full_email_update_by_admin(user: models.User, email: str) -> None:
    """
    Runs the whole email update process at once, without sending any
    confirmation email: log update history, update user's email and
    mark it as validated.
    """
    check_email_address_does_not_exist(email)

    admin_update_event = models.UserEmailHistory.build_admin_update(user=user, new_email=email)

    user.email = email
    user.isEmailValidated = True

    repository.save(user, admin_update_event)


def get_token_key(user: models.User, token_type: TokenType) -> str:
    match token_type:
        case TokenType.CONFIRMATION:
            return f"update_email_confirmation_token_{user.id}"
        case TokenType.VALIDATION:
            return f"update_email_validation_token_{user.id}"
        case _:
            raise ValueError(f"Invalid token type: {token_type}")


def generate_email_change_token(
    user: models.User, new_email: str, expiration_date: datetime, token_type: TokenType
) -> str:
    token = utils.encode_jwt_payload({"current_email": user.email, "new_email": new_email}, expiration_date)
    key = get_token_key(user, token_type)
    app.redis_client.set(key, token, ex=constants.EMAIL_CHANGE_TOKEN_LIFE_TIME)  # type: ignore [attr-defined]
    return token


def get_active_token_expiration(user: models.User) -> datetime | None:
    """returns the expiration date of the active token (confirmation or validation) or none if no ttl or no token exists"""
    ttl = app.redis_client.ttl(get_token_key(user, TokenType.CONFIRMATION))  # type: ignore [attr-defined]
    if ttl > 0:
        return datetime.utcnow() + timedelta(seconds=ttl)
    ttl = app.redis_client.ttl(get_token_key(user, TokenType.VALIDATION))  # type: ignore [attr-defined]
    if ttl > 0:
        return datetime.utcnow() + timedelta(seconds=ttl)
    confirmation_token_expiration = Token.get_expiration_date(token_utils.TokenType.EMAIL_CHANGE_CONFIRMATION, user.id)
    validation_token_expiration = Token.get_expiration_date(token_utils.TokenType.EMAIL_CHANGE_VALIDATION, user.id)
    return confirmation_token_expiration or validation_token_expiration


def generate_email_change_token_expiration_date() -> datetime:
    return datetime.utcnow() + constants.EMAIL_CHANGE_TOKEN_LIFE_TIME


def check_user_password(user: models.User, password: str) -> None:
    try:
        users_repository.check_user_and_credentials(user, password)
    except exceptions.InvalidIdentifier as exc:
        raise exceptions.EmailUpdateInvalidPassword() from exc
    except exceptions.UnvalidatedAccount as exc:
        # This should not happen. But, if it did:
        # 1. log the error
        # 2. raise the same error as above, so the end client
        # can't guess what happened.
        logger.error("Unvalidated account tried to change their email", extra={"user": user.id})
        raise exceptions.EmailUpdateInvalidPassword() from exc


def check_email_address_does_not_exist(email: str) -> None:
    if users_repository.find_user_by_email(email):
        raise exceptions.EmailExistsError(email)


def check_no_ongoing_email_update_request(user: models.User) -> None:
    """Raise error if user has an ongoing email update request"""
    if (
        Token.token_exists(token_utils.TokenType.EMAIL_CHANGE_CONFIRMATION, user.id)
        or Token.token_exists(token_utils.TokenType.EMAIL_CHANGE_VALIDATION, user.id)
        or app.redis_client.exists(f"update_email_confirmation_token_{user.id}")  # type: ignore [attr-defined]  #FIXME : remove this after the old tokens disappear https://passculture.atlassian.net/browse/PC-23343
        or app.redis_client.exists(f"update_email_validation_token_{user.id}")  # type: ignore [attr-defined]  #FIXME : remove this after the old tokens disappear https://passculture.atlassian.net/browse/PC-23343
    ):
        raise exceptions.EmailUpdateTokenExists()


def validated_update_request_exists(old_email: str, new_email: str) -> bool:
    """
    Check if an email update exists and has been validated (by the user
    or by an admin).
    """
    return db.session.query(
        models.UserEmailHistory.query.filter(
            models.UserEmailHistory.oldEmail == old_email, models.UserEmailHistory.newEmail == new_email
        )
        .filter(
            sqla.or_(
                models.UserEmailHistory.eventType == models.EmailHistoryEventTypeEnum.VALIDATION,
                models.UserEmailHistory.eventType == models.EmailHistoryEventTypeEnum.ADMIN_VALIDATION,
            )
        )
        .exists()
    ).scalar()

from datetime import datetime
from datetime import timedelta
import enum
import logging

from flask import current_app as app
import sqlalchemy as sqla

from pcapi import settings
from pcapi.core.mails import transactional as transactional_mails
from pcapi.core.users import api
from pcapi.core.users import constants
from pcapi.core.users import exceptions
from pcapi.core.users import models
from pcapi.core.users import repository as users_repository
from pcapi.core.users.utils import encode_jwt_payload
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

    token = generate_email_change_confirmation_token(user, new_email, expiration_date)
    link_for_email_change_confirmation = _build_link_for_email_change_action(
        EmailChangeAction.CONFIRMATION,
        new_email,
        expiration_date,
        token=token,
    )
    link_for_email_change_cancellation = _build_link_for_email_change_action(
        EmailChangeAction.CANCELLATION,
        new_email,
        expiration_date,
        token=token,
    )
    success = transactional_mails.send_confirmation_email_change_email(
        user,
        link_for_email_change_confirmation,
        link_for_email_change_cancellation,
    )

    return success


def generate_and_send_beneficiary_validation_email_for_email_change(user: models.User, new_email: str) -> bool:
    expiration_date = generate_email_change_token_expiration_date()
    token = generate_email_change_validation_token(user, new_email, expiration_date)

    link_for_email_change_validation = _build_link_for_email_change_action(
        EmailChangeAction.VALIDATION,
        new_email,
        expiration_date,
        token=token,
    )

    success = transactional_mails.send_validation_email_change_email(
        user,
        new_email,
        link_for_email_change_validation,
    )

    return success


def request_email_update(user: models.User, new_email: str, password: str) -> None:
    check_user_password(user, password)
    check_and_increment_email_update_attempts_count(user)
    check_email_address_does_not_exist(new_email)
    check_no_ongoing_email_update_request(user)

    # TODO: manage the atomicity and the errors
    email_history = models.UserEmailHistory.build_update_request(user=user, new_email=new_email)
    repository.save(email_history)
    generate_and_send_beneficiary_confirmation_email_for_email_change(user, new_email)


def confirm_email_update_request(token: str) -> None:
    """Confirm the email update request for the given user"""

    payload = ChangeEmailTokenContent.from_token(token)
    current_email = payload.current_email
    new_email = payload.new_email
    user = users_repository.find_user_by_email(current_email)
    if not user:
        raise exceptions.InvalidEmailError()
    check_email_address_does_not_exist(new_email)
    check_and_desactivate_confirmation_token(user, token)
    try:
        with transaction():
            models.UserEmailHistory.build_confirmation(user, new_email)
            generate_and_send_beneficiary_validation_email_for_email_change(user, new_email)

    except Exception as error:
        raise ApiErrors(
            errors={"message": f"erreur inattendue: {error}"},
        )


def request_email_update_from_pro(user: models.User, email: str, password: str) -> None:
    check_user_password(user, password)
    check_pro_email_update_attempts(user)
    check_email_address_does_not_exist(email)

    expiration_date = generate_email_change_token_expiration_date()

    email_history = models.UserEmailHistory.build_update_request(user=user, new_email=email)
    repository.save(email_history)

    send_pro_user_emails_for_email_change(user, email, expiration_date)


def check_and_increment_email_update_attempts_count(user: models.User) -> None:
    """Check if the user has reached the maximum number of email update attempts.
    If yes, raise an exception.
    The number of attempts is *always* incremented, even if the limit is reached.
    """
    update_email_attempts_key = f"update_email_attemps_user_{user.id}"
    count = app.redis_client.incr(update_email_attempts_key)  # type: ignore [attr-defined]

    if count == 1:
        app.redis_client.expire(update_email_attempts_key, settings.EMAIL_UPDATE_ATTEMPTS_TTL)  # type: ignore [attr-defined]

    if count > settings.MAX_EMAIL_UPDATE_ATTEMPTS:
        raise exceptions.EmailUpdateLimitReached()


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


def get_confirmation_token_key(user: models.User) -> str:
    return f"update_email_confirmation_token_{user.id}"


def get_validation_token_key(user: models.User) -> str:
    return f"update_email_validation_token_{user.id}"


def confirmation_token_exists(user: models.User) -> bool:
    """Check if there is an active confirmation token for the user"""
    key = get_confirmation_token_key(user)
    return app.redis_client.exists(key)  # type: ignore [attr-defined]


def validation_token_exists(user: models.User) -> bool:
    """Check if there is an active validation token for the user"""
    key = get_validation_token_key(user)
    return app.redis_client.exists(key)  # type: ignore [attr-defined]


def generate_email_change_confirmation_token(user: models.User, new_email: str, expiration_date: datetime) -> str:
    token = encode_jwt_payload({"current_email": user.email, "new_email": new_email}, expiration_date)
    app.redis_client.set(get_confirmation_token_key(user), token, exat=expiration_date)  # type: ignore [attr-defined]
    return token


def generate_email_change_validation_token(user: models.User, new_email: str, expiration_date: datetime) -> str:
    token = encode_jwt_payload({"current_email": user.email, "new_email": new_email}, expiration_date)
    app.redis_client.set(get_validation_token_key(user), token, exat=expiration_date)  # type: ignore [attr-defined]
    return token


def check_and_desactivate_confirmation_token(user: models.User, token: str) -> None:
    token_key = get_confirmation_token_key(user)
    assert app.redis_client  # helps mypy
    if app.redis_client.get(token_key) != token:
        raise exceptions.InvalidToken()
    app.redis_client.delete(token_key)



def check_and_desactivate_validation_token(user: models.User, token: str) -> None:
    token_key = get_validation_token_key(user)
    if app.redis_client.get(token_key) == token:  # type: ignore [attr-defined]
        app.redis_client.delete(token_key)  # type: ignore [attr-defined]
    else:
        raise exceptions.InvalidToken()


def check_no_active_token_exists(
    user: models.User, expiration_date: datetime
) -> None:  # TODO Do not use this function replace it with create token and
    """
    Use a dummy counter to find out whether the user already has an
    active token.

    * If the incr command returns 1, there were none. Hence, set a TTL
      (expiration_date, the lifetime of the validation token).
    * If not, raise an error because there is already one.
    """
    key = get_confirmation_token_key(user)
    count = app.redis_client.incr(key)  # type: ignore [attr-defined]

    if count > 1:
        raise exceptions.EmailUpdateTokenExists()

    app.redis_client.expireat(key, expiration_date)  # type: ignore [attr-defined]


def get_active_token_expiration(user: models.User) -> datetime | None:
    confirmation_key = get_confirmation_token_key(user)
    validation_key = get_validation_token_key(user)
    ttl = max(app.redis_client.ttl(confirmation_key), app.redis_client.ttl(validation_key))  # type: ignore [attr-defined]
    if ttl < 0:
        return None
    return datetime.utcnow() + timedelta(seconds=ttl)


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
    if confirmation_token_exists(user) or validation_token_exists(user):
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

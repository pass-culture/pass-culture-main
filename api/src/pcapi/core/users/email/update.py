from datetime import datetime
from datetime import timedelta
import logging
import typing

from flask import current_app as app

from pcapi import settings
from pcapi.core.users import constants
from pcapi.core.users import exceptions
from pcapi.core.users import repository as users_repository
from pcapi.core.users.api import find_user_by_email
from pcapi.core.users.models import User
from pcapi.core.users.models import UserEmailHistory
from pcapi.repository import repository

from .send import send_user_emails_for_email_change


logger = logging.getLogger(__name__)


def request_email_update(user: User, email: str, password: str) -> None:
    check_email_update_attempts(user)

    expiration_date = generate_token_expiration_date()
    check_no_active_token_exists(user, expiration_date)

    check_email_address_does_not_exist(email)
    check_user_password(user, password)

    email_history = UserEmailHistory.build_update_request(user=user, new_email=email)
    repository.save(email_history)

    send_user_emails_for_email_change(user, email, expiration_date)


def check_email_update_attempts(user: User) -> None:
    update_email_attempts_key = f"update_email_attemps_user_{user.id}"
    count = app.redis_client.incr(update_email_attempts_key)

    if count == 1:
        app.redis_client.expire(update_email_attempts_key, settings.EMAIL_UPDATE_ATTEMPTS_TTL)

    if count > settings.MAX_EMAIL_UPDATE_ATTEMPTS:
        raise exceptions.EmailUpdateLimitReached()


def get_no_active_token_key(user: User) -> str:
    return f"update_email_active_tokens_{user.id}"


def check_no_active_token_exists(user: User, expiration_date: datetime) -> None:
    """
    Use a dummy counter to find out whether the user already has an
    active token.

    * If the incr command returns 1, there were none. Hence, set a TTL
      (expiration_date, the lifetime of the validation token).
    * If not, raise an error because there is already one.
    """
    key = get_no_active_token_key(user)
    count = app.redis_client.incr(key)

    if count > 1:
        raise exceptions.EmailUpdateTokenExists()

    app.redis_client.expireat(key, expiration_date)


def get_active_token_expiration(user) -> typing.Optional[datetime]:
    key = get_no_active_token_key(user)
    ttl = app.redis_client.ttl(key)

    if ttl < 0:
        return None

    return datetime.utcnow() + timedelta(seconds=ttl)


def generate_token_expiration_date() -> datetime:
    return datetime.utcnow() + constants.EMAIL_CHANGE_TOKEN_LIFE_TIME


def check_user_password(user: User, password: str) -> None:
    try:
        users_repository.check_user_and_credentials(user, password)
    except exceptions.InvalidIdentifier as exc:
        raise exceptions.EmailUpdateInvalidPassword() from exc
    except exceptions.UnvalidatedAccount as exc:
        # This should not happen. But, if it did:
        # 1. log the error
        # 2. raise the same error as above, so the end client
        # can't guess what happened.
        logger.error("Unvalidated account tried to change their e-mail", extra={"user": user.id})
        raise exceptions.EmailUpdateInvalidPassword() from exc


def check_email_address_does_not_exist(email: str) -> None:
    if find_user_by_email(email):
        raise exceptions.EmailExistsError(email)

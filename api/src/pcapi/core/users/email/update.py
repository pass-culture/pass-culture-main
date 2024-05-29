from datetime import datetime
import enum
import logging

from flask import current_app as app

from pcapi import settings
from pcapi.core import token as token_utils
import pcapi.core.external.sendinblue as external_contacts
from pcapi.core.mails import transactional as transactional_mails
from pcapi.core.users import api
from pcapi.core.users import constants
from pcapi.core.users import exceptions
from pcapi.core.users import models
from pcapi.core.users import repository as users_repository
from pcapi.core.users.email.send import send_pro_user_emails_for_email_change
from pcapi.models import db
from pcapi.models.api_errors import ApiErrors
from pcapi.repository import repository
from pcapi.repository import transaction
from pcapi.utils.urls import generate_firebase_dynamic_link


logger = logging.getLogger(__name__)


class EmailChangeAction(enum.Enum):
    CONFIRMATION = "changement-email/confirmation"
    CANCELLATION = "suspension-compte/confirmation"
    VALIDATION = "changement-email/validation"


def _build_link_for_email_change_action(
    action: EmailChangeAction, new_email: str | None, expiration_date: datetime, token: str
) -> str:
    expiration = int(expiration_date.timestamp())
    path = action.value
    params = {
        "token": token,
        "expiration_timestamp": expiration,
    }
    if new_email:
        params["new_email"] = new_email

    return generate_firebase_dynamic_link(path, params)


def send_confirmation_email_for_email_change(user: models.User) -> None:
    """Generate a Token
    Generate a link with the token
    Send an email with the link"""

    expiration_date = generate_email_change_token_expiration_date()
    encoded_token = token_utils.Token.create(
        token_utils.TokenType.EMAIL_CHANGE_CONFIRMATION,
        constants.EMAIL_CHANGE_TOKEN_LIFE_TIME,
        user.id,
    ).encoded_token

    link_for_email_change_confirmation = _build_link_for_email_change_action(
        EmailChangeAction.CONFIRMATION,
        new_email=None,
        expiration_date=expiration_date,
        token=encoded_token,
    )
    link_for_email_change_cancellation = _build_link_for_email_change_action(
        EmailChangeAction.CANCELLATION,
        new_email=None,
        expiration_date=expiration_date,
        token=encoded_token,
    )
    transactional_mails.send_confirmation_email_change_email(
        user,
        link_for_email_change_confirmation,
        link_for_email_change_cancellation,
    )


def generate_and_send_beneficiary_confirmation_email_for_email_change(user: models.User, new_email: str) -> None:
    """Generate a Token
    Generate a link with the token
    Send an email with the link"""

    expiration_date = generate_email_change_token_expiration_date()

    encoded_token = token_utils.Token.create(
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
    transactional_mails.send_confirmation_email_change_email(
        user,
        link_for_email_change_confirmation,
        link_for_email_change_cancellation,
    )


def generate_and_send_beneficiary_validation_email_for_email_change(user: models.User, new_email: str) -> None:
    expiration_date = generate_email_change_token_expiration_date()
    encoded_token = token_utils.Token.create(
        token_utils.TokenType.EMAIL_CHANGE_VALIDATION,
        constants.EMAIL_CHANGE_TOKEN_LIFE_TIME,
        user_id=user.id,
        data={"new_email": new_email},
    ).encoded_token

    link_for_email_change_validation = _build_link_for_email_change_action(
        EmailChangeAction.VALIDATION,
        new_email,
        expiration_date,
        token=encoded_token,
    )

    transactional_mails.send_validation_email_change_email(
        user,
        new_email,
        link_for_email_change_validation,
    )


def request_email_update(user: models.User) -> None:
    check_no_ongoing_email_update_request(user)
    check_email_update_attempts_count(user)

    email_history = models.UserEmailHistory.build_update_request(user=user)
    db.session.add(email_history)

    increment_email_update_attempts_count(user)
    send_confirmation_email_for_email_change(user)


def request_email_update_with_credentials(user: models.User, new_email: str, password: str) -> None:
    check_no_ongoing_email_update_request(user)
    check_email_update_attempts_count(user)
    check_user_password(user, password)

    email_history = models.UserEmailHistory.build_update_request(user=user, new_email=new_email)
    repository.save(email_history)
    increment_email_update_attempts_count(user)
    generate_and_send_beneficiary_confirmation_email_for_email_change(user, new_email)


def confirm_email_update_request_and_send_mail(encoded_token: str) -> None:
    """Confirm the email update request for the given user"""
    token = token_utils.Token.load_and_check(encoded_token, token_utils.TokenType.EMAIL_CHANGE_CONFIRMATION)
    user = models.User.query.filter_by(id=token.user_id).one_or_none()
    if not user:
        raise exceptions.InvalidToken()
    new_email = token.data["new_email"]
    check_email_address_does_not_exist(new_email)
    try:
        generate_and_send_beneficiary_validation_email_for_email_change(user, new_email)
        with transaction():
            models.UserEmailHistory.build_confirmation(user, new_email)
        token.expire()

    except Exception as error:
        raise ApiErrors(
            errors={"message": f"erreur inattendue: {error}"},
        )


def confirm_new_email_selection_and_send_mail(user: models.User, encoded_new_mail_token: str, new_email: str) -> None:
    new_mail_token = token_utils.Token.load_and_check(
        encoded_new_mail_token, token_utils.TokenType.EMAIL_CHANGE_NEW_EMAIL_SELECTION
    )
    if user.id != new_mail_token.user_id:
        raise exceptions.InvalidToken()

    check_email_address_does_not_exist(new_email)
    generate_and_send_beneficiary_validation_email_for_email_change(user, new_email)

    email_history = models.UserEmailHistory.build_new_email_selection(user, new_email)
    db.session.add(email_history)

    new_mail_token.expire()


def confirm_email_update_request(encoded_token: str) -> models.User:
    """Confirm the email update request for the given user"""
    token = token_utils.Token.load_and_check(encoded_token, token_utils.TokenType.EMAIL_CHANGE_CONFIRMATION)
    user = models.User.query.filter_by(id=token.user_id).one_or_none()
    if not user:
        raise exceptions.InvalidToken()

    email_history = models.UserEmailHistory.build_confirmation(user)
    db.session.add(email_history)
    token.expire()

    return user


def cancel_email_update_request(encoded_token: str) -> None:
    """Cancel the email update request for the given user"""

    token = token_utils.Token.load_and_check(encoded_token, token_utils.TokenType.EMAIL_CHANGE_CONFIRMATION)
    user = models.User.query.filter_by(id=token.user_id).one_or_none()
    if not user:
        raise exceptions.InvalidToken()
    new_email = token.data.get("new_email")
    api.suspend_account(
        user, constants.SuspensionReason.FRAUD_SUSPICION, user, "Suspension suite à un changement d'email annulé"
    )
    transactional_mails.send_email_update_cancellation_email(user)
    models.UserEmailHistory.build_cancellation(user, new_email)
    token.expire()


def validate_email_update_request(
    encoded_email_validation_token: str,
) -> models.User:
    """
    Change a user's email and add a new (validation) entry to its email
    history.

    If no user is found, check whether a validated update request
    exists: if so, there is no need to panic nor to redo the update
    since it already has been done.

    Therefore this function can be called multiple times with the same
    inputs safely.
    """
    email_update_validation_token = token_utils.Token.load_without_checking(encoded_email_validation_token)
    user = models.User.query.filter_by(id=email_update_validation_token.user_id).one_or_none()
    if not user:
        raise exceptions.UserDoesNotExist()

    old_email = user.email
    new_email = email_update_validation_token.data["new_email"]
    if old_email == new_email:
        return user

    email_update_validation_token.check(token_utils.TokenType.EMAIL_CHANGE_VALIDATION)

    check_email_address_does_not_exist(new_email)
    api.change_email(user, new_email)

    external_contacts.update_contact_email(user=user, old_email=old_email, new_email=new_email)
    transactional_mails.send_email_change_information_email(user)

    email_update_validation_token.expire()
    recent_password_reset_token = token_utils.Token.get_token(token_utils.TokenType.RECENTLY_RESET_PASSWORD, user.id)
    if recent_password_reset_token:
        recent_password_reset_token.expire()

    return models.User.query.filter_by(id=user.id).one()


def request_email_update_from_pro(user: models.User, email: str, password: str) -> None:
    check_user_password(user, password)
    check_pro_email_update_attempts(user)
    check_email_address_does_not_exist(email)

    token = token_utils.Token.create(
        token_utils.TokenType.EMAIL_CHANGE_VALIDATION,
        ttl=constants.EMAIL_CHANGE_TOKEN_LIFE_TIME,
        user_id=user.id,
        data={"current_email": user.email, "new_email": email},
    )

    email_history = models.UserEmailHistory.build_update_request(user=user, new_email=email)
    repository.save(email_history)

    send_pro_user_emails_for_email_change(user, email, token)


def check_email_update_attempts_count(user: models.User) -> None:
    """Check if the user has reached the maximum number of email update attempts.
    If yes, raise an exception.
    """
    update_email_attempts = app.redis_client.get(f"update_email_attemps_user_{user.id}")
    if update_email_attempts and int(update_email_attempts) >= settings.MAX_EMAIL_UPDATE_ATTEMPTS:
        raise exceptions.EmailUpdateLimitReached()


def increment_email_update_attempts_count(user: models.User) -> None:
    """
    increment or intitiate the number of attempts
    """
    update_email_attempts_key = f"update_email_attemps_user_{user.id}"

    result = app.redis_client.incr(update_email_attempts_key)
    if result == 1:
        # If the key did not exist, set the expiration time
        app.redis_client.expire(update_email_attempts_key, settings.EMAIL_UPDATE_ATTEMPTS_TTL)


def check_pro_email_update_attempts(user: models.User) -> None:
    update_email_attempts_key = f"update_email_attemps_user_{user.id}"
    count = app.redis_client.incr(update_email_attempts_key)

    if count == 1:
        app.redis_client.expire(update_email_attempts_key, constants.EMAIL_PRO_UPDATE_ATTEMPTS_TTL)

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


def full_email_update_by_admin(user: models.User, email: str, commit: bool = False) -> None:
    """
    Runs the whole email update process at once, without sending any
    confirmation email: log update history, update user's email and
    mark it as validated.
    """
    check_email_address_does_not_exist(email)

    admin_update_event = models.UserEmailHistory.build_admin_update(user=user, new_email=email)
    db.session.add(admin_update_event)

    user.email = email
    user.isEmailValidated = True
    db.session.add(user)

    if commit:
        db.session.commit()


def get_active_token_expiration(user: models.User) -> datetime | None:
    """returns the expiration date of the active token (confirmation or validation) or none if no ttl or no token exists"""
    confirmation_token_expiration = token_utils.Token.get_expiration_date(
        token_utils.TokenType.EMAIL_CHANGE_CONFIRMATION, user.id
    )
    new_email_selection_token_expiration = token_utils.Token.get_expiration_date(
        token_utils.TokenType.EMAIL_CHANGE_NEW_EMAIL_SELECTION, user.id
    )
    validation_token_expiration = token_utils.Token.get_expiration_date(
        token_utils.TokenType.EMAIL_CHANGE_VALIDATION, user.id
    )
    return confirmation_token_expiration or new_email_selection_token_expiration or validation_token_expiration


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
    if token_utils.Token.token_exists(
        token_utils.TokenType.EMAIL_CHANGE_CONFIRMATION, user.id
    ) or token_utils.Token.token_exists(token_utils.TokenType.EMAIL_CHANGE_VALIDATION, user.id):
        raise exceptions.EmailUpdateTokenExists()

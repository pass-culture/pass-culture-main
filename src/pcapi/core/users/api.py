from datetime import date
from datetime import datetime
from datetime import timedelta
import secrets
from typing import Optional

from pcapi.core.users import exceptions
from pcapi.core.users.models import Token
from pcapi.core.users.models import TokenType
from pcapi.core.users.utils import create_custom_jwt_token
from pcapi.core.users.utils import format_email
from pcapi.domain import user_emails
from pcapi.domain.password import generate_reset_token
from pcapi.domain.password import random_password
from pcapi.models.deposit import DEPOSIT_DEFAULT_AMOUNT
from pcapi.models.deposit import Deposit
from pcapi.models.user_session import UserSession
from pcapi.models.user_sql_entity import UserSQLEntity
from pcapi.repository import repository
from pcapi.repository.user_queries import find_user_by_email
from pcapi.scripts.beneficiary import THIRTY_DAYS_IN_HOURS
from pcapi.utils import mailing as mailing_utils
from pcapi.utils.logger import logger

from . import constants


def create_email_validation_token(user: UserSQLEntity) -> Token:
    return generate_and_save_token(
        user, TokenType.EMAIL_VALIDATION, life_time=constants.EMAIL_VALIDATION_TOKEN_LIFE_TIME
    )


def create_reset_password_token(user: UserSQLEntity) -> Token:
    return generate_and_save_token(user, TokenType.RESET_PASSWORD, life_time=constants.RESET_PASSWORD_TOKEN_LIFE_TIME)


def create_id_check_token(user: UserSQLEntity) -> Optional[Token]:
    if not is_user_eligible(user):
        return None

    return generate_and_save_token(user, TokenType.ID_CHECK, constants.ID_CHECK_TOKEN_LIFE_TIME)


def generate_and_save_token(user: UserSQLEntity, token_type: TokenType, life_time: Optional[timedelta] = None) -> Token:
    expiration_date = datetime.now() + life_time if life_time else None
    token_value = create_custom_jwt_token(user.id, token_type.value, expiration_date)

    token_with_same_value = Token.query.filter_by(value=token_value).first()
    if token_with_same_value:
        return token_with_same_value

    token = Token(userId=user.id, value=token_value, type=token_type, expirationDate=expiration_date)
    repository.save(token)

    return token


def create_account(
    email: str,
    password: str,
    brithdate: date,
    has_allowed_recommendations: bool = False,
    is_email_validated: bool = False,
    send_activation_mail: bool = True,
) -> UserSQLEntity:
    if find_user_by_email(email):
        raise exceptions.UserAlreadyExistsException()

    user = UserSQLEntity(
        email=format_email(email),
        dateOfBirth=brithdate,
        isEmailValidated=is_email_validated,
        departementCode="007",
        publicName="   ",  # Required because model validation requires 3+ chars
        hasSeenTutorials=False,
        firstName="",
        hasAllowedRecommendations=has_allowed_recommendations,
    )
    user.setPassword(password)
    repository.save(user)

    if not is_email_validated and send_activation_mail:
        request_email_confirmation(user)
    return user


def request_email_confirmation(user: UserSQLEntity) -> None:
    token = create_email_validation_token(user)
    user_emails.send_activation_email(user, mailing_utils.send_raw_email, native_version=True, token=token)


def is_user_eligible(user: UserSQLEntity) -> bool:
    age = user.calculate_age()
    return age is not None and age == constants.ELIGIBILITY_AGE


def fulfill_user_data(user: UserSQLEntity, deposit_source: str) -> UserSQLEntity:
    user.password = random_password()
    generate_reset_token(user, validity_duration_hours=THIRTY_DAYS_IN_HOURS)

    deposit = Deposit()
    deposit.amount = DEPOSIT_DEFAULT_AMOUNT
    deposit.source = deposit_source
    user.deposits = [deposit]

    return user


def suspend_account(user: UserSQLEntity, reason: constants.SuspensionReason, actor: UserSQLEntity):
    user.isActive = False
    user.suspensionReason = str(reason)
    # If we ever unsuspend the account, we'll have to explictly enable
    # isAdmin again. An admin now may not be an admin later.
    user.isAdmin = False
    # FIXME (before merge): est-ce qu'il y a un intérêt à modifier le
    # mot de passe ? De toute façon, l'utilisateur ne pourra pas se
    # logger puisque `isActive=False`.
    user.setPassword(secrets.token_urlsafe(30))
    repository.save(user)

    sessions = UserSession.query.filter_by(userId=user.id)
    repository.delete(*sessions)

    logger.info("user=%s has been suspended by actor=%s for reason=%s", user.id, actor.id, reason)


def unsuspend_account(user: UserSQLEntity, actor: UserSQLEntity):
    user.isActive = True
    user.suspensionReason = ""
    repository.save(user)

    logger.info("user=%s has been unsuspended by actor=%s", user.id, actor.id)

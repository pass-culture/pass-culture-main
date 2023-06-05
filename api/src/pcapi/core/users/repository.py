from datetime import date
from datetime import datetime
import logging
import typing

from dateutil.relativedelta import relativedelta
from flask_sqlalchemy import BaseQuery
import sqlalchemy as sa
from sqlalchemy.sql.functions import func

import pcapi.core.offerers.models as offerers_models
from pcapi.repository import repository
from pcapi.utils import crypto
import pcapi.utils.email as email_utils

from . import constants
from . import exceptions
from . import models


logger = logging.getLogger(__name__)


HASHED_PLACEHOLDER = crypto.hash_password("placeholder")


def check_user_and_credentials(user: models.User | None, password: str, allow_inactive: bool = False) -> None:
    # Order is important to prevent end-user to guess user emails
    # We need to check email and password before checking email validation
    if not user:
        # Hash the given password, just like we would do if the user
        # existed. This avoids user enumeration by comparing server
        # response time.
        crypto.check_password(password, HASHED_PLACEHOLDER)
        raise exceptions.InvalidIdentifier()
    if not (user.checkPassword(password) and (user.isActive or allow_inactive)):
        logger.info(
            "Failed authentication attempt",
            extra={"identifier": user.email, "user": user.id, "avoid_current_user": True, "success": False},
            technical_message_id="users.login",
        )
        raise exceptions.InvalidIdentifier()
    if not user.isValidated or not user.isEmailValidated:
        raise exceptions.UnvalidatedAccount()


def get_user_with_credentials(identifier: str, password: str, allow_inactive: bool = False) -> models.User:
    user = find_user_by_email(identifier)
    if not user:
        logger.info(
            "Failed authentication attempt",
            extra={"identifier": identifier, "user": "not found", "avoid_current_user": True, "success": False},
            technical_message_id="users.login",
        )
    check_user_and_credentials(user, password, allow_inactive)
    if user:
        logger.info(
            "Successful authentication attempt",
            extra={"identifier": identifier, "user": user.id, "avoid_current_user": True, "success": True},
            technical_message_id="users.login",
        )
    return typing.cast(models.User, user)


def _find_user_by_email_query(email: str) -> BaseQuery:
    # FIXME (dbaty, 2021-05-02): remove call to `func.lower()` once
    # all emails have been sanitized in the database.
    return models.User.query.filter(func.lower(models.User.email) == email_utils.sanitize_email(email))


def find_user_by_email(email: str) -> models.User | None:
    return _find_user_by_email_query(email).one_or_none()


def find_pro_user_by_email_query(email: str) -> BaseQuery:
    return _find_user_by_email_query(email).filter(models.User.has_pro_role.is_(True))  # type: ignore [attr-defined]


def get_user_with_valid_token(
    token_value: str, token_types: list[models.TokenType], use_token: bool = True
) -> models.User:
    token = models.Token.query.filter(
        models.Token.value == token_value,
        models.Token.type.in_(token_types),
        sa.not_(models.Token.isUsed),
    ).one_or_none()

    if not token:
        raise exceptions.InvalidToken()

    if token.expirationDate and token.expirationDate < datetime.utcnow():
        raise exceptions.ExpiredToken(user=token.user)

    if use_token:
        token.isUsed = True
        repository.save(token)

    return token.user


def get_newly_eligible_age_18_users(since: date) -> list[models.User]:
    """get users that are eligible between `since` (excluded) and now (included) and that have
    created their account before `since`"""
    today = datetime.combine(datetime.today(), datetime.min.time())
    since = datetime.combine(since, datetime.min.time())
    eligible_users = (
        models.User.query.outerjoin(offerers_models.UserOfferer)
        .filter(
            sa.not_(models.User.has_beneficiary_role),  # not already beneficiary
            sa.not_(models.User.has_admin_role),  # not an admin
            offerers_models.UserOfferer.userId.is_(None),  # not a pro
            # less than 19yo
            models.User.birth_date > today - relativedelta(years=(constants.ELIGIBILITY_AGE_18 + 1)),  # type: ignore [operator]
            # more than or 18yo
            models.User.birth_date <= today - relativedelta(years=constants.ELIGIBILITY_AGE_18),  # type: ignore [operator]
            # less than 18yo at since
            models.User.birth_date > since - relativedelta(years=constants.ELIGIBILITY_AGE_18),  # type: ignore [operator]
            models.User.dateCreated < today,
        )
        .all()
    )
    return eligible_users


def get_users_with_validated_attachment_by_offerer(offerer: offerers_models.Offerer) -> list[models.User]:
    return (
        models.User.query.join(offerers_models.UserOfferer)
        .filter(
            offerers_models.UserOfferer.isValidated,
            offerers_models.UserOfferer.offererId == offerer.id,
        )
        .all()
    )


def get_users_with_validated_attachment(offerer: offerers_models.Offerer) -> list[models.User]:
    return (
        models.User.query.join(offerers_models.UserOfferer)
        .filter_by(offererId=offerer.id, isValidated=True)
        .order_by(offerers_models.UserOfferer.id)
        .all()
    )


def get_and_lock_user(userId: int) -> models.User:
    user = models.User.query.filter(models.User.id == userId).populate_existing().with_for_update().one_or_none()
    return user

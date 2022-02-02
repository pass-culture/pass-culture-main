from datetime import date
from datetime import datetime
import logging
from typing import Optional

from dateutil.relativedelta import relativedelta
from sqlalchemy.sql.functions import func

from pcapi.core.offerers.models import Offerer
from pcapi.core.users.utils import sanitize_email
from pcapi.models.user_offerer import UserOfferer
from pcapi.repository import repository
from pcapi.utils import crypto

from . import constants
from . import exceptions
from . import models
from .models import User


logger = logging.getLogger(__name__)


HASHED_PLACEHOLDER = crypto.hash_password("placeholder")


def check_user_and_credentials(user: User, password: str) -> None:
    # Order is important to prevent end-user to guess user emails
    # We need to check email and password before checking email validation
    if not user:
        # Hash the given password, just like we would do if the user
        # existed. This avoids user enumeration by comparing server
        # response time.
        crypto.check_password(password, HASHED_PLACEHOLDER)
        raise exceptions.InvalidIdentifier()
    if not user.checkPassword(password) or not user.isActive:
        logging.info("Failed authentication attempt", extra={"user": user.id, "avoid_current_user": True})
        raise exceptions.InvalidIdentifier()
    if not user.isValidated or not user.isEmailValidated:
        raise exceptions.UnvalidatedAccount()


def get_user_with_credentials(identifier: str, password: str) -> User:
    user = find_user_by_email(identifier)
    check_user_and_credentials(user, password)
    return user


def _find_user_by_email_query(email: str):
    # FIXME (dbaty, 2021-05-02): remove call to `func.lower()` once
    # all emails have been sanitized in the database.
    return User.query.filter(func.lower(User.email) == sanitize_email(email))


def find_user_by_email(email: str) -> Optional[User]:
    return _find_user_by_email_query(email).one_or_none()


def find_pro_user_by_email(email: str) -> Optional[User]:
    return _find_user_by_email_query(email).filter(User.has_pro_role.is_(True)).one_or_none()


def get_user_with_valid_token(
    token_value: str, token_types: list[models.TokenType], use_token: bool = True
) -> Optional[User]:
    token = models.Token.query.filter(
        models.Token.value == token_value, models.Token.type.in_(token_types), models.Token.isUsed == False
    ).one_or_none()
    if not token:
        return None

    if token.expirationDate and token.expirationDate < datetime.now():
        return None

    if use_token:
        token.isUsed = True
        repository.save(token)

    return token.user


def get_newly_eligible_age_18_users(since: date) -> list[User]:
    """get users that are eligible between `since` (excluded) and now (included) and that have
    created their account before `since`"""
    today = datetime.combine(datetime.today(), datetime.min.time())
    since = datetime.combine(since, datetime.min.time())
    eligible_users = (
        User.query.outerjoin(UserOfferer)
        .filter(
            User.has_beneficiary_role == False,  # not already beneficiary
            User.has_admin_role == False,  # not an admin
            UserOfferer.userId.is_(None),  # not a pro
            User.dateOfBirth > today - relativedelta(years=(constants.ELIGIBILITY_AGE_18 + 1)),  # less than 19yo
            User.dateOfBirth <= today - relativedelta(years=constants.ELIGIBILITY_AGE_18),  # more than or 18yo
            User.dateOfBirth > since - relativedelta(years=constants.ELIGIBILITY_AGE_18),  # less than 18yo at since
            User.dateCreated < today,
        )
        .all()
    )
    return eligible_users


def get_favorites_for_offers(offer_ids: list[int]) -> list[models.Favorite]:
    return models.Favorite.query.filter(models.Favorite.offerId.in_(offer_ids)).all()


def does_validated_phone_exist(phone_number: str) -> bool:
    return bool(User.query.filter(User.phoneNumber == phone_number, User.is_phone_validated).count())


def get_users_with_validated_attachment_by_offerer(offerer: Offerer) -> User:
    return (
        User.query.join(UserOfferer)
        .filter(UserOfferer.validationToken.is_(None), UserOfferer.offererId == offerer.id)
        .all()
    )

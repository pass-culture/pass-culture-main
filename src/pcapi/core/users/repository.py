from datetime import date
from datetime import datetime
from typing import List
from typing import Optional

from dateutil.relativedelta import relativedelta

from pcapi.models import UserOfferer
from pcapi.repository.user_queries import find_user_by_email

from . import constants
from . import exceptions
from . import models
from .models import User


def check_user_and_credentials(user: User, password: str) -> None:
    # Order is important to prevent end-user to guess user emails
    # We need to check email and password before checking email validation
    if not user or not user.isActive or not user.checkPassword(password):
        raise exceptions.InvalidIdentifier()
    if not user.isValidated or not user.isEmailValidated:
        raise exceptions.UnvalidatedAccount()


def get_user_with_credentials(identifier: str, password: str) -> User:
    user = find_user_by_email(identifier)
    check_user_and_credentials(user, password)
    return user


def get_user_with_valid_token(token_value: str, token_types: List[models.TokenType]) -> Optional[User]:
    token = models.Token.query.filter(models.Token.value == token_value, models.Token.type.in_(token_types)).first()
    if not token:
        return None

    if token.expirationDate and token.expirationDate < datetime.now():
        return None

    return token.user


def get_id_check_token(token_value: str) -> models.Token:
    return models.Token.query.filter(
        models.Token.value == token_value, models.Token.type == models.TokenType.ID_CHECK
    ).first()


def get_newly_eligible_users(since: date) -> List[User]:
    """get users that are eligible between `since` (excluded) and now (included) and that have
    created their account before `since`"""
    today = datetime.combine(datetime.today(), datetime.min.time())
    since = datetime.combine(since, datetime.min.time())
    return (
        User.query.outerjoin(UserOfferer)
        .filter(
            User.isBeneficiary == False,  # not already beneficiary
            User.isAdmin == False,  # not an admin
            UserOfferer.userId.is_(None),  # not a pro
            User.dateOfBirth > today - relativedelta(years=(constants.ELIGIBILITY_AGE + 1)),  # less than 19yo
            User.dateOfBirth <= today - relativedelta(years=constants.ELIGIBILITY_AGE),  # more than or 18yo
            User.dateOfBirth > since - relativedelta(years=constants.ELIGIBILITY_AGE),  # less than 18yo at since
            User.dateCreated < since,
        )
        .all()
    )

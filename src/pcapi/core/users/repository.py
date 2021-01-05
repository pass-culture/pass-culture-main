from datetime import datetime
from typing import List
from typing import Optional

from pcapi.repository.user_queries import find_user_by_email

from . import exceptions
from . import models
from .models import UserSQLEntity


def _check_user_and_credentials(user: UserSQLEntity, password: str) -> None:
    if not user:
        raise exceptions.InvalidIdentifier()
    if not user.isActive:
        raise exceptions.InvalidIdentifier()
    if not user.isValidated or not user.isEmailValidated:
        raise exceptions.UnvalidatedAccount()
    if not user.checkPassword(password):
        raise exceptions.InvalidPassword()


def get_user_with_credentials(identifier: str, password: str) -> UserSQLEntity:
    user = find_user_by_email(identifier)
    _check_user_and_credentials(user, password)
    return user


def get_user_with_valid_token(token_value: str, token_types: List[models.TokenType]) -> Optional[UserSQLEntity]:
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

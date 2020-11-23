from datetime import datetime
from typing import List
from typing import Optional

from pcapi.core.users.models import Token
from pcapi.core.users.models import TokenType
from pcapi.models.user_sql_entity import UserSQLEntity
from pcapi.repository.user_queries import find_user_by_email

from . import exceptions


def get_user_with_credentials(identifier: str, password: str) -> UserSQLEntity:
    user = find_user_by_email(identifier)
    if not user:
        raise exceptions.InvalidIdentifier()
    if not user.isValidated:
        raise exceptions.UnvalidatedAccount()
    if not user.checkPassword(password):
        raise exceptions.InvalidPassword()
    return user


def get_user_with_valid_token(token_value: str, token_types: List[TokenType]) -> Optional[UserSQLEntity]:
    token: Optional[Token] = Token.query.filter(Token.value == token_value, Token.type.in_(token_types)).first()
    if not token:
        return None

    if token.expirationDate and token.expirationDate < datetime.now():
        return None

    return token.user

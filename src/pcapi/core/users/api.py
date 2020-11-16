from datetime import datetime
from datetime import timedelta
from typing import List
from typing import Optional

from pcapi.core.users.models import Token
from pcapi.core.users.models import TokenType
from pcapi.core.users.utils import create_custom_jwt_token
from pcapi.models.user_sql_entity import UserSQLEntity
from pcapi.repository import repository
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


def generate_and_save_token(user: UserSQLEntity, token_type: TokenType, life_time: Optional[timedelta] = None) -> Token:
    expiration_date = datetime.now() + life_time if life_time else None
    token_value = create_custom_jwt_token(user.id, token_type.value, expiration_date)

    token_with_same_value = Token.query.filter_by(value=token_value).first()
    if token_with_same_value:
        return token_with_same_value

    token = Token(
        from_dict={"userId": user.id, "value": token_value, "type": token_type, "expirationDate": expiration_date}
    )
    repository.save(token)

    return token


def get_user_with_valid_token(token_value: str, token_types: List[TokenType]) -> Optional[UserSQLEntity]:
    token: Optional[Token] = Token.query.filter(Token.value == token_value, Token.type.in_(token_types)).first()
    if not token:
        return None

    if token.expirationDate and token.expirationDate < datetime.now():
        return None

    return token.user

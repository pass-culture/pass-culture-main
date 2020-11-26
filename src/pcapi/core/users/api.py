from datetime import datetime
from datetime import timedelta
from typing import Optional

from pcapi.core.users.models import Token
from pcapi.core.users.models import TokenType
from pcapi.core.users.utils import create_custom_jwt_token
from pcapi.models.user_sql_entity import UserSQLEntity
from pcapi.repository import repository

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

    token = Token(
        from_dict={"userId": user.id, "value": token_value, "type": token_type, "expirationDate": expiration_date}
    )
    repository.save(token)

    return token


def is_user_eligible(user: UserSQLEntity) -> bool:
    age = user.calculate_age()
    return age is not None and age == constants.ELIGIBILITY_AGE

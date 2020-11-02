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

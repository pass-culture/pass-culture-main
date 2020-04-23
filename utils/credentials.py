""" credentials """
from flask import session

from models.api_errors import ApiErrors
from models.db import auto_close_db_transaction
from models.user_sql_entity import UserSQLEntity
from repository import repository
from repository.user_queries import find_user_by_email


def get_user_with_credentials(identifier: str, password: str) -> UserSQLEntity:

    with auto_close_db_transaction():
        user = find_user_by_email(identifier)

    errors = ApiErrors()
    errors.status_code = 401

    if not user:
        errors.add_error('identifier', 'Identifiant incorrect')
        raise errors
    if not user.isValidated:
        errors.add_error('identifier', "Ce compte n'est pas validé.")
        raise errors
    if not user.checkPassword(password):
        errors.add_error('password', 'Mot de passe incorrect')
        raise errors

    return user


def change_password(user, password):
    if type(user) != UserSQLEntity:
        user = UserSQLEntity.query.filter_by(email=user).one()
    user.setPassword(password)
    user = session.merge(user)
    repository.save(user)

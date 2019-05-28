""" credentials """
from flask import session

from models.api_errors import ApiErrors
from models.pc_object import PcObject
from models.user import User
from repository.user_queries import find_user_by_email


def get_user_with_credentials(identifier: str, password: str) -> User:
    user = find_user_by_email(identifier)

    errors = ApiErrors()
    errors.status_code = 401

    if not user:
        errors.addError('identifier', 'Identifiant incorrect')
        raise errors
    if not user.isValidated:
        errors.addError('identifier', "Ce compte n'est pas validé.")
        raise errors
    if not user.checkPassword(password):
        errors.addError('password', 'Mot de passe incorrect')
        raise errors

    return user


def change_password(user, password):
    if type(user) != User:
        user = User.query.filter_by(email=user).one()
    user.setPassword(password)
    user = session.merge(user)
    PcObject.save(user)

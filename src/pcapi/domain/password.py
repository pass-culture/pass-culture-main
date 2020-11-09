from datetime import datetime
from datetime import timedelta
import re
from typing import Dict

from pcapi.models import ApiErrors
from pcapi.models import UserSQLEntity
from pcapi.models.user_sql_entity import hash_password
from pcapi.utils.token import random_token


RESET_PASSWORD_TOKEN_LENGTH = 10


def random_password() -> bytes:
    return hash_password(random_token(length=12))


def check_password_validity(new_password: str, new_confirmation_password: str, old_password: str, user: UserSQLEntity) -> None:
    api_errors = ApiErrors()
    _ensure_new_password_is_strong_enough('newPassword', new_password, api_errors)
    _ensure_given_old_password_is_correct(user, old_password, api_errors)
    _ensure_new_password_is_different_from_old(user, new_password, api_errors)
    _ensure_confirmation_password_is_same_as_new_password(new_password, new_confirmation_password, api_errors)
    if len(api_errors.errors) > 0:
        raise api_errors


def validate_change_password_request(json: Dict) -> None:
    api_errors = ApiErrors()
    if 'oldPassword' not in json or not json['oldPassword']:
        api_errors.add_error('oldPassword', 'Ancien mot de passe manquant')

    if 'newPassword' not in json or not json['newPassword']:
        api_errors.add_error('newPassword', 'Nouveau mot de passe manquant')

    if 'newConfirmationPassword' not in json or not json['newConfirmationPassword']:
        api_errors.add_error('newConfirmationPassword', 'Confirmation du nouveau mot de passe manquante')

    if len(api_errors.errors) > 0:
        raise api_errors


def generate_reset_token(user, validity_duration_hours=24):
    token = random_token(length=RESET_PASSWORD_TOKEN_LENGTH)
    user.resetPasswordToken = token
    user.resetPasswordTokenValidityLimit = datetime.utcnow() + timedelta(hours=validity_duration_hours)


def validate_reset_request(request):
    if 'email' not in request.get_json():
        errors = ApiErrors()
        errors.add_error('email', 'L\'email est manquant')
        raise errors

    if not request.get_json()['email']:
        errors = ApiErrors()
        errors.add_error('email', 'L\'email renseigné est vide')
        raise errors


def validate_new_password_request(request):
    if 'token' not in request.get_json():
        errors = ApiErrors()
        errors.add_error('token', 'Votre lien de changement de mot de passe est invalide.')
        raise errors

    if 'newPassword' not in request.get_json():
        errors = ApiErrors()
        errors.add_error('newPassword', 'Vous devez renseigner un nouveau mot de passe.')
        raise errors


def check_reset_token_validity(user):
    if datetime.utcnow() > user.resetPasswordTokenValidityLimit:
        errors = ApiErrors()
        errors.add_error('token',
                         'Votre lien de changement de mot de passe est périmé. Veuillez effectuer une nouvelle demande.')
        raise errors


def check_password_strength(key: str, password: str) -> None:
    api_errors = ApiErrors()
    _ensure_new_password_is_strong_enough(key, password, api_errors)
    if len(api_errors.errors) > 0:
        raise api_errors


def _ensure_new_password_is_different_from_old(user: UserSQLEntity, new_password: str, errors: ApiErrors) -> None:
    if user.checkPassword(new_password):
        errors.add_error('newPassword', 'Ton nouveau mot de passe est identique à l’ancien.')


def _ensure_given_old_password_is_correct(user: UserSQLEntity, old_password: str, errors: ApiErrors) -> None:
    if not user.checkPassword(old_password):
        errors.add_error('oldPassword', 'Ton ancien mot de passe est incorrect.')


def _ensure_new_password_is_strong_enough(field_name: str, field_value: str, errors: ApiErrors) -> None:
    at_least_one_uppercase = '(?=.*?[A-Z])'
    at_least_one_lowercase = '(?=.*?[a-z])'
    at_least_one_digit = '(?=.*?[0-9])'
    min_length = '.{12,}'
    at_least_one_special_char = '(?=.*?[#~|=;:,+><?!@$%^&*_.-])'

    regex = '^' \
            + at_least_one_uppercase \
            + at_least_one_lowercase \
            + at_least_one_digit \
            + at_least_one_special_char \
            + min_length \
            + '$'

    if not re.match(regex, field_value):
        errors.add_error(
            field_name,
            'Ton mot de passe doit contenir au moins :\n'
            '- 12 caractères\n'
            '- Un chiffre\n'
            '- Une majuscule et une minuscule\n'
            '- Un caractère spécial'
        )

def _ensure_confirmation_password_is_same_as_new_password(new_password_value: str, new_confirmation_password_value: str, errors: ApiErrors) -> None:
    if(new_password_value != new_confirmation_password_value):
        errors.add_error('newConfirmationPassword', 'Les deux mots de passe ne sont pas identiques.')

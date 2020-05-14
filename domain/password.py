import re
from datetime import datetime, timedelta

import bcrypt

from models import ApiErrors
from utils.token import random_token

RESET_PASSWORD_TOKEN_LENGTH = 10


def random_password():
    return bcrypt.hashpw(random_token(length=12).encode('utf-8'), bcrypt.gensalt())


def check_new_password_validity(user, old_password, new_password):
    errors = ApiErrors()

    if not user.checkPassword(old_password):
        errors.add_error('oldPassword', 'Ton ancien mot de passe est incorrect.')
        raise errors

    if user.checkPassword(new_password):
        errors.add_error('newPassword', 'Ton nouveau mot de passe est identique à l’ancien.')
        raise errors


def validate_change_password_request(json):
    errors = ApiErrors()

    if 'oldPassword' not in json:
        errors.add_error('oldPassword', 'Ancien mot de passe manquant')
        raise errors

    if 'newPassword' not in json:
        errors.add_error('newPassword', 'Nouveau mot de passe manquant')
        raise errors


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


def check_password_strength(field_name, field_value):
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
        errors = ApiErrors()
        errors.add_error(
            field_name,
            'Ton mot de passe doit contenir au moins :\n'
            '- 12 caractères\n'
            '- Un chiffre\n'
            '- Une majuscule et une minuscule\n'
            '- Un caractère spécial'
        )
        raise errors

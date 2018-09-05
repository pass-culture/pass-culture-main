import secrets
import string
from datetime import datetime, timedelta

from models import ApiErrors

RESET_PASSWORD_TOKEN_LENGTH = 10


def change_password(user, old_password, new_password):
    errors = ApiErrors()

    if not user.checkPassword(old_password):
        errors.addError('oldPassword', 'Votre ancien mot de passe est incorrect')
        raise errors

    if user.checkPassword(new_password):
        errors.addError('newPassword', 'Votre nouveau mot de passe est identique à l\'ancien')
        raise errors

    user.setPassword(new_password)


def validate_request(json):
    errors = ApiErrors()

    if 'oldPassword' not in json:
        errors.addError('oldPassword', 'Ancien mot de passe manquant')
        raise errors

    if 'newPassword' not in json:
        errors.addError('newPassword', 'Nouveau mot de passe manquant')
        raise errors


def generate_reset_token(user):
    token = ''.join(_random_alphanum_char() for _ in range(RESET_PASSWORD_TOKEN_LENGTH))
    user.resetPasswordToken = token
    user.resetPasswordTokenValidityLimit = datetime.utcnow() + timedelta(hours=24)


def validate_reset_request(request):
    if 'email' not in request.get_json():
        errors = ApiErrors()
        errors.addError('email', 'L\'email est manquant')
        raise errors

    if not request.get_json()['email']:
        errors = ApiErrors()
        errors.addError('email', 'L\'email renseigné est vide')
        raise errors


def validate_new_password_request(request):
    if 'token' not in request.get_json():
        errors = ApiErrors()
        errors.addError('token', 'Votre lien de changement de mot de passe est invalide.')
        raise errors

    if 'newPassword' not in request.get_json():
        errors = ApiErrors()
        errors.addError('newPassword', 'Vous devez renseigner un nouveau mot de passe.')
        raise errors


def check_reset_token_validity(user):
    if datetime.utcnow() > user.resetPasswordTokenValidityLimit:
        errors = ApiErrors()
        errors.addError('token', 'Votre lien de changement de mot de passe est périmé. Veuillez effecture une nouvelle demande.')
        raise errors


def _random_alphanum_char():
    return secrets.choice(string.ascii_uppercase + string.digits)

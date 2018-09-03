from models import ApiErrors


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
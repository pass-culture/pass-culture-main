from pcapi.models.api_errors import ApiErrors
from pcapi.models.api_errors import ResourceNotFoundError


def check_valid_token_for_user_validation(user_to_validate):
    if user_to_validate is None:
        errors = ResourceNotFoundError()
        errors.add_error(
            'global',
            'Ce lien est invalide'
        )
        raise errors

def check_validation_request(token):
    if token is None:
        error = ApiErrors()
        error.add_error('token', 'Vous devez fournir un jeton de validation')
        raise error


def check_venue_found(venue):
    if venue is None:
        error = ResourceNotFoundError()
        error.add_error('token', 'Jeton inconnu')
        raise error

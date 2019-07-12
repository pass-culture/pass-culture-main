from models.api_errors import ResourceNotFound, ApiErrors


def check_valid_token_for_user_validation(user_to_validate):
    if user_to_validate is None:
        errors = ResourceNotFound()
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
        error = ResourceNotFound()
        error.add_error('token', 'Jeton inconnu')
        raise error

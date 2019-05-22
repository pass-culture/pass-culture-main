from models import ApiErrors
from models.api_errors import ResourceNotFound


def check_validation_request(token):
    if token is None:
        error = ApiErrors()
        error.addError('token', 'Vous devez fournir un jeton de validation')
        raise error


def check_venue_found(venue):
    if venue is None:
        error = ResourceNotFound()
        error.addError('token', 'Jeton inconnu')
        raise error

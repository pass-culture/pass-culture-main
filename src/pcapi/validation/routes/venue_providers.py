from pcapi.models import ApiErrors
from pcapi.models import Provider


def check_existing_provider(provider: Provider):
    if not provider:
        errors = ApiErrors()
        errors.status_code = 400
        errors.add_error("provider", "Cette source n'est pas disponible")
        raise errors

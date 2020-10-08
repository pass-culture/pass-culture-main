import re

from pcapi.models import ApiErrors
from pcapi.models.db import Model


def validate(model: Model, api_errors: ApiErrors) -> ApiErrors:
    if model.postalCode is not None and not re.match(r'^\d[AB0-9]\d{3,4}$', model.postalCode):
        api_errors.add_error('postalCode', 'Ce code postal est invalide')

    return api_errors
